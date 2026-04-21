"""
Test helpers functions.
"""

from presidio_analyzer import PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine

import helpers
from helpers import (
    analyze,
    anonymizer_engine,
    anonymize,
    annotate,
    create_ad_hoc_deny_list_recognizer,
    create_ad_hoc_regex_recognizer,
)
from _const import SAMPLE_TXT


def make_recognizer_result(entity_type, start, end, score=0.85):
    return RecognizerResult(entity_type=entity_type, start=start, end=end, score=score)


# --- create_ad_hoc_deny_list_recognizer ---


def test_deny_list_recognizer_returns_none_for_empty_list():
    assert create_ad_hoc_deny_list_recognizer([]) is None


def test_deny_list_recognizer_returns_none_for_none_input():
    assert create_ad_hoc_deny_list_recognizer(None) is None


def test_deny_list_recognizer_returns_recognizer_for_valid_list():
    result = create_ad_hoc_deny_list_recognizer(['John', 'Jane'])
    assert result is not None
    assert isinstance(result, PatternRecognizer)
    assert result.supported_entities == ['GENERIC_PII']


# --- create_ad_hoc_regex_recognizer ---


def test_regex_recognizer_returns_none_for_empty_regex():
    assert create_ad_hoc_regex_recognizer('', 'EMAIL', 0.5) is None


def test_regex_recognizer_returns_recognizer_for_valid_regex():
    result = create_ad_hoc_regex_recognizer(
        r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', 'EMAIL', 0.7
    )
    assert result is not None
    assert isinstance(result, PatternRecognizer)
    assert result.supported_entities == ['EMAIL']


def test_regex_recognizer_returns_recognizer_with_context():
    result = create_ad_hoc_regex_recognizer(
        r'\d{3}-\d{2}-\d{4}', 'SSN', 0.8, context=['ssn', 'social security']
    )
    assert result is not None
    assert isinstance(result, PatternRecognizer)


# --- anonymizer_engine ---


def test_anonymizer_engine_returns_instance():
    assert isinstance(anonymizer_engine(), AnonymizerEngine)


# --- anonymize ---


def test_anonymize_replace_operator():
    text = 'My name is John Smith.'
    analyze_results = [make_recognizer_result('PERSON', 11, 21)]
    result = anonymize(text=text, operator='replace', analyze_results=analyze_results)
    assert result.text != ''
    assert 'John Smith' not in result.text


def test_anonymize_mask_operator():
    text = 'My name is John Smith.'
    analyze_results = [make_recognizer_result('PERSON', 11, 21)]
    result = anonymize(
        text=text,
        operator='mask',
        analyze_results=analyze_results,
        mask_char='*',
        number_of_chars=4,
    )
    assert result.text != ''


def test_anonymize_redact_operator():
    text = 'My name is John Smith.'
    analyze_results = [make_recognizer_result('PERSON', 11, 21)]
    result = anonymize(text=text, operator='redact', analyze_results=analyze_results)
    assert 'John Smith' not in result.text


def test_anonymize_empty_results():
    text = 'No PII here.'
    result = anonymize(text=text, operator='replace', analyze_results=[])
    assert result.text == text


def test_anonymize_highlight_operator():
    text = 'My name is John Smith.'
    analyze_results = [make_recognizer_result('PERSON', 11, 21)]
    result = anonymize(
        text=text, operator='highlight', analyze_results=analyze_results
    )
    assert result.text == text
    assert result.items
    assert len(result.items) == len(analyze_results)


def test_anonymize_synthesize_operator():
    text = 'My name is John Smith.'
    analyze_results = [make_recognizer_result('PERSON', 11, 21)]
    result = anonymize(text=text, operator='synthesize', analyze_results=analyze_results)
    assert 'John Smith' not in result.text


# --- annotate ---


def test_annotate_single_entity():
    text = 'My name is John Smith.'
    analyze_results = [make_recognizer_result('PERSON', 11, 21)]
    tokens = annotate(text=text, analyze_results=analyze_results)
    assert isinstance(tokens, list)
    entity_tokens = [t for t in tokens if isinstance(t, tuple)]
    assert len(entity_tokens) > 0
    assert entity_tokens[0][1] == 'PERSON'


def test_annotate_no_entities():
    text = 'No PII here.'
    tokens = annotate(text=text, analyze_results=[])
    assert isinstance(tokens, list)


def test_annotate_multiple_entities():
    text = 'John Smith lives in New York.'
    analyze_results = [
        make_recognizer_result('PERSON', 0, 10),
        make_recognizer_result('LOCATION', 20, 28),
    ]
    tokens = annotate(text=text, analyze_results=analyze_results)
    entity_tokens = [t for t in tokens if isinstance(t, tuple)]
    assert len(entity_tokens) == 2


# --- analyze + anonymize integration (monkeypatched) ---


def test_helpers_logic(monkeypatch):
    """
    Test the helpers logic.
    """
    st_model = 'en'
    st_model_package = 'stanza'
    st_ta_key = None
    st_ta_endpoint = None

    analyzer_params = (st_model_package, st_model, st_ta_key, st_ta_endpoint)

    # Read default text
    st_text = SAMPLE_TXT

    name_start = st_text.index('David Johnson')
    name_end = name_start + len('David Johnson')
    fake_analyze_results = [
        RecognizerResult(
            entity_type='PERSON',
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
    monkeypatch.setattr(helpers, 'analyzer_engine', lambda *args, **kwargs: fake_engine)

    # Analyze
    st_analyze_results = analyze.__wrapped__(
        *analyzer_params,
        text=st_text,
        entities='All',
        language='en',
        score_threshold=0.35,
        return_decision_process=True,
        allow_list=[],
        deny_list=[],
    )
    assert len(st_analyze_results) > 0
    assert fake_engine.last_kwargs['entities'] is None
    assert 'deny_list' not in fake_engine.last_kwargs

    # Anonymize
    monkeypatch.setattr(helpers, 'anonymizer_engine', AnonymizerEngine)
    st_anonymize_results = anonymize(
        text=st_text,
        operator='replace',
        mask_char=None,
        number_of_chars=None,
        encrypt_key=None,
        analyze_results=st_analyze_results,
    )

    assert st_anonymize_results.text != ''
    assert st_anonymize_results.text != st_text
    assert 'David Johnson' not in st_anonymize_results.text
