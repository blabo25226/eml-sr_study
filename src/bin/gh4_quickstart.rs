use oxieml::{Canonical, EmlTree, EvalCtx};

fn main() {
    // Build exp(x) = eml(x, 1)
    let x = EmlTree::var(0);
    let exp_x = Canonical::exp(&x);

    // Evaluate at x = 1.0 -> e
    let ctx = EvalCtx::new(&[1.0]);
    let result = exp_x.eval_real(&ctx).unwrap();
    assert!((result - std::f64::consts::E).abs() < 1e-10);

    // Euler's number: eml(1, 1) = exp(1) - ln(1) = e
    let e = Canonical::euler();
    println!("{}", e); // "eml(1, 1)"

    // Negation, addition, multiplication — all from eml and 1
    let y = EmlTree::var(1);
    let sum = Canonical::add(&x, &y);
    let product = Canonical::mul(&x, &y);

    // Lower to standard operations for efficient evaluation
    let lowered = exp_x.lower();
    println!("{}", lowered.to_pretty()); // "exp(x0)"
    let fast_result = lowered.eval(&[1.0]);

    // Generate Rust source code
    let code = oxieml::compile::compile_to_rust(&exp_x, "my_exp");
    println!("{code}");
}
