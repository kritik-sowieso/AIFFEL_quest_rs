import unittest
from jamo.core import annotate, canonical, decompose, render, score, validate_input

class AnnotationTests(unittest.TestCase):
    def test_unicode_boundaries(self):
        self.assertEqual(decompose('가'), ('ㄱ','ㅏ',''))
        self.assertEqual(decompose('힣'), ('ㅎ','ㅣ','ㅎ'))
        self.assertEqual(decompose('강'), ('ㄱ','ㅏ','ㅇ'))
        self.assertEqual(decompose('오늘'[1]), ('ㄴ','ㅡ','ㄹ'))

    def test_name_has_correct_jamo_and_positions(self):
        p = annotate('강지수')
        self.assertEqual(render(p), 'ㄱㅏ ㅈㅣ ㅅ\nㅇ     ㅜ')
        self.assertEqual(len(p), 7)

    def test_duplicate_and_shift_are_errors(self):
        gold = render(annotate('강지수'))
        self.assertEqual(score(gold, gold)['exact_grid'], 1)
        self.assertEqual(score(gold+'ㅇ', gold)['extra'], 1)
        shifted = gold.replace('\nㅇ', '\n ㅇ')
        self.assertEqual(score(shifted, gold)['character_inventory'], 1)
        self.assertEqual(score(shifted, gold)['exact_grid'], 0)

    def test_whitespace_and_commentary(self):
        self.assertEqual(canonical('ㄱㅏ  \r\nㅇ  '), 'ㄱㅏ\nㅇ')
        self.assertNotEqual(canonical(' ㄱㅏ\nㅇ'), 'ㄱㅏ\nㅇ')
        self.assertEqual(score('```\nㄱㅏ\n```','ㄱㅏ')['exact_grid'], 0)

    def test_scope_validation(self):
        for text in ('', 'abc', '왜', '한글\n두줄', ' 한글'):
            with self.assertRaises(ValueError):
                validate_input(text)

if __name__ == '__main__':
    unittest.main()
