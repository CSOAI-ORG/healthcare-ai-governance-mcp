"""Functional tests for Healthcare AI Governance MCP Server tools.

Tests SaMD classification, CDS exemption, HIPAA-AI checks, WHO ethics,
and dual compliance. No external API calls.
"""
import json
import os
import sys
from unittest.mock import MagicMock

_mock_mcp_module = MagicMock()

class _MockFastMCP:
    def __init__(self, name="", **kwargs):
        self.name = name

    def tool(self):
        def decorator(fn):
            return fn
        return decorator

_mock_mcp_module.FastMCP = _MockFastMCP
sys.modules["mcp"] = MagicMock()
sys.modules["mcp.server"] = MagicMock()
sys.modules["mcp.server.fastmcp"] = _mock_mcp_module

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("MEOK_API_KEY", None)

import server as srv  # noqa: E402
import pytest  # noqa: E402
from unittest.mock import patch, MagicMock  # noqa: E402


@pytest.fixture(autouse=True)
def reset_state():
    srv._usage.clear()
    yield
    srv._usage.clear()


@pytest.fixture(autouse=True)
def bypass_auth_and_rate_limit():
    mock_check = MagicMock(return_value=(True, "OK", "community"))
    with patch.object(srv, "check_access", mock_check), \
         patch.object(srv, "_rl", return_value=None):
        yield


class TestMcpRegistration:
    def test_mcp_object_exists(self):
        assert hasattr(srv, "mcp")

    def test_all_tools_callable(self):
        tool_names = [
            "classify_samd", "check_cds_exemption",
            "hipaa_ai_check", "who_health_ai_ethics",
            "dual_compliance_check",
        ]
        for name in tool_names:
            assert callable(getattr(srv, name)), f"Tool not callable: {name}"


class TestKnowledgeBase:
    def test_fda_classes_defined(self):
        assert "I" in srv.FDA_CLASSES
        assert "II" in srv.FDA_CLASSES
        assert "III" in srv.FDA_CLASSES
        assert srv.FDA_CLASSES["I"]["risk"] == "low"
        assert srv.FDA_CLASSES["II"]["risk"] == "moderate"
        assert srv.FDA_CLASSES["III"]["risk"] == "high"


class TestClassifySamd:
    def test_class_iii_life_sustaining(self):
        result = srv.classify_samd("Life-sustaining AI for critical care", "ICU monitoring")
        assert result["classification"] == "Class III"
        assert result["risk_level"] == "high"
        assert result["requires_pma"] is True

    def test_class_ii_diagnostic(self):
        result = srv.classify_samd("AI diagnostic imaging tool", "Radiology screening")
        assert result["classification"] == "Class II"
        assert result["requires_510k"] is True

    def test_class_i_wellness(self):
        result = srv.classify_samd("Wellness fitness tracker app", "General health tracking")
        assert result["classification"] == "Class I"
        assert result["risk_level"] == "low"

    def test_default_class_ii_for_moderate_risk(self):
        result = srv.classify_samd("AI scheduling assistant", "Operational tool", risk_to_patient="moderate")
        assert result["classification"] == "Class II"

    def test_pccp_eligibility(self):
        result = srv.classify_samd("AI diagnostic", "Clinical decision support")
        assert "pccp_eligible" in result

    def test_intended_use_preserved(self):
        result = srv.classify_samd("Some device", "Cardiac arrhythmia detection")
        assert result["intended_use"] == "Cardiac arrhythmia detection"


class TestCheckCdsExemption:
    def test_exempt_cds(self):
        result = srv.check_cds_exemption(
            "Evidence-based clinical decision support tool that provides recommendations",
            provides_diagnosis=False, requires_professional=True,
        )
        assert result["exempt_from_fda_regulation"] is True

    def test_not_exempt_provides_diagnosis(self):
        result = srv.check_cds_exemption(
            "AI that provides diagnosis evidence",
            provides_diagnosis=True, requires_professional=True,
        )
        assert result["exempt_from_fda_regulation"] is False

    def test_not_exempt_autonomous(self):
        result = srv.check_cds_exemption(
            "AI must make automatic decisions without oversight",
            provides_diagnosis=False, requires_professional=False,
        )
        assert result["exempt_from_fda_regulation"] is False

    def test_criteria_keys_present(self):
        result = srv.check_cds_exemption(
            "Decision support with evidence sources",
            provides_diagnosis=False, requires_professional=True,
        )
        assert "criteria" in result
        criteria = result["criteria"]
        assert "not_intended_to_replace_professional" in criteria
        assert "provides_recommendation_not_directive" in criteria


class TestHipaaAiCheck:
    def test_phi_detected(self):
        result = srv.hipaa_ai_check("name, ssn, diagnosis", "Clinical analysis")
        assert result["contains_phi"] is True
        assert result["baa_required"] is True

    def test_no_phi(self):
        result = srv.hipaa_ai_check("aggregate statistics, de-identified data", "Research")
        assert result["contains_phi"] is False
        assert result["baa_required"] is False

    def test_phi_with_baa_compliant(self):
        result = srv.hipaa_ai_check(
            "patient names, medical records", "Healthcare processing",
            has_baa=True,
        )
        assert result["contains_phi"] is True
        assert result["compliant"] is True

    def test_phi_without_baa_non_compliant(self):
        result = srv.hipaa_ai_check(
            "patient names, diagnosis", "AI processing", has_baa=False,
        )
        assert result["compliant"] is False

    def test_hipaa_requirements_listed(self):
        result = srv.hipaa_ai_check("ssn, medical records", "Processing", has_baa=True)
        assert "hipaa_requirements" in result
        assert len(result["hipaa_requirements"]) > 0


class TestWhoHealthAiEthics:
    def test_six_principles(self):
        result = srv.who_health_ai_ethics("AI diagnostic tool for rural healthcare")
        assert result["total_principles"] == 6
        assert "principles" in result
        assert "protect_autonomy" in result["principles"]

    def test_application_preserved(self):
        result = srv.who_health_ai_ethics("Clinical decision support")
        assert result["application"] == "Clinical decision support"

    def test_framework_reference(self):
        result = srv.who_health_ai_ethics("Test app")
        assert "WHO" in result["framework"]


class TestDualComplianceCheck:
    def test_us_and_eu(self):
        result = srv.dual_compliance_check("AI diagnostic device", jurisdictions="us,eu")
        assert "fda" in result["frameworks"]
        assert "eu_ai_act" in result["frameworks"]
        assert "eu_mdr" in result["frameworks"]

    def test_us_only(self):
        result = srv.dual_compliance_check("AI device", jurisdictions="us")
        assert "fda" in result["frameworks"]
        assert "eu_ai_act" not in result["frameworks"]

    def test_uk_jurisdiction(self):
        result = srv.dual_compliance_check("Device", jurisdictions="uk")
        assert "uk_mdr" in result["frameworks"]

    def test_total_frameworks_count(self):
        result = srv.dual_compliance_check("Device", jurisdictions="us,eu,uk")
        assert result["total_frameworks"] == 4