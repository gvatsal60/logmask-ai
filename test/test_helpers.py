from presidio_analyzer import PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine

from helpers import (
    anonymizer_engine,
    anonymize,
    annotate,
    create_ad_hoc_deny_list_recognizer,
    create_ad_hoc_regex_recognizer,
)


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
