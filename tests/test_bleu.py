import unittest
from FastWrite import bleu

class TestBleu(unittest.TestCase):
    def test_calculate_bleu_identical(self):
        candidate = "This is a test documentation."
        reference = "This is a test documentation."
        score = bleu.calculate_bleu(candidate, reference)
        
        # For identical strings, BLEU should be 1.0 (or close)
        self.assertAlmostEqual(score, 1.0, places=4)

    def test_calculate_bleu_different(self):
        candidate = "Completely different text here."
        reference = "This is a test documentation."
        score = bleu.calculate_bleu(candidate, reference)
        
        # BLEU should be low for completely different texts
        self.assertLess(score, 0.5)

    def test_calculate_bleu_smoothing(self):
        candidate = "This is test."
        reference = "This is a test documentation."
        # Without smoothing it might be 0 due to 4-gram mismatch
        score_no_smooth = bleu.calculate_bleu(candidate, reference)
        score_smooth = bleu.calculate_bleu(candidate, reference, smoothing_method='method1')
        
        self.assertGreaterEqual(score_smooth, score_no_smooth)

if __name__ == '__main__':
    unittest.main()
