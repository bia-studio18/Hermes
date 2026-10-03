mod ingestion;
mod similarity;

pub struct Module {
    pub name: &'static str,
    pub components: Vec<&'static str>,
}

impl Module {
    pub fn new(name: &'static str) -> Self {
        Self {
            name,
            components: Vec::new(),
        }
    }

    pub fn add(&mut self, component: &'static str) {
        self.components.push(component);
    }
}

pub fn register(m: &mut Module) {
    m.add("ingestion");
    m.add("similarity");
}