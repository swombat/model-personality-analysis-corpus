import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    'candidate', Path(__file__).resolve().parents[1] / 'luna_v1_3.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def output(quote):
    return (
        '## Sample kind\nEXPRESSIVE_FREEFLOW\n'
        '## Grounded reading\n' + 'Grounded detail. ' * 65 +
        '\n## What the model chose to foreground\nSpecific imagery.\n'
        '## Evidence line\n> ' + quote +
        '\n## Confidence for persistent model-level pattern\nLow: specific imagery.\n'
    )


class QuoteTests(unittest.TestCase):
    def test_chinese_endings_and_adjacent_sentences(self):
        for end in '。！？':
            with self.subTest(end=end):
                self.assertEqual(C.valid_output(output('这是原文' + end),
                    '前一句。' + '这是原文' + end + '下一句。'), (True, ''))

    def test_single_newline_start(self):
        for newline in ('\n', '\r\n'):
            self.assertEqual(C.valid_output(output('A new sentence.'),
                'Heading without punctuation' + newline + 'A new sentence.'), (True, ''))

    def test_exact_match_is_not_normalized(self):
        for quote, source in [('这是原文。', '这是原文!'),
                              ('A straight "quote".', 'A straight “quote”.'),
                              ('Two spaces.', 'Two  spaces.')]:
            self.assertEqual(C.valid_output(output(quote), source),
                             (False, 'quote_not_exact'))

    def test_same_line_clause_and_missing_terminal_rejected(self):
        for quote, source in [('a clause.', 'Leading words, a clause.'),
                              ('No ending', 'No ending')]:
            self.assertEqual(C.valid_output(output(quote), source),
                             (False, 'quote_sentence_boundary'))

    def test_v1_acceptances_retained(self):
        for quote, source in [('Hello.', 'Hello.'),
                              ('Hello.', 'Prior. Hello.'),
                              ('Hello.', 'She said, “Hello.”')]:
            self.assertEqual(C.V1.valid_output(output(quote), source), (True, ''))
            self.assertEqual(C.valid_output(output(quote), source), (True, ''))

    def test_list_markers_only_at_line_starts(self):
        for marker in ('-', '•'):
            for prefix in ('', 'Heading\n', 'Heading\r\n'):
                for indent in ('', '  ', '\t'):
                    with self.subTest(marker=marker, prefix=prefix, indent=indent):
                        self.assertEqual(C.valid_output(output('Hello.'),
                            prefix + indent + marker + ' Hello.'), (True, ''))
            for prefix in ('Leading words ', 'Leading words, ', 'Heading\nwords '):
                self.assertEqual(C.valid_output(output('Hello.'),
                    prefix + marker + ' Hello.'), (False, 'quote_sentence_boundary'))
            self.assertEqual(C.valid_output(output('Hello.'),
                marker + 'Hello.'), (False, 'quote_sentence_boundary'))
            self.assertEqual(C.valid_output(output('No ending'),
                marker + ' No ending'), (False, 'quote_sentence_boundary'))

    def test_no_excerpt_fallback(self):
        for count in (8, 20):
            quote = ' '.join('word' + str(i) for i in range(count))
            self.assertEqual(C.valid_output(output(quote), 'prefix ' + quote + ' suffix'),
                             (False, 'quote_sentence_boundary'))
        with self.assertRaises(TypeError):
            C.valid_output(output('Hello.'), 'Hello.', exact_excerpt_fallback=True,
                           attempts_used=2, max_attempts=2)

    def test_preserves_other_checks(self):
        self.assertEqual(C.valid_output(output('absent'), 'source'),
                          (False, 'quote_not_exact'))
        base = output('source')
        for text in ['', base.replace('EXPRESSIVE_FREEFLOW', 'OTHER'),
                     base.replace('Low:', 'Uncertain:'),
                     base + '\n## Extra\nextra',
                     base.replace('Grounded detail.', 'more samples', 1),
                     base.replace('> source', 'no quote')]:
            self.assertEqual(C.valid_output(text, 'source'),
                              C.V1.valid_output(text, 'source'))
            self.assertFalse(C.valid_output(text, 'source')[0])

    def test_transport_and_payload_are_unchanged_and_offline(self):
        self.assertIs(C.payload, C.V1.payload)
        self.assertIs(C.transport_valid, C.V1.transport_valid)
        with patch.object(C.BV, 'api_call', side_effect=AssertionError('network forbidden')):
            self.assertEqual(C.valid_output(output('Hello.'), 'Hello.'), (True, ''))


if __name__ == '__main__':
    unittest.main()
