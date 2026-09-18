"""
| Class / function                         | What it does                                      |
| ---------------------------------------- | ------------------------------------------------- |
| `NormalizationEngine`                    | Main engine that executes normalization           |
| `NormalizationEngine.normalize()`        | Normalize a complete dataset                      |
| `NormalizationEngine.normalize_record()` | Normalize one record                              |
| `NormalizationEngine.normalize_stream()` | Normalize records lazily                          |
| `NormalizationEngine.add_rule()`         | Add one rule                                      |
| `NormalizationEngine.add_rules()`        | Add multiple rules                                |
| `NormalizationEngine.remove_rule()`      | Remove a rule                                     |
| `NormalizationEngine.clear_rules()`      | Remove all rules                                  |
| `NormalizationEngine.rules`              | Current pipeline                                  |
| `NormalizationEngine.validate()`         | Validate the configured pipeline before execution |
| `NormalizationEngine.describe()`         | Return a description of the pipeline              |
| `_apply_rule()`                          | Internal rule execution                           |
| `_apply_rules()`                         | Internal sequential execution                     |

"""

class NormalizationEngine:
    def normalize(self): ...

    def normalize_record(self): ...

    def normalize_stream(self): ...

    def add_rule(self): ...

    def add_rules(self): ...

    def remove_rule(self): ...

    def clear_rules(self): ...

    def rules(self): ...

    def validate(self): ...

    def describe(self): ...


def _apply_rule():
    ...

def _apply_rules(): ...