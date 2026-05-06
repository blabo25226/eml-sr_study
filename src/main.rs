// eml_srクレートから、探索器（Searcher）と設定（SearchConfig）をインポート
use eml_sr::{Searcher, SearchConfig};

fn main() {
    println!("=== EML Symbolic Regression Study ===");

    // 1. 探索の設定を作成（今回はデフォルト設定を使用）
    let config = SearchConfig::default();
    
    // 2. 探索器（Searcher）を初期化
    let searcher = Searcher::new(config);

    println!("探索器の初期化に成功しました！");
    println!("ここにデータセットを渡して、数式探索（学習）の処理を追記していきます。");
}