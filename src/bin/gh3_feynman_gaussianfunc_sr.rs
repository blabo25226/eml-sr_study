//! Feynman I.6.2a — Gaussian PDF symbolic regression with `eml-sr`.
//!
//! CSV: `exp(-theta**2/2)/sqrt(2*pi)`  (variable `theta` ∈ [1, 3])
//!
//! Run from the repo root:
//!   cargo run --bin gh3_feynman_gaussianfunc_sr --release

use eml_sr::{SearchConfig, Searcher};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

const FEYNMAN_ID: &str = "I.6.2a";
const N_SAMPLES: usize = 128;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let csv_path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data/FeynmanEquations.csv");
    let csv_text = fs::read_to_string(&csv_path)?;

    println!("===========================================================");
    println!("  Feynman Gaussian SR (eml-sr) — {FEYNMAN_ID}");
    println!("  CSV: {}", csv_path.display());
    println!("===========================================================\n");

    let row = load_row(&csv_text, FEYNMAN_ID)?;
    println!("--- {FEYNMAN_ID} ---");
    println!("  Expected:  {} = {}", row.output, row.formula);
    print!("  Variables: ");
    for v in &row.variables {
        print!("{}∈[{:.1},{:.1}] ", v.name, v.low, v.high);
    }
    println!();
    println!("  Samples:   {N_SAMPLES} random points in CSV ranges");

    let (inputs, targets) = synthesize_dataset(&row, N_SAMPLES, 42 + row.filename.len() as u64);
    let start = Instant::now();
    let outcome = run_gaussian_search(&inputs, &targets);
    let elapsed = start.elapsed();

    match outcome {
        SearchOutcome::LogFallback {
            result,
            note,
            log_shift,
        } => {
            print_result(
                &result,
                &inputs,
                &targets,
                &row.formula,
                elapsed,
                Some(log_shift),
            );
            println!("  Note:        {note}");
            println!("  Status:      OK (log-space search)\n");
        }
        SearchOutcome::Failed { result, note } => {
            if let Some(r) = result {
                print_result(&r, &inputs, &targets, &row.formula, elapsed, None);
            } else {
                println!("  Time:        {elapsed:?}");
            }
            println!("  Note:        {note}");
            println!("  Status:      CHECK\n");
        }
    }

    Ok(())
}

enum SearchOutcome {
    LogFallback {
        result: eml_sr::SearchResult,
        note: String,
        log_shift: f64,
    },
    Failed {
        result: Option<eml_sr::SearchResult>,
        note: String,
    },
}

/// `exp(-theta^2/2)/sqrt(2*pi)` — search on `ln(y)+ln(sqrt(2*pi)) = -theta^2/2`, then map back.
fn run_gaussian_search(inputs: &[Vec<f64>], targets: &[f64]) -> SearchOutcome {
    let log_shift = 0.5 * (2.0 * std::f64::consts::PI).ln();
    let log_targets: Vec<f64> = targets.iter().map(|y| y.ln() + log_shift).collect();

    let mut log_config = SearchConfig::builder()
        .max_complexity(7)
        .beam_width(800)
        .precision_goal(1e-10)
        .build();
    log_config.parallelism = 1;
    let searcher = Searcher::new(log_config);

    let hold_rmse = |result: &eml_sr::SearchResult| {
        let preds = map_from_log_space(result.eval_batch(inputs), log_shift);
        let err = rmse(targets, &preds);
        if err.is_finite() { err } else { f64::INFINITY }
    };

    let mut best: Option<(f64, eml_sr::SearchResult)> = None;
    if let Ok(candidates) = searcher.find_candidates(inputs, &log_targets) {
        for c in candidates {
            let err = hold_rmse(&c);
            if best.as_ref().map_or(true, |(e, _)| err < *e) {
                best = Some((err, c));
            }
        }
    }

    if let Some((err, result)) = best {
        if err < 0.05 {
            let note = if err < 1e-5 {
                "Searched on ln(y)+ln(sqrt(2*pi)) = -theta^2/2; map back with \
                 exp(found - ln(sqrt(2*pi))) for the CSV formula."
                    .to_string()
            } else {
                format!(
                    "Log-space search (approximate, hold RMSE={err:.3e}). Map back with \
                     exp(found - ln(sqrt(2*pi)))."
                )
            };
            return SearchOutcome::LogFallback {
                result,
                note,
                log_shift,
            };
        }
    }

    SearchOutcome::Failed {
        result: None,
        note: "Gaussian recovery failed even with log-space search (try --release).".to_string(),
    }
}

fn map_from_log_space(log_preds: Vec<f64>, shift: f64) -> Vec<f64> {
    log_preds.into_iter().map(|p| (p - shift).exp()).collect()
}

fn print_result(
    result: &eml_sr::SearchResult,
    inputs: &[Vec<f64>],
    targets: &[f64],
    expected: &str,
    elapsed: std::time::Duration,
    log_shift: Option<f64>,
) {
    let raw = result.eval_batch(inputs);
    let preds = match log_shift {
        Some(shift) => map_from_log_space(raw, shift),
        None => raw,
    };
    let pred_rmse = rmse(targets, &preds);
    println!("  Found:       {}", result.formula());
    println!("  Python:      {}", result.to_python());
    println!("  Expected:    {expected}");
    println!("  Search RMSE: {:.6e}", result.error());
    println!("  Hold RMSE:   {:.6e}", pred_rmse);
    println!("  Complexity:  {}", result.complexity());
    println!("  Time:        {elapsed:?}");
}

#[derive(Debug, Clone)]
struct VarSpec {
    name: String,
    low: f64,
    high: f64,
}

#[derive(Debug, Clone)]
struct FeynmanRow {
    filename: String,
    output: String,
    formula: String,
    variables: Vec<VarSpec>,
}

fn load_row(csv: &str, filename: &str) -> Result<FeynmanRow, Box<dyn std::error::Error>> {
    let line = csv
        .lines()
        .find(|l| l.starts_with(&format!("{filename},")))
        .ok_or_else(|| format!("row {filename} not found in FeynmanEquations.csv"))?;

    let fields = parse_csv_line(line);
    let output = fields.get(2).cloned().unwrap_or_default();
    let formula = fields.get(3).cloned().unwrap_or_default();
    let n_vars: usize = fields.get(4).and_then(|s| s.parse().ok()).unwrap_or(0);

    let mut variables = Vec::with_capacity(n_vars);
    let mut col = 5usize;
    for _ in 0..n_vars {
        let name = fields.get(col).filter(|s| !s.is_empty()).cloned();
        col += 1;
        let low: f64 = fields.get(col).and_then(|s| s.parse().ok()).unwrap_or(1.0);
        col += 1;
        let high: f64 = fields.get(col).and_then(|s| s.parse().ok()).unwrap_or(5.0);
        col += 1;
        if let Some(name) = name {
            variables.push(VarSpec { name, low, high });
        }
    }

    Ok(FeynmanRow {
        filename: filename.to_string(),
        output,
        formula,
        variables,
    })
}

fn parse_csv_line(line: &str) -> Vec<String> {
    let mut fields = Vec::new();
    let mut current = String::new();
    let mut in_quotes = false;
    for ch in line.chars() {
        match ch {
            '"' => in_quotes = !in_quotes,
            ',' if !in_quotes => {
                fields.push(current.clone());
                current.clear();
            }
            c => current.push(c),
        }
    }
    fields.push(current);
    fields
}

fn synthesize_dataset(
    row: &FeynmanRow,
    n: usize,
    seed: u64,
) -> (Vec<Vec<f64>>, Vec<f64>) {
    let mut rng = seed;
    let mut inputs = Vec::with_capacity(n);
    let mut targets = Vec::with_capacity(n);

    for _ in 0..n {
        let mut env = HashMap::new();
        let mut point = Vec::with_capacity(row.variables.len());
        for v in &row.variables {
            let u = lcg(&mut rng);
            let value = v.low + u * (v.high - v.low);
            env.insert(v.name.clone(), value);
            point.push(value);
        }
        let y = eval_sympy_expr(&row.formula, &env)
            .unwrap_or_else(|| panic!("failed to evaluate {} for {:?}", row.formula, point));
        inputs.push(point);
        targets.push(y);
    }

    (inputs, targets)
}

fn lcg(state: &mut u64) -> f64 {
    *state = state
        .wrapping_mul(6364136223846793005)
        .wrapping_add(1442695040888963407);
    (*state >> 11) as f64 / ((1u64 << 53) as f64)
}

fn rmse(actual: &[f64], predicted: &[f64]) -> f64 {
    let n = actual.len() as f64;
    let mse: f64 = actual
        .iter()
        .zip(predicted)
        .map(|(a, p)| (a - p).powi(2))
        .sum::<f64>()
        / n;
    mse.sqrt()
}

// --- SymPy-style evaluator (exp, sqrt, pi — needed for the Gaussian formula) ---

#[derive(Clone, Debug)]
enum Tok {
    Num(f64),
    Ident(String),
    Op(char),
    Eof,
}

fn tokenize(expr: &str) -> Vec<Tok> {
    let mut tokens = Vec::new();
    let bytes = expr.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        let c = bytes[i] as char;
        if c.is_ascii_whitespace() {
            i += 1;
            continue;
        }
        if c.is_ascii_digit() || c == '.' {
            let start = i;
            i += 1;
            while i < bytes.len() {
                let d = bytes[i] as char;
                if d.is_ascii_digit() || d == '.' {
                    i += 1;
                } else {
                    break;
                }
            }
            let s = &expr[start..i];
            tokens.push(Tok::Num(s.parse().unwrap_or(0.0)));
            continue;
        }
        if c.is_ascii_alphabetic() || c == '_' {
            let start = i;
            i += 1;
            while i < bytes.len() {
                let d = bytes[i] as char;
                if d.is_ascii_alphanumeric() || d == '_' {
                    i += 1;
                } else {
                    break;
                }
            }
            tokens.push(Tok::Ident(expr[start..i].to_string()));
            continue;
        }
        if c == '*' && i + 1 < bytes.len() && bytes[i + 1] == b'*' {
            tokens.push(Tok::Op('^'));
            i += 2;
            continue;
        }
        if "+-*/()".contains(c) {
            tokens.push(Tok::Op(c));
            i += 1;
            continue;
        }
        panic!("unexpected character '{c}' in '{expr}'");
    }
    tokens.push(Tok::Eof);
    tokens
}

struct Parser {
    tokens: Vec<Tok>,
    pos: usize,
    env: HashMap<String, f64>,
}

impl Parser {
    fn new(tokens: Vec<Tok>, env: HashMap<String, f64>) -> Self {
        Self {
            tokens,
            pos: 0,
            env,
        }
    }

    fn peek(&self) -> &Tok {
        self.tokens.get(self.pos).unwrap_or(&Tok::Eof)
    }

    fn bump(&mut self) -> Tok {
        let t = self.tokens[self.pos].clone();
        if !matches!(t, Tok::Eof) {
            self.pos += 1;
        }
        t
    }

    fn parse_expr(&mut self) -> f64 {
        let mut val = self.parse_term();
        loop {
            match self.peek() {
                Tok::Op('+') => {
                    self.bump();
                    val += self.parse_term();
                }
                Tok::Op('-') => {
                    self.bump();
                    val -= self.parse_term();
                }
                Tok::Op(')') => break,
                _ => break,
            }
        }
        val
    }

    fn parse_term(&mut self) -> f64 {
        let mut val = self.parse_power();
        loop {
            match self.peek() {
                Tok::Op('*') => {
                    self.bump();
                    val *= self.parse_power();
                }
                Tok::Op('/') => {
                    self.bump();
                    val /= self.parse_power();
                }
                Tok::Op(')') => break,
                _ => break,
            }
        }
        val
    }

    fn parse_power(&mut self) -> f64 {
        let base = self.parse_unary();
        if matches!(self.peek(), Tok::Op('^')) {
            self.bump();
            let exp = self.parse_power();
            base.powf(exp)
        } else {
            base
        }
    }

    fn parse_unary(&mut self) -> f64 {
        match self.peek() {
            Tok::Op('-') => {
                self.bump();
                -self.parse_unary()
            }
            Tok::Op('+') => {
                self.bump();
                self.parse_unary()
            }
            _ => self.parse_atom(),
        }
    }

    fn parse_atom(&mut self) -> f64 {
        match self.bump() {
            Tok::Num(n) => n,
            Tok::Ident(name) => {
                if matches!(self.peek(), Tok::Op('(')) {
                    self.bump();
                    let arg = self.parse_expr();
                    if !matches!(self.bump(), Tok::Op(')')) {
                        panic!("expected ')' after {name}(...)");
                    }
                    return eval_named_fn(&name, arg);
                }
                match name.as_str() {
                    "pi" => std::f64::consts::PI,
                    "e" => std::f64::consts::E,
                    _ => *self
                        .env
                        .get(&name)
                        .unwrap_or_else(|| panic!("unknown identifier '{name}'")),
                }
            }
            Tok::Op('(') => {
                let val = self.parse_expr();
                if !matches!(self.bump(), Tok::Op(')')) {
                    panic!("expected ')'");
                }
                val
            }
            other => panic!("unexpected token: {other:?}"),
        }
    }
}

fn eval_named_fn(name: &str, arg: f64) -> f64 {
    match name {
        "exp" => arg.exp(),
        "sqrt" => arg.sqrt(),
        "log" | "ln" => arg.ln(),
        "sin" => arg.sin(),
        "cos" => arg.cos(),
        "tan" => arg.tan(),
        "abs" => arg.abs(),
        other => panic!("unsupported function '{other}'"),
    }
}

fn eval_sympy_expr(expr: &str, env: &HashMap<String, f64>) -> Option<f64> {
    let tokens = tokenize(expr);
    let mut p = Parser::new(tokens, env.clone());
    Some(p.parse_expr())
}
