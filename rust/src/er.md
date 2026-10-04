### 1. Input ingestion

Accept arbitrary records from:

* CSV / JSON / Parquet
* database rows
* API payloads
* streaming events

It should not require the caller to manually define matching rules for every dataset.

### 2. Schema / field inference

Automatically determine:

* field names and types
* likely identifiers
* names
* emails
* phone numbers
* addresses
* dates
* organization names
* URLs / domains
* IDs
* categorical attributes

It should also detect that different schemas may represent the same concept:

`first_name` ↔ `fname` ↔ `givenName`

### 3. Data normalization

Create canonical representations for comparable values:

* casing
* whitespace
* Unicode
* punctuation
* phone formats
* email formats
* addresses
* names
* dates
* common abbreviations
* transliteration where applicable

Keep both **raw value and normalized value**.

### 4. Entity representation

Build an internal entity model independent of the input schema.

For example:

```text
Entity
 ├── entity_id
 ├── attributes
 ├── source_records
 ├── aliases
 ├── identifiers
 └── confidence / provenance
```

An entity can accumulate information from multiple records.

### 5. Candidate generation

Do **not** compare every record with every entity.

Automatically create candidates using techniques such as:

* exact indexes
* inverted indexes
* blocking
* prefix/suffix keys
* phonetic keys
* n-grams
* locality-sensitive hashing
* embeddings/vector search
* field-specific indexes

### 6. Matching

For each record/candidate pair, calculate evidence from multiple fields.

Examples:

```text
name similarity
email similarity
phone similarity
address similarity
organization similarity
identifier equality
source reliability
historical evidence
```

The matcher should combine these into a match decision rather than relying on one field.

### 7. Decision layer

Produce at least:

```text
MATCH
NO_MATCH
UNCERTAIN
```

with:

```text
confidence
evidence
matched_entity_id
```

Uncertain cases should not be silently merged.

### 8. Entity creation

If no sufficiently strong existing entity matches:

```text
create new entity
```

If a strong match exists:

```text
link record → existing entity
```

### 9. Entity merging

Entities may initially be created separately and later become connected.

The system therefore needs:

```text
entity A ← record 1
entity B ← record 2

new evidence

A ↔ B

merge / consolidate
```

This needs lineage so merges can be reversed or audited.

### 10. Incremental learning

The pipeline should improve from previously resolved data.

It should learn things like:

* recurring aliases
* source-specific formats
* reliable identifiers
* common transformations
* accepted/rejected matches
* field reliability

But learned behavior needs versioning; otherwise the system can silently change historical resolutions.

### 11. Cross-source resolution

It should understand that the same real-world entity can appear differently across sources:

```text
CRM
ERP
Payments
Support
Web
CSV
API
```

and connect them into one canonical entity.

### 12. Relationship resolution

General entity resolution should eventually support relationships:

```text
Person → works_for → Company
Person → owns → Account
Company → has_address → Address
Person → has_phone → Phone
```

This allows evidence from related entities to contribute to resolution.

### 13. Provenance

Every resolved attribute and relationship should answer:

```text
Where did this come from?
When?
Which source?
Which record?
What transformation?
Why was it accepted?
```

Never lose the original record.

### 14. Explainability

For every match, expose something like:

```text
record: 8472
entity: E10291

decision: MATCH
confidence: 0.94

evidence:
  email: exact
  phone: exact
  name: 0.91 similarity
  address: 0.76 similarity

model_version: 3
```

### 15. Uncertainty / human review

The system needs a review queue:

```text
high confidence → automatically link
medium confidence → review
low confidence → create / leave unresolved
```

Human decisions should become training/evaluation data.

### 16. Deduplication

Resolve duplicates both:

```text
incoming record → existing entity
```

and:

```text
existing entity ↔ existing entity
```

### 17. Temporal handling

Entities change.

The system should preserve:

* previous names
* previous addresses
* old phone numbers
* historical identifiers
* validity periods

So an old record can still resolve correctly.

### 18. Evaluation

It needs built-in evaluation for:

* precision
* recall
* false merges
* false splits
* candidate recall
* confidence calibration
* source-specific performance

False merges are particularly important because they contaminate the entity itself.

### 19. Configuration without requiring configuration

The default API should ideally be:

```rust
let result = resolver.resolve(data).await?;
```

But advanced users should be able to override:

```rust
ResolverConfig {
    matching_strategy,
    thresholds,
    field_hints,
    blocking,
    models,
    source_weights,
    ...
}
```

Automatic inference should be the default, not the only mode.

### 20. Rust architecture

A reasonable internal pipeline is:

```text
Input
  ↓
Ingestion
  ↓
Schema Inference
  ↓
Field Semantic Inference
  ↓
Normalization
  ↓
Entity / Record Representation
  ↓
Indexing
  ↓
Candidate Generation
  ↓
Pairwise Matching
  ↓
Decision Engine
  ├── MATCH ───────→ Link
  ├── NO_MATCH ────→ Create Entity
  └── UNCERTAIN ───→ Review
             ↓
      Entity Consolidation
             ↓
       Knowledge Graph
             ↓
     Provenance / Audit
             ↓
       Feedback / Learning
```

The key requirement is that **“intelligent” should not mean one giant model**. The system should combine schema inference, normalization, deterministic identifiers, candidate retrieval, fuzzy matching, ML/embeddings, decisioning, entity clustering, provenance, and feedback into one pipeline.
