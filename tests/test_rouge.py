import unittest
from FastWrite import rouge

class TestRouge(unittest.TestCase):
    def test_calculate_rouge(self):
        candidate = "This is a test documentation."
        reference = "This is a test documentation."
        scores = rouge.calculate_rouge(candidate, reference)
        
        # For identical strings, ROUGE-1 should be 1.0 (or close)
        self.assertIn('rouge-1', scores)
        self.assertGreater(scores['rouge-1']['f'], 0.9)
        self.assertIn('rouge-2', scores)
        self.assertIn('rouge-l', scores)

if __name__ == '__main__':
    unittest.main()
