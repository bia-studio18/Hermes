import pytest
from hermes._rust import er


def test_scores_run_from_identical_to_unrelated():
    assert er.exact_similarity("Ada", " ada ") == 1.0
    assert er.exact_similarity("Ada", "Bob") == 0.0
    assert er.levenshtein_similarity("kitten", "kitten") == 1.0
    assert 0.0 < er.levenshtein_similarity("kitten", "sitting") < 1.0
    assert er.date_similarity("2024-01-01", "2024-01-06", "day_difference", 10) == 0.5
    assert er.date_similarity("2024-01-01", "2024-01-11", "day_difference", 10) == 0.0
    assert er.email_similarity("a@x.com", "a@y.com", "combined") == 0.5


def test_sources_are_sniffed_and_bad_input_raises():
    assert er.identify_source("data.csv") == "CSV"
    assert er.identify_source("kafka://events") == "STREAMING"
    assert er.identify_source("mystery") == "UNKNOWN"

    with pytest.raises(er.HermesErError):
        er.email_similarity("nope", "a@b.com", "exact")
    with pytest.raises(er.HermesErError):
        er.token_similarity("a", "b", "bogus")
