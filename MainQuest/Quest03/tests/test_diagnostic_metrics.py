"""진단 지표가 문자 누락과 위치 오류를 구분하는지 확인한다."""
import unittest
from evaluation.analyze_baseline import detail, summarize, edit_distance

class DiagnosticTests(unittest.TestCase):
    def row(self, prediction, target='ㄱㅏ\nㄴ'):
        return detail({'id':'test','text':'간','prediction':prediction,'target':target,'hit_token_limit':False})

    def test_perfect_and_shifted(self):
        correct=summarize([self.row('ㄱㅏ\nㄴ')])
        shifted=summarize([self.row(' ㄱㅏ\n ㄴ')])
        self.assertEqual(correct['coordinate_f1'],1)
        self.assertEqual(shifted['inventory_f1'],1)
        self.assertEqual(shifted['nonspace_cer'],0)
        self.assertEqual(shifted['exact_grid'],0)
        self.assertLess(shifted['coordinate_f1'],1)

    def test_extra_characters_are_penalized(self):
        result=summarize([self.row('ㄱㅏ\nㄴㄴㄴㄴㄴ')])
        self.assertGreater(result['nonspace_cer'],1)
        self.assertLess(result['inventory_f1'],1)
        self.assertEqual(result['missing'],0)
        self.assertEqual(result['extra'],4)

    def test_empty_and_edit_operations(self):
        result=summarize([self.row('')])
        self.assertEqual(result['nonspace_cer'],1)
        self.assertEqual(result['inventory_f1'],0)
        self.assertEqual(edit_distance('abc','axc'),1)
        self.assertEqual(edit_distance('','abc'),3)

if __name__=='__main__': unittest.main()
