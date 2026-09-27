#[derive(Debug, Clone, PartialEq, Eq)]
pub struct BlockingKey {
    pub field: Option<String>,
    pub value: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct CandidatePair {
    pub left_index: usize,
    pub right_index: usize,
    pub blocking_key: String,
}

pub fn build_keys(_values: &[String]) -> Vec<BlockingKey> {
    unimplemented!("blocking key generation")
}

pub fn find_candidates(_keys: &[BlockingKey]) -> Vec<CandidatePair> {
    unimplemented!("blocking candidate generation")
}
