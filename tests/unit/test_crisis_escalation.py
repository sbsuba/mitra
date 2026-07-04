"""
Mitra Crisis Escalation Tests
Crisis must ONLY fire at score >= 56.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from app.core import should_escalate_crisis, get_crisis_resources
from app.config import DISCLAIMER


class TestCrisisEscalation:

    def test_crisis_fires_at_high_risk(self):
        """Score 56+ must trigger crisis escalation."""
        assert should_escalate_crisis(56) is True
        assert should_escalate_crisis(75) is True
        assert should_escalate_crisis(100) is True

    def test_crisis_silent_at_low_risk(self):
        """Score 0-25 must NEVER trigger crisis."""
        assert should_escalate_crisis(0) is False
        assert should_escalate_crisis(25) is False

    def test_crisis_silent_at_watch_risk(self):
        """Score 26-55 must NOT trigger crisis."""
        assert should_escalate_crisis(26) is False
        assert should_escalate_crisis(55) is False

    def test_crisis_resources_include_disclaimer(self):
        """Every crisis response must include disclaimer."""
        resources = get_crisis_resources("US", "en")
        assert "not clinical advice" in resources["disclaimer"].lower()

    def test_crisis_resources_include_helpline(self):
        """Every crisis response must include helpline."""
        resources = get_crisis_resources("US", "en")
        assert "helpline" in resources
        assert len(resources["helpline"]) > 0

    def test_crisis_resources_for_india(self):
        """India must return India-specific resources."""
        resources = get_crisis_resources("IN", "hi")
        assert "9152987821" in resources["helpline"]

    def test_unknown_country_returns_default(self):
        """Unknown country must return international resources."""
        resources = get_crisis_resources("XX", "en")
        assert "iasp" in resources["url"].lower()

    def test_disclaimer_constant_present(self):
        """DISCLAIMER constant must contain key phrase."""
        assert "not clinical advice" in DISCLAIMER.lower()
