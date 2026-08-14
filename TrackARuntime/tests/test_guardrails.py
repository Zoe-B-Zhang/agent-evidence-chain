"""Unit tests for M3 guardrails."""

from __future__ import annotations

import unittest

from m3.guardrails import check_formality, formal_tone_score


class TestGuardrails(unittest.TestCase):
    def test_formal_tone_neutral(self) -> None:
        score = formal_tone_score("The route has been updated. Please review.")
        self.assertAlmostEqual(score, 0.9, places=2)

    def test_formal_tone_hype_words_and_exclamations(self) -> None:
        score = formal_tone_score("Amazing!!! This exciting route is awesome!!!")
        self.assertEqual(score, 0.0)

    def test_check_formality_passes(self) -> None:
        ok, score, msg = check_formality("The route has been updated.", 0.7)
        self.assertTrue(ok)
        self.assertEqual(msg, "ok")

    def test_check_formality_fails(self) -> None:
        ok, score, msg = check_formality("Amazing!!!", 0.7)
        self.assertFalse(ok)
        self.assertIn("formality", msg)


if __name__ == "__main__":
    unittest.main()
