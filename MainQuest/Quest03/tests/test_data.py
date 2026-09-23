import collections
import unittest
from pathlib import Path
from jamo.core import read_jsonl,render
from demo.app import check_input

class DatasetTests(unittest.TestCase):
    def test_no_split_leakage_and_annotations_match(self):
        paths=['data/train_reviewed.jsonl','data/validation.jsonl','data/test.jsonl']
        if not all(Path(p).exists() for p in paths):
            self.skipTest('Main dataset not present in the pilot package')
        seen_text=set();seen_ids=set();seen_groups=set()
        for path in paths:
            rows=read_jsonl(path)
            texts={r['text'] for r in rows}; ids={r['id'] for r in rows};groups={r['group_id'] for r in rows}
            self.assertEqual(len(texts),len(rows));self.assertFalse(texts & seen_text)
            self.assertFalse(ids & seen_ids);self.assertFalse(groups & seen_groups)
            seen_text |= texts;seen_ids |= ids;seen_groups |= groups
            for row in rows:
                self.assertEqual(check_input(row['text']),row['text'])
                self.assertEqual(render(row['aux_points']),row['target'])
                self.assertEqual(row['annotation_source'],'synthetic_coordinates')
                self.assertTrue(row['review_approved'])

    def test_demo_rejects_unsupported_without_replacing_output(self):
        for text in ['외국','hello','두\n줄',' 가나다']:
            with self.assertRaises(ValueError):check_input(text)

if __name__=='__main__':
    unittest.main()
