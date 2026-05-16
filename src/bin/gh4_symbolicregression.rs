use oxieml::symreg::{SymRegConfig, SymRegEngine};

fn main() {
// Generate data from an unknown function
let inputs: Vec<Vec<f64>> = (0..50).map(|i| vec![i as f64 * 0.1]).collect();
let targets: Vec<f64> = inputs.iter().map(|x| x[0].exp()).collect();

let config = SymRegConfig {
    max_depth: 2,
    learning_rate: 1e-2,
    tolerance: 1e-8,
    ..Default::default()
};

let engine = SymRegEngine::new(config);
let formulas = engine.discover(&inputs, &targets, 1).unwrap();

println!("Best formula: {}", formulas[0].pretty);
println!("MSE: {:.2e}", formulas[0].mse);
}