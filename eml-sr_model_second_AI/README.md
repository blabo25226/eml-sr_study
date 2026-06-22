# eml-sr_model_first_AI

`eml-sr_model_first_AI` は、Exp-Minus-Log (EML) オペレータを用いた記号回帰ライブラリ `eml-sr` の次世代改善版です。
従来の `eml-sr` では、探索空間内に固定値（$\pi, e$ など）が存在し、それらの組み合わせによる近似表現で探索リソースを浪費してしまう弱点がありました。本クレートはこれを克服し、「**定数を完全に抽象化（パラメータ化）し、探索評価のたびに連続最適化を走らせる（Model-First アプローチ）**」機構を導入しています。

## 主な改善点
1. **ネイティブなパラメータノード（`Param`）の導入**:
   数式ツリーの中に初期状態から未定のパラメータ `C` を割り当てることで、$C_1 \times x + C_2$ などの複雑な係数フィッティングを初期探索から高精度に評価します。
2. **高速な連続最適化**:
   ツリー結合時に毎回 L-BFGS/勾配法ベースの軽量な最適化が走り、数式の真のポテンシャル（MSE）を評価します。
3. **パラメータの再最適化維持**:
   一度最適化されたパラメータも固定値にはならず、上位レイヤーで他の数式と結合された際に「初期値を持つパラメータ」として再度全体で最適化されます。

## インストール方法（Python）

Python 側からは元の `eml_sr` モジュールと互換性のある（しかし内部エンジンが進化した）`eml_sr_model_first_AI` として利用できます。

```bash
cd eml-sr_model_first_AI
pip install .
```

```python
import eml_sr_model_first_AI
import numpy as np

# 探索エンジンの初期化
searcher = eml_sr_model_first_AI.Searcher(max_complexity=10, beam_width=500)

# 例: データの学習
X = np.random.rand(100, 2)
y = 3.5 * X[:, 0] + np.sin(2.0 * X[:, 1]) - 1.2
result = searcher.find_multivariate(X, y)

print(f"発見された数式: {result.formula}")
print(f"誤差(MSE): {result.error}")
```

## Rust からの利用

Rust のプロジェクトから利用する場合は、`Cargo.toml` にパス指定で追加します。

```toml
[dependencies]
eml_sr = { path = "../eml-sr_model_first_AI" }
```

```rust
use eml_sr::{Searcher, SearchConfig};

fn main() {
    let config = SearchConfig::builder().max_complexity(5).build();
    let searcher = Searcher::new(config);
    // ...
}
```

## 開発と実行
* `cargo build --release` で最適化ビルド
* `cargo test` でテスト実行
* `cargo run --example 01_simple_discovery` などでサンプルの動作確認が可能
