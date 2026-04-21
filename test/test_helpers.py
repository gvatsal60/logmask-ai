import unittest

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine

from helpers import (
    anonymizer_engine,
    anonymize,
    annotate,
    create_ad_hoc_deny_list_recognizer,
    create_ad_hoc_regex_recognizer,
)


class TestCreateAdHocDenyListRecognizer(unittest.TestCase):
    def test_returns_none_for_empty_list(self):
        result = create_ad_hoc_deny_list_recognizer([])
        self.assertIsNone(result)

    def test_returns_none_for_none_input(self):
        result = create_ad_hoc_deny_list_recognizer(None)
        self.assertIsNone(result)

    def test_returns_recognizer_for_valid_list(self):
        from presidio_analyzer import PatternRecognizer
        result = create_ad_hoc_deny_list_recognizer(['John', 'Jane'])
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PatternRecognizer)
        self.assertEqual(result.supported_entities, ['GENERIC_PII'])


class TestCreateAdHocRegexRecognizer(unittest.TestCase):
    def test_returns_none_for_empty_regex(self):
        result = create_ad_hoc_regex_recognizer('', 'EMAIL', 0.5)
        self.assertIsNone(result)

    def test_returns_recognizer_for_valid_regex(self):
        from presidio_analyzer import PatternRecognizer
        result = create_ad_hoc_regex_recognizer(
            r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', 'EMAIL', 0.7
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PatternRecognizer)
        self.assertEqual(result.supported_entities, ['EMAIL'])

    def test_returns_recognizer_with_context(self):
        from presidio_analyzer import PatternRecognizer
        result = create_ad_hoc_regex_recognizer(
            r'\d{3}-\d{2}-\d{4}', 'SSN', 0.8, context=['ssn', 'social security']
        )
        self.assertIsNotNone(result)
        self.assertIsInstance(result, PatternRecognizer)


class TestAnonymizerEngine(unittest.TestCase):
    def test_returns_anonymizer_engine(self):
        engine = anonymizer_engine()
        self.assertIsInstance(engine, AnonymizerEngine)


class TestAnonymize(unittest.TestCase):
    def _make_recognizer_result(self, entity_type, start, end, score=0.85):
        return RecognizerResult(
            entity_type=entity_type, start=start, end=end, score=score
        )

    def test_anonymize_replace_operator(self):
        text = 'My name is John Smith.'
        analyze_results = [self._make_recognizer_result('PERSON', 11, 21)]
        result = anonymize(
            text=text,
            operator='replace',
            analyze_results=analyze_results,
        )
        self.assertIsNotNone(result)
        self.assertNotEqual(result.text, '')
        self.assertNotIn('John Smith', result.text)

    def test_anonymize_mask_operator(self):
        text = 'My name is John Smith.'
        analyze_results = [self._make_recognizer_result('PERSON', 11, 21)]
        result = anonymize(
            text=text,
            operator='mask',
            analyze_results=analyze_results,
            mask_char='*',
            number_of_chars=4,
        )
        self.assertIsNotNone(result)
        self.assertNotEqual(result.text, '')

    def test_anonymize_redact_operator(self):
        text = 'My name is John Smith.'
        analyze_results = [self._make_recognizer_result('PERSON', 11, 21)]
        result = anonymize(
            text=text,
            operator='redact',
            analyze_results=analyze_results,
        )
        self.assertIsNotNone(result)
        self.assertNotIn('John Smith', result.text)

    def test_anonymize_empty_results(self):
        text = 'No PII here.'
        result = anonymize(
            text=text,
            operator='replace',
            analyze_results=[],
        )
        self.assertEqual(result.text, text)

    def test_anonymize_highlight_operator(self):
        text = 'My name is John Smith.'
        analyze_results = [self._make_recognizer_result('PERSON', 11, 21)]
        result = anonymize(
            text=text,
            operator='highlight',
            analyze_results=analyze_results,
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.text, text)
        self.assertTrue(result.items)
        self.assertEqual(len(result.items), len(analyze_results))

    def test_anonymize_synthesize_operator(self):
        text = 'My name is John Smith.'
        analyze_results = [self._make_recognizer_result('PERSON', 11, 21)]
        result = anonymize(
            text=text,
            operator='synthesize',
            analyze_results=analyze_results,
        )
        self.assertIsNotNone(result)
        self.assertNotIn('John Smith', result.text)


class TestAnnotate(unittest.TestCase):
    def _make_recognizer_result(self, entity_type, start, end, score=0.85):
        return RecognizerResult(
            entity_type=entity_type, start=start, end=end, score=score
        )

    def test_annotate_single_entity(self):
        text = 'My name is John Smith.'
        analyze_results = [self._make_recognizer_result('PERSON', 11, 21)]
        tokens = annotate(text=text, analyze_results=analyze_results)
        self.assertIsInstance(tokens, list)
        self.assertTrue(len(tokens) > 0)
        # At least one token should be a tuple (entity, entity_type)
        entity_tokens = [t for t in tokens if isinstance(t, tuple)]
        self.assertTrue(len(entity_tokens) > 0)
        self.assertEqual(entity_tokens[0][1], 'PERSON')

    def test_annotate_no_entities(self):
        text = 'No PII here.'
        tokens = annotate(text=text, analyze_results=[])
        self.assertIsInstance(tokens, list)

    def test_annotate_multiple_entities(self):
        text = 'John Smith lives in New York.'
        analyze_results = [
            self._make_recognizer_result('PERSON', 0, 10),
            self._make_recognizer_result('LOCATION', 20, 28),
        ]
        tokens = annotate(text=text, analyze_results=analyze_results)
        entity_tokens = [t for t in tokens if isinstance(t, tuple)]
        self.assertEqual(len(entity_tokens), 2)


if __name__ == '__main__':
    unittest.main()
