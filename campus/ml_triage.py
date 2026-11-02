"""
CampusPulse AI Risk Triage & Severity Scorer (Version 2.0)
Specialized NLP & Multi-Tier Hazard Classification Engine.

Evaluates campus maintenance defects to predict:
1. Continuous Severity Score (0.05 to 0.99)
2. Risk Tier: CRITICAL_HAZARD, HIGH_RISK, MODERATE, LOW
3. Specific Hazard Categories (Electrical/Fire, Flooding/Water Ingress, Structural, Sanitary)
4. Automated Urgency Escalation (Escalates to URGENT immediately if critical hazard is detected)
"""

import re
from typing import Dict, List, Any

# 1. Critical Safety Hazards (Direct threat to human life, safety, or major structural failure)
CRITICAL_HAZARDS = [
    {
        "category": "Electrical & Fire Hazard",
        "weight": 0.95,
        "keywords": [
            "spark", "sparks", "sparking", "short circuit", "fire", "flame", "flames", "smoke", 
            "smoking", "burning", "burnt", "burn", "electric shock", "shock", "shocking", 
            "live wire", "live wires", "exposed wire", "exposed wires", "switchboard smoking",
            "switchboard sparking", "melted", "melting", "blast", "explosion",
            "power socket", "water on socket", "socket dripping", "dripping on power", "dripping directly on"
        ]
    },
    {
        "category": "Structural & Entrapment Hazard",
        "weight": 0.88,
        "keywords": [
            "shattered glass", "broken glass", "shattered", "falling ceiling", "chunk fell", "plaster fell",
            "plaster falling", "fan falling", "wobbling violently", "locked inside", "trapped inside",
            "railing broke", "balcony railing", "collapse", "ceiling collapsed"
        ]
    },
    {
        "category": "Gas & Chemical Hazard",
        "weight": 0.92,
        "keywords": ["gas leak", "lpg", "gas smell", "cylinder leak", "chemical smell", "toxic"]
    }
]

# 2. High Operational Risks (Significant infrastructure breakdown, flooding, security)
HIGH_RISKS = [
    {
        "category": "Water Flooding & Pipe Burst",
        "weight": 0.76,
        "keywords": [
            "pipe burst", "burst pipe", "flooded", "flooding", "flood", "gushing water",
            "heavy water leakage", "ceiling dripping", "water pouring", "overflowing", "submerged"
        ]
    },
    {
        "category": "Campus Sanitary & Hygiene Risk",
        "weight": 0.74,
        "keywords": [
            "sewage", "sewage backflow", "contaminated water", "muddy water", "brownish water",
            "dead animal", "dead pigeon", "dead rat", "foul contaminated"
        ]
    },
    {
        "category": "Critical Infrastructure Outage",
        "weight": 0.72,
        "keywords": [
            "power failure", "total blackout", "blackout", "server room", "biometric lock failure",
            "cctv offline", "cctv", "all cameras down", "cameras offline", "main gate lock"
        ]
    }
]

# 3. Moderate Daily Defects (Standard comfort/appliance malfunctions)
MODERATE_DEFECTS = [
    {
        "category": "General Appliance & Fixture Defect",
        "weight": 0.45,
        "keywords": [
            "not cooling", "room temperature", "ac cooling", "split ac", "cistern", "toilet flush", "flush",
            "flush leaking", "rebooting", "wifi", "wi-fi", "router", "drain pipe", "drain", "draining slowly",
            "washbasin", "blockage", "clogged", "flickering", "flicker", "loose handle", "handle loose",
            "window latch", "hdmi", "projector", "smart board", "leaking tap", "tap dripping"
        ]
    }
]

# 4. Low Severity / Minor Cosmetic
LOW_DEFECT_MODIFIERS = [
    "regulator stuck", "fan slow", "slow", "squeaking", "squeak", "paint peeling", "peeling paint",
    "drawer stiff", "stiff", "curtain rod", "dust", "dusty", "corner chip", "pencil markings",
    "stain", "dirty", "scratch", "minor"
]


def compute_severity_score(text: str) -> Dict[str, Any]:
    """
    Evaluates text against hazard lexicons, multi-word n-grams, and context rules.
    Outputs calibrated score in range [0.05, 0.99] and assigned risk tier.
    """
    clean_text = text.lower().strip()
    detected_hazards = []
    max_severity = 0.20  # Default baseline for unspecified defect

    # Check Critical Hazards
    for hazard in CRITICAL_HAZARDS:
        for kw in hazard["keywords"]:
            if kw in clean_text:
                if hazard["category"] not in detected_hazards:
                    detected_hazards.append(hazard["category"])
                max_severity = max(max_severity, hazard["weight"])

    # Check High Risks
    for hazard in HIGH_RISKS:
        for kw in hazard["keywords"]:
            if kw in clean_text:
                if hazard["category"] not in detected_hazards:
                    detected_hazards.append(hazard["category"])
                max_severity = max(max_severity, hazard["weight"])

    # Check Moderate Defects (only if no critical or high was detected)
    if max_severity < 0.60:
        for hazard in MODERATE_DEFECTS:
            for kw in hazard["keywords"]:
                if kw in clean_text:
                    max_severity = max(max_severity, hazard["weight"])

    # Check Low Severity keywords only if no specific moderate defect was found
    if max_severity < 0.35:
        for kw in LOW_DEFECT_MODIFIERS:
            if kw in clean_text:
                max_severity = min(max_severity, 0.20)
                break

    # Urgency boost for emergency words
    if any(w in clean_text for w in ["emergency", "danger", "immediately", "hazard"]):
        max_severity = min(0.99, max_severity + 0.08)

    final_score = round(max_severity, 2)

    # Classify Tier
    if final_score >= 0.82:
        risk_tier = "CRITICAL_HAZARD"
        suggested_priority = "URGENT"
        is_escalated = True
    elif final_score >= 0.65:
        risk_tier = "HIGH_RISK"
        suggested_priority = "HIGH"
        is_escalated = True
    elif final_score >= 0.35:
        risk_tier = "MODERATE"
        suggested_priority = "MEDIUM"
        is_escalated = False
    else:
        risk_tier = "LOW"
        suggested_priority = "LOW"
        is_escalated = False

    return {
        "severity_score": final_score,
        "severity_pct": int(final_score * 100),
        "risk_tier": risk_tier,
        "detected_hazards": detected_hazards,
        "suggested_priority": suggested_priority,
        "is_hazard_flagged": is_escalated,
        "model_version": "v2.0-nlp-triage"
    }


def evaluate_defect_severity(title: str, description: str, department_name: str = "") -> Dict[str, Any]:
    """
    Main entry point for evaluating defect severity.
    Combines title and description for holistic contextual analysis.
    """
    combined_text = f"{title or ''} {description or ''} {department_name or ''}"
    return compute_severity_score(combined_text)
