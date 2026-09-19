import json

import polars as pl
import pytest

from hermes.core.errors import ParseError
from hermes.parsing.engine import ParserEngine

engine = ParserEngine()


def test_detect_format():
    assert engine.detect_format("data.csv") == "csv"
    assert engine.detect_format("a/b/data.jsonl") == "jsonl"
    assert engine.detect_format("data.ndjson") == "jsonl"
    assert engine.detect_format("data.parquet") == "parquet"
    assert engine.detect_format("<a><b>1</b></a>") == "xml"
    assert engine.detect_format(b'{"a": 1}') == "json"
    assert engine.detect_format("noext") is None
    assert engine.detect_format(b"\x00\x01") is None


def test_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,x\n2,y\n")
    df = engine.parse(p)
    assert df.shape == (2, 2)
    assert df.columns == ["a", "b"]


def test_csv_from_bytes():
    df = engine.parse(b"a,b\n1,x\n2,y\n", format="csv")
    assert df.shape == (2, 2)


def test_json(tmp_path):
    p = tmp_path / "data.json"
    p.write_text(json.dumps([{"a": 1, "b": 2}, {"a": 3, "b": 4}]))
    df = engine.parse(p)
    assert df.shape == (2, 2)


def test_json_content():
    df = engine.parse('[{"a": 1}, {"a": 2}]')
    assert df.height == 2
    assert df["a"].to_list() == [1, 2]


def test_json_lines(tmp_path):
    p = tmp_path / "data.jsonl"
    p.write_text('{"a": 1}\n{"a": 2}\n')
    df = engine.parse(p)
    assert df.height == 2
    assert df["a"].to_list() == [1, 2]


def test_parquet_roundtrip(tmp_path):
    p = tmp_path / "data.parquet"
    pl.DataFrame({"a": [1, 2], "b": ["x", "y"]}).write_parquet(p)
    df = engine.parse(p)
    assert df.shape == (2, 2)


def test_xml_records(tmp_path):
    p = tmp_path / "data.xml"
    p.write_text(
        "<root><row><name>Apple</name><price>1.5</price></row><row><name>Banana</name><price>0.5</price></row></root>"
    )
    df = engine.parse(p)
    assert df.shape == (2, 2)
    assert df["name"].to_list() == ["Apple", "Banana"]


def test_xml_flat_root():
    df = engine.parse("<root><a>1</a><b>2</b></root>")
    assert df.columns == ["a", "b"]
    assert df.row(0) == ("1", "2")


def test_xml_namespace():
    df = engine.parse('<root xmlns="urn:x"><row><a>1</a></row></root>')
    assert df.columns == ["a"]


def test_xml_nested():
    df = engine.parse("<root><row><person><name>X</name></person></row></root>")
    assert df.columns == ["person.name"]


def test_unsupported_format():
    with pytest.raises(ParseError):
        engine.parse(b"\x00\x01unrecognized")
    with pytest.raises(ParseError):
        engine.parse("file.unknown")


def test_malformed_csv():
    with pytest.raises(ParseError):
        engine.parse(b"a,b\n1\n2,3")


def test_malformed_json():
    with pytest.raises(ParseError):
        engine.parse(b"{not json", format="json")
