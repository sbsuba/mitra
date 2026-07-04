"""
Mitra Risk Scoring Tests
Outcome-based tests — assert on final scores not internal calls.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from app.agent import calculate_risk_score, get_risk_level, should_escalate_crisis


class TestRiskScoring:

    def test_all_good_signals_produce_zero(self):
        """All positive signals must produce score 0."""
        signals = {"sleep": "good", "energy": "high",
                   "social": "yes", "mood": "good"}
        assert calculate_risk_score(signals) == 0

    def test_all_bad_signals_produce_100(self):
        """All negative signals must produce score 100."""
        signals = {"sleep": "poor", "energy": "low",
                   "social": "no", "mood": "low"}
        assert calculate_risk_score(signals) == 100

    def test_mixed_signals_produce_watch_risk(self):
        """Mixed signals must produce score 26-55."""
        signals = {"sleep": "fair", "energy": "fair",
                   "social": "brief", "mood": "neutral"}
        score = calculate_risk_score(signals)
        assert 26 <= score <= 55

    def test_sleep_poor_contributes_30_points(self):
        """Sleep poor must contribute exactly 30 points."""
        signals = {"sleep": "poor", "energy": "high",
                   "social": "yes", "mood": "good"}
        assert calculate_risk_score(signals) == 30

    def test_social_no_contributes_25_points(self):
        """Social no must contribute exactly 25 points."""
        signals = {"sleep": "good", "energy": "high",
                   "social": "no", "mood": "good"}
        assert calculate_risk_score(signals) == 25

    def test_invalid_signal_raises_value_error(self):
        """Invalid signal values must raise ValueError."""
        signals = {"sleep": "excellent"}
        with pytest.raises(ValueError):
            calculate_risk_score(signals)

    def test_low_risk_level(self):
        """Score 0-25 must return low."""
        assert get_risk_level(0) == "low"
        assert get_risk_level(25) == "low"

    def test_watch_risk_level(self):
        """Score 26-55 must return watch."""
        assert get_risk_level(26) == "watch"
        assert get_risk_level(55) == "watch"

    def test_high_risk_level(self):
        """Score 56-100 must return high."""
        assert get_risk_level(56) == "high"
        assert get_risk_level(100) == "high"
