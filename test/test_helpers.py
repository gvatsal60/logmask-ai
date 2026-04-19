"""
Test helpers functions.
"""

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine

from helpers import analyze, anonymize
from _const import SAMPLE_TXT


def test_helpers_logic(monkeypatch):
    """
    Test the helpers logic.
    """
    st_model = "en"
    st_model_package = "stanza"
    st_ta_key = None
    st_ta_endpoint = None

    analyzer_params = (st_model_package, st_model, st_ta_key, st_ta_endpoint)

    # Read default text
    st_text = SAMPLE_TXT

    name_start = st_text.index("David Johnson")
    name_end = name_start + len("David Johnson")
    fake_analyze_results = [
        RecognizerResult(
            entity_type="PERSON",
            start=name_start,
            end=name_end,
            score=0.99,
        )
    ]

    class FakeAnalyzerEngine:
        def __init__(self):
            self.last_kwargs = None

        def analyze(self, **kwargs):
            self.last_kwargs = kwargs
            return fake_analyze_results

    fake_engine = FakeAnalyzerEngine()
    monkeypatch.setattr(helpers, "analyzer_engine", lambda *args, **kwargs: fake_engine)

    # Analyze
    st_analyze_results = analyze.__wrapped__(
        *analyzer_params,
        text=st_text,
        entities="All",
        language="en",
        score_threshold=0.35,
        return_decision_process=True,
        allow_list=[],
        deny_list=[],
    )
    assert len(st_analyze_results) > 0
    assert fake_engine.last_kwargs["entities"] is None
    assert "deny_list" not in fake_engine.last_kwargs

    # Anonymize
    monkeypatch.setattr(helpers, "anonymizer_engine", AnonymizerEngine)
    st_anonymize_results = anonymize(
        text=st_text,
        operator="replace",
        mask_char=None,
        number_of_chars=None,
        encrypt_key=None,
        analyze_results=st_analyze_results,
    )

    assert st_anonymize_results.text != ""
    assert st_anonymize_results.text != st_text
    assert "David Johnson" not in st_anonymize_results.text
