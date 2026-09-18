import datetime

import polars as pl
import pytest

try:
    import pyarrow as pa
except ImportError:  # pragma: no cover
    pa = None

import hermes as hr
from hermes.core.errors import NormalizationError
from hermes.normalization import (
    Cast,
    ConvertUnit,
    MapConcept,
    MapValue,
    NormalizationEngine,
    NormalizationRule,
    NormalizeBoolean,
    NormalizeCountry,
    NormalizeCurrency,
    NormalizeDate,
    NormalizeIdentifier,
    NormalizeName,
    NormalizeNull,
    NormalizeString,
    NormalizeUnit,
    ParsePeriod,
    Rename,
    Round,
    RuleConfigurationError,
    RuleExecutionError,
    StripCharacters,
)


def test_rename():
    data = pl.DataFrame({"a": [1, 2], "b": [3, 4]})
    out = Rename({"a": "alpha", "b": "beta"}).apply(data)
    assert out.columns == ["alpha", "beta"]


def test_rename_missing_column_raises():
    with pytest.raises(RuleExecutionError):
        Rename({"nope": "x"}).apply(pl.DataFrame({"a": [1]}))


def test_cast_named():
    data = pl.DataFrame({"revenue": ["1.5", "2.25"], "employees": ["3", "4"]})
    out = Cast({"revenue": "float", "employees": "integer"}).apply(data)
    assert out.schema["revenue"] == pl.Float64
    assert out.schema["employees"] == pl.Int64


def test_cast_invalid_values_null_when_not_strict():
    data = pl.DataFrame({"x": ["1.5", "oops"]})
    out = Cast("x", "float", strict=False).apply(data)
    assert out["x"].to_list() == [1.5, None]


def test_cast_unknown_type_raises():
    with pytest.raises(RuleConfigurationError):
        Cast("x", "monetary")


def test_normalize_string():
    data = pl.DataFrame({"name": ["  Alice  SMITH ", " bob\tdylan"]})
    out = NormalizeString("name", case="lower").apply(data)
    assert out["name"].to_list() == ["alice smith", "bob dylan"]
    out2 = NormalizeString("name", case="title").apply(data)
    assert out2["name"].to_list() == ["Alice Smith", "Bob Dylan"]


def test_normalize_null():
    data = pl.DataFrame({"a": ["", "x", "NA"], "b": [1, None, 2]})
    out = NormalizeNull(["a"]).apply(data)
    assert out["a"].to_list() == [None, "x", None]
    assert out["b"].to_list() == [1, None, 2]


def test_normalize_null_custom_values():
    data = pl.DataFrame({"a": ["-", "x"]})
    out = NormalizeNull(["a"], null_values=("-",)).apply(data)
    assert out["a"].to_list() == [None, "x"]


def test_normalize_boolean():
    data = pl.DataFrame({"married": ["yes", "no", "maybe", "YES"]})
    out = NormalizeBoolean("married").apply(data)
    assert out["married"].to_list() == [True, False, None, True]
    assert out.schema["married"] == pl.Boolean


def test_normalize_date():
    data = pl.DataFrame({"d": ["2024-01-15", "01/15/2024", "garbage"]})
    out = NormalizeDate("d", formats=("%Y-%m-%d", "%m/%d/%Y")).apply(data)
    assert out["d"].to_list() == [datetime.date(2024, 1, 15), datetime.date(2024, 1, 15), None]
    assert out.schema["d"] == pl.Date


def test_normalize_datetime_default_formats():
    data = pl.DataFrame({"d": ["2024-01-15", "2024-01-15 12:30:00", "garbage"]})
    out = NormalizeDate("d").apply(data)
    assert out.schema["d"] == pl.Datetime
    assert out["d"].to_list() == [
        datetime.datetime(2024, 1, 15, 0, 0),
        datetime.datetime(2024, 1, 15, 12, 30),
        None,
    ]


def test_normalize_date_raise_on_bad():
    data = pl.DataFrame({"d": ["2024-01-15", "garbage"]})
    with pytest.raises(NormalizationError):
        NormalizeDate("d", errors="raise").apply(data)


def test_normalize_country():
    data = pl.DataFrame({"c": ["USA", "Germany", "pakistan", "zzz"]})
    out = NormalizeCountry("c").apply(data)
    assert out["c"].to_list() == ["US", "DE", "PK", "zzz"]


def test_normalize_currency():
    data = pl.DataFrame({"cur": ["USD", "$", "EUR", "gbp"]})
    out = NormalizeCurrency("cur").apply(data)
    assert out["cur"].to_list() == ["USD", "USD", "EUR", "GBP"]


def test_normalize_unit():
    data = pl.DataFrame({"u": ["Kg", "kilograms", "ml", "mL"]})
    out = NormalizeUnit("u").apply(data)
    assert out["u"].to_list() == ["kg", "kg", "mL", "mL"]


def test_convert_unit():
    data = pl.DataFrame({"weight": [1000.0, 2500.5, None]})
    out = ConvertUnit("weight", "g", "kg").apply(data)
    assert out["weight"].to_list() == pytest.approx([1.0, 2.5005, None])


def test_convert_unit_validate_unknown():
    with pytest.raises(RuleConfigurationError):
        ConvertUnit("weight", "furlong", "kg")


def test_normalize_identifier():
    data = pl.DataFrame({"id": ["  abc-def ", " x-y  ", "Z"]})
    out = NormalizeIdentifier("id", case="upper", remove="-").apply(data)
    assert out["id"].to_list() == ["ABCDEF", "XY", "Z"]


def test_normalize_name():
    data = pl.DataFrame({"name": [" APPLE  INC. ", "  bob  dylan  "]})
    out = NormalizeName("name", case="title", remove_chars=".").apply(data)
    assert out["name"].to_list() == ["Apple Inc", "Bob Dylan"]


def test_map_value():
    data = pl.DataFrame({"x": ["yes", "no", "maybe"]})
    out = MapValue("x", {"yes": "YES", "no": "NO"}).apply(data)
    assert out["x"].to_list() == ["YES", "NO", "maybe"]


def test_map_value_case_insensitive():
    data = pl.DataFrame({"x": ["YES", "No"]})
    out = MapValue("x", {"yes": "y", "no": "n"}, case_insensitive=True).apply(data)
    assert out["x"].to_list() == ["y", "n"]


def test_map_concept():
    data = pl.DataFrame({"status": ["s1", "x"]})
    out = MapConcept("status", {"s1": "active"}).apply(data)
    assert out["status"].to_list() == ["active", "x"]


def test_parse_period():
    data = pl.DataFrame({"p": ["2025Q1", "Q2 2025", "FY2025", "2025", "2025-03", "garbage"]})
    out = ParsePeriod("p").apply(data)
    assert out["p"].to_list() == ["2025Q1", "2025Q2", "FY2025", "2025", "2025-03", "garbage"]


def test_parse_period_idempotent():
    data = pl.DataFrame({"p": ["2025Q1", "FY2025", "2025-03"]})
    once = ParsePeriod("p").apply(data)
    twice = ParsePeriod("p").apply(once)
    assert once.equals(twice)


def test_strip_characters():
    data = pl.DataFrame({"x": ["a-b-c", "--"]})
    out = StripCharacters("x", "-").apply(data)
    assert out["x"].to_list() == ["abc", ""]


def test_round():
    data = pl.DataFrame({"x": [1.234, 5.678]})
    out = Round("x", 2).apply(data)
    assert out["x"].to_list() == [1.23, 5.68]


def test_round_half_up():
    data = pl.DataFrame({"x": [2.345]})
    out = Round("x", 2, half_up=True).apply(data)
    assert out["x"].to_list() == [2.35]


# -- engine ------------------------------------------------------------------


def test_engine_ordering_is_preserved():
    engine = NormalizationEngine([Rename({"a": "b"}), Rename({"b": "c"})])
    out = engine.normalize(pl.DataFrame({"a": [1]}))
    assert out.columns == ["c"]


def test_engine_fluent_add():
    engine = NormalizationEngine().add_rule(Rename({"a": "b"}))
    assert engine.add_rule(Rename({"b": "c"})).rules[1].name == "Rename"


def test_engine_records_in_out():
    engine = NormalizationEngine([NormalizeString("name", case="lower")])
    out = engine.normalize([{"name": "Alice"}, {"name": "Bob"}])
    assert out == [{"name": "alice"}, {"name": "bob"}]


def test_engine_single_record():
    engine = NormalizationEngine([NormalizeString("name", case="upper")])
    assert engine.normalize_record({"name": "alice"}) == {"name": "ALICE"}


def test_engine_stream():
    engine = NormalizationEngine([NormalizeString("name", case="upper")])
    out = list(engine.normalize_stream([{"name": "alice"}, {"name": "bob"}]))
    assert out == [{"name": "ALICE"}, {"name": "BOB"}]


def test_engine_lazyframe():
    engine = NormalizationEngine([NormalizeString("name", case="lower")])
    out = engine.normalize(pl.DataFrame({"name": ["Alice"]}).lazy())
    assert isinstance(out, pl.LazyFrame)
    assert out.collect()["name"].to_list() == ["alice"]


@pytest.mark.skipif(pa is None, reason="pyarrow not installed")
def test_engine_arrow():
    engine = NormalizationEngine([NormalizeString("name", case="upper")])
    table = pa.Table.from_pylist([{"name": "alice"}])
    out = engine.normalize(table)
    assert isinstance(out, pa.Table)
    assert out.column("name").to_pylist() == ["ALICE"]


def test_engine_missing_column_raises():
    engine = NormalizationEngine([Round("nope", 2)])
    with pytest.raises(RuleExecutionError):
        engine.normalize(pl.DataFrame({"a": [1.5]}))


def test_engine_remove_and_clear():
    engine = NormalizationEngine([Rename({"a": "b"}), Rename({"b": "c"})])
    engine.remove_rule("Rename")
    assert len(engine.rules) == 1
    engine.clear_rules()
    assert engine.rules == []


def test_engine_describe():
    engine = NormalizationEngine([MapValue("x", {"a": "b"})])
    desc = engine.describe()
    assert desc[0]["name"] == "MapValue"
    assert desc[0]["mapping"] == {"a": "b"}


def test_engine_validate():
    engine = NormalizationEngine([Rename({"a": "b"})])
    engine.validate()
    with pytest.raises(RuleConfigurationError):
        engine.add_rule(_BadRule()).validate()


class _BadRule(NormalizationRule):
    def apply(self, data, context=None):
        return data

    def validate(self):
        raise RuleConfigurationError("bad")


def test_engine_report_success():
    data = pl.DataFrame({"a": [" X ", "Y"]})
    result = NormalizationEngine([NormalizeString("a", case="lower")]).normalize_report(data)
    assert result.success
    assert result.rules == ["NormalizeString"]
    assert result.changes >= 1
    assert result.data["a"].to_list() == ["x", "y"]


def test_engine_report_failure():
    data = pl.DataFrame({"a": [1]})
    result = NormalizationEngine([Round("a", 2), Round("nope", 2)]).normalize_report(data)
    assert not result.success
    assert result.errors


def test_engine_unsupported_input():
    with pytest.raises(NormalizationError):
        NormalizationEngine().normalize(123)


# -- public API --------------------------------------------------------------

def test_hr_normalize():
    data = [{"status": "yes", "name": " X "}]
    out = hr.normalize(data, rules=[NormalizeBoolean("status"), NormalizeString("name", case="lower")])
    assert out == [{"status": True, "name": "x"}]


def test_hr_normalize_report():
    out = hr.normalize([{"a": "x"}], rules=[MapValue("a", {"x": "X"})], report=True)
    assert out.success
    assert out.changes == 1
