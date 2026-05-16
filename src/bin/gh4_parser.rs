use oxieml::parser::{parse, to_compact_string};

fn main() {

// Parse E(x, y) notation
let tree = parse("E(E(1, 1), 1)").unwrap();
assert_eq!(tree.depth(), 2);

// Also accepts eml(x, y) notation
let tree = parse("eml(E(1, x0), 1)").unwrap();

// Convert back to compact string
let compact = to_compact_string(&tree);
assert_eq!(parse(&compact).unwrap(), tree); // roundtrip
}