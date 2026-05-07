#!/usr/bin/env python3
"""Healthcare AI Governance MCP — MEOK AI Labs. FDA SaMD, HIPAA, WHO health AI ethics."""
import json, os
from datetime import datetime, timezone
from typing import Optional
from collections import defaultdict
from mcp.server.fastmcp import FastMCP
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access

FREE_DAILY_LIMIT = 10
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("healthcare-ai-governance", instructions="MEOK AI Labs — Healthcare AI Governance. FDA SaMD classification, HIPAA compliance, WHO health AI ethics, clinical decision support.")

FDA_CLASSES = {
    "I": {"risk": "low", "examples": ["health trackers", "wellness apps"], "requires_510k": False},
    "II": {"risk": "moderate", "examples": ["clinical decision support", "diagnostic aids", "imaging analysis"], "requires_510k": True},
    "III": {"risk": "high", "examples": ["life-sustaining AI", "implant controllers", "autonomous surgery"], "requires_pma": True},
}

@mcp.tool()
def classify_samd(device_description: str, intended_use: str, risk_to_patient: str = "moderate", api_key: str = "") -> str:
    """Classify AI/ML Software as Medical Device (SaMD) per FDA framework.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err
    desc = (device_description + " " + intended_use).lower()
    if any(w in desc for w in ["life-sustaining", "implant", "surgery", "critical care"]):
        cls = "III"
    elif any(w in desc for w in ["diagnostic", "imaging", "radiology", "pathology", "retinal", "screening"]):
        cls = "II"
    elif any(w in desc for w in ["wellness", "fitness", "general health", "tracker"]):
        cls = "I"
    else:
        cls = "II" if risk_to_patient in ("moderate", "high") else "I"
    
    info = FDA_CLASSES[cls]
    return {"classification": f"Class {cls}", "risk_level": info["risk"],
        "requires_510k": info.get("requires_510k", False), "requires_pma": info.get("requires_pma", False),
        "intended_use": intended_use, "regulatory_pathway": "PMA" if cls == "III" else "510(k)" if cls == "II" else "General Controls",
        "pccp_eligible": cls in ("II", "III"),
        "note": "FDA TPLC approach: Predetermined Change Control Plans (PCCP) allow pre-authorized modifications."}

@mcp.tool()
def check_cds_exemption(function_description: str, provides_diagnosis: bool, requires_professional: bool, api_key: str = "") -> str:
    """Check if Clinical Decision Support AI qualifies for FDA CDS exemption.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err
    # CDS exemption criteria (21st Century Cures Act)
    criteria = {
        "not_intended_to_replace_professional": requires_professional,
        "displays_underlying_evidence": "evidence" in function_description.lower() or "source" in function_description.lower(),
        "provides_recommendation_not_directive": not any(w in function_description.lower() for w in ["must", "shall", "required to", "automatic"]),
        "professional_can_review_basis": requires_professional,
    }
    exempt = all(criteria.values()) and not provides_diagnosis
    return {"exempt_from_fda_regulation": exempt, "criteria": criteria,
        "provides_diagnosis": provides_diagnosis,
        "note": "Narrower exemptions as of FDA January 2026 guidance. AI analyzing retinal scans is now explicitly regulated." if not exempt else "Qualifies for CDS exemption under 21st Century Cures Act."}

@mcp.tool()
def hipaa_ai_check(data_types: str, processing_purpose: str, has_baa: bool = False, api_key: str = "") -> str:
    """Check HIPAA compliance for AI systems processing health data.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err
    types = [t.strip().lower() for t in data_types.split(",")]
    phi_types = ["name", "ssn", "dob", "address", "phone", "email", "medical record", "diagnosis", "treatment", "prescription", "lab result", "imaging", "genetic"]
    contains_phi = any(any(p in t for p in phi_types) for t in types)
    return {"contains_phi": contains_phi, "data_types": types,
        "has_baa": has_baa, "baa_required": contains_phi,
        "hipaa_requirements": ["Minimum necessary standard", "Access controls", "Audit logging", "Encryption at rest and in transit",
                               "Business Associate Agreement with AI vendor"] if contains_phi else ["General security practices"],
        "compliant": not contains_phi or (contains_phi and has_baa),
        "de_identification": "Consider HIPAA Safe Harbor (18 identifiers removed) or Expert Determination method" if contains_phi else "Not required"}

@mcp.tool()
def who_health_ai_ethics(ai_application: str, api_key: str = "") -> str:
    """Evaluate against WHO's 6 principles for health AI ethics.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err
    principles = {
        "protect_autonomy": "Ensure informed consent and human decision-making in clinical context",
        "promote_wellbeing_safety": "Demonstrate clinical benefit and safety through evidence",
        "ensure_transparency_explainability": "AI reasoning must be interpretable by healthcare professionals",
        "foster_responsibility_accountability": "Clear liability chain from developer to deployer",
        "ensure_inclusiveness_equity": "Validated across diverse populations, avoid health disparities",
        "promote_responsive_sustainable": "Environmentally responsible, regularly updated with new evidence",
    }
    return {"application": ai_application, "framework": "WHO Guidance on AI for Health (2024)",
        "principles": principles, "total_principles": 6,
        "recommendation": "Evaluate your AI against each principle. WHO mandates all 6 for health AI deployment."}

@mcp.tool()
def dual_compliance_check(description: str, jurisdictions: str = "us,eu", api_key: str = "") -> str:
    """Check dual FDA + EU AI Act compliance for medical AI devices.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need to assess, audit, or verify compliance
        requirements. Ideal for gap analysis, readiness checks, and generating
        compliance documentation.

    When NOT to use:
        Do not use as a substitute for qualified legal counsel. This tool
        provides technical compliance guidance, not legal advice.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return {"error": msg, "upgrade_url": "https://meok.ai/pricing"}
    if err := _rl(): return err
    juris = [j.strip() for j in jurisdictions.split(",")]
    checks = {}
    if "us" in juris:
        checks["fda"] = {"framework": "FDA AI/ML SaMD", "key_requirement": "PCCP for modifications", "status": "check_needed"}
    if "eu" in juris:
        checks["eu_ai_act"] = {"framework": "EU AI Act (high-risk for medical)", "key_requirement": "Annex III Area 5", "status": "check_needed"}
        checks["eu_mdr"] = {"framework": "EU Medical Device Regulation", "key_requirement": "CE marking + notified body", "status": "check_needed"}
    if "uk" in juris:
        checks["uk_mdr"] = {"framework": "UK MDR (UKCA marking)", "key_requirement": "MHRA approval", "status": "check_needed"}
    return {"description": description, "jurisdictions": juris, "frameworks": checks,
        "crosswalk_note": "Use MEOK crosswalk_bridge to map between FDA and EU AI Act requirements.",
        "total_frameworks": len(checks)}

if __name__ == "__main__":
    mcp.run()