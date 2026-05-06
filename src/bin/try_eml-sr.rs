use eml_sr::{Searcher, SearchConfig};

fn main() {
    let searcher = Searcher::new(SearchConfig::default());
    let xs = vec![1.0, 2.0, 3.0, 4.0, 5.0];
    let ys = vec![2.5, 4.5, 6.5, 8.5, 10.5];

    if let Ok(result) = searcher.find_function(&xs, &ys) {
        println!("Found formula: {}", result.formula());
    }
}
