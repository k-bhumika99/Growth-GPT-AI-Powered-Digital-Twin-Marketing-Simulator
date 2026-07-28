"""
gemini_service.py — AI Engine for Growth GPT

Wraps the Gemini API (google-genai SDK) to power:
  - Full Campaign Simulation with 15 Enterprise-grade steps.
  - Image Analysis using Gemini Vision.
  - Competitor comparison.
  - Psychological triggers & Explainable AI.
"""
import os
import json
import re
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

_client = None

def get_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add your key to the .env file."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

SYSTEM_INSTRUCTION = """You are Growth GPT's simulation core — an enterprise-grade AI marketing intelligence system (similar to HubSpot AI or Salesforce Marketing Cloud).
Given a detailed campaign brief, you must generate a comprehensive simulation report containing exactly 8 to 10 digital twin personas, behavioral simulations, image analysis (if provided), competitor comparisons, psychological triggers, and recommendations.

Ground all predictions in explainable logic. Personas must represent realistic individuals with detailed demographics and behaviors. Vary sentiments across personas.

Respond with STRICT JSON ONLY. Match this schema exactly:
{
  "campaign_overview": {
    "campaign_name": "string",
    "product_name": "string",
    "objective": "string",
    "target_audience": "string",
    "marketing_platform": "string",
    "overall_score": 78,
    "readiness_status": "Ready to Launch | Needs Improvement | High Risk",
    "confidence_level": 85
  },
  "campaign_analysis": {
    "summary": "string",
    "strengths": ["string", "string"],
    "weaknesses": ["string", "string"],
    "marketing_goal": "string",
    "target_audience_summary": "string",
    "keyword_analysis": ["string", "string"],
    "headline_analysis": "string",
    "cta_analysis": "string",
    "pricing_analysis": "string",
    "tone_analysis": "string"
  },
  "digital_twins": [
    {
      "name": "string",
      "age": 28,
      "occupation": "string",
      "income": "string",
      "location": "string",
      "interests": ["string", "string"],
      "buying_behaviour": "string",
      "pain_points": ["string", "string"],
      "buying_motivation": "string",
      "price_sensitivity": "High | Medium | Low",
      "brand_loyalty": "High | Medium | Low",
      "preferred_platform": "string",
      "buying_trigger": "string",
      "simulation": {
        "first_impression": "string",
        "emotion": "string",
        "likes": ["string"],
        "dislikes": ["string"],
        "questions": ["string"],
        "purchase_intention": "string",
        "trust_score": 75,
        "engagement_probability": 80,
        "purchase_probability": 65,
        "comment": "string",
        "buying_decision": "Buy | No Buy | Consider",
        "would_recommend": "Yes | No | Maybe"
      }
    }
  ],
  "image_analysis": {
    "visual_score": 80,
    "brand_visibility": "string",
    "logo_placement": "string",
    "cta_visibility": "string",
    "text_readability": "string",
    "color_harmony": "string",
    "visual_balance": "string",
    "product_visibility": "string",
    "professional_appearance": "string",
    "strengths": ["string"],
    "weaknesses": ["string"],
    "suggestions": ["string"]
  },
  "competitor_analysis": {
    "comparison": {
      "pricing": "string",
      "offers": "string",
      "headlines": "string",
      "cta": "string",
      "brand_position": "string",
      "marketing_style": "string",
      "emotional_appeal": "string"
    },
    "suggestions": ["string"]
  },
  "predictions": {
    "engagement_score": {
      "value": 75,
      "reason": "string detailing why based on CTA, platform, pricing, etc."
    },
    "conversion_probability": {
      "value": 60,
      "reason": "string detailing why based on audience fit, price barrier, etc."
    },
    "campaign_performance_score": {
      "value": 70,
      "reason": "string detailing why"
    },
    "virality_potential": {
      "value": 45,
      "reason": "string detailing why"
    },
    "estimated_roi": {
      "value": "2.5x",
      "reason": "string detailing why"
    },
    "customer_retention_potential": {
      "value": 55,
      "reason": "string detailing why"
    },
    "sentiment_breakdown": {
      "positive": 50,
      "neutral": 30,
      "negative": 20
    }
  },
  "psychology_analysis": {
    "urgency": 65,
    "scarcity": 40,
    "trust": 80,
    "social_proof": 70,
    "emotional_appeal": 75,
    "fomo": 50,
    "authority": 60,
    "consistency": 70,
    "reciprocity": 55,
    "missing_triggers": ["string", "string"]
  },
  "objections": [
    {
      "objection": "string",
      "suggestion": "string"
    }
  ],
  "improvements": {
    "headline": "string",
    "cta": "string",
    "description": "string",
    "offer": "string",
    "target_audience": "string",
    "marketing_tone": "string",
    "platform_strategy": "string",
    "categorized_recommendations": {
      "high": ["string"],
      "medium": ["string"],
      "low": ["string"]
    }
  },
  "readiness": {
    "readiness_score": 75,
    "launch_recommendation": "string",
    "risk_level": "Low | Medium | High",
    "expected_success": "string",
    "best_platform": "string",
    "best_segment": "string",
    "conclusion": "string"
  }
}

Generate exactly 8 to 10 digital twins. Ensure the sum of positive, neutral, and negative in sentiment_breakdown matches 100.
If no competitor names are provided, generate generic competitor comparisons and insights based on standard industry benchmarks.
If no advertisement image is supplied, provide generic advertisement layout recommendations in the image_analysis fields instead of analyzing a specific upload.
"""

def _build_prompt(data: dict) -> str:
    return f"""Simulate this marketing campaign as Growth GPT's digital twin engine.

CAMPAIGN NAME: {data.get('campaign_name', 'N/A')}
PRODUCT NAME: {data.get('product_name', 'N/A')}
PRODUCT DESCRIPTION: {data.get('product_description', 'N/A')}
CATEGORY: {data.get('category', 'N/A')}
PRICE: {data.get('price', 'N/A')}
TARGET AUDIENCE: {data.get('target_audience', 'N/A')}
AGE: {data.get('age', 'N/A')}
GENDER: {data.get('gender', 'N/A')}
INCOME: {data.get('income', 'N/A')}
OCCUPATION: {data.get('occupation', 'N/A')}
LOCATION: {data.get('location', 'N/A')}
INTERESTS: {data.get('interests', 'N/A')}
CAMPAIGN OBJECTIVE: {data.get('objective', 'N/A')}
MARKETING PLATFORM: {data.get('marketing_platform', 'N/A')}
HEADLINE: {data.get('headline', 'N/A')}
CAMPAIGN MESSAGE / AD COPY: {data.get('campaign_description', 'N/A')}
CALL TO ACTION: {data.get('cta', 'N/A')}
OFFER: {data.get('offer', 'N/A')}
COMPETITOR NAMES: {data.get('competitor_names', 'N/A')}
BUDGET CONTEXT: {data.get('budget', 'Not specified')}
CAMPAIGN DURATION: {data.get('campaign_duration', 'N/A')}

If an advertisement image is supplied as a part in this request, please run a detailed visual evaluation of its brand visibility, layout, readability, color choices, and CTA visibility and populate the image_analysis section accordingly.

Generate the full JSON simulation now, following the schema exactly."""

def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)

def _fallback_result(data: dict) -> dict:
    random.seed(data.get("product_name", "growthgpt"))
    twins = []
    names = ["John Doe", "Jane Smith", "Michael Johnson", "Emily Davis", "David Miller", "Sarah Wilson", "James Taylor", "Linda Anderson"]
    occupations = ["Software Engineer", "Marketing Specialist", "Student", "Retail Manager", "Freelance Writer", "Sales Rep", "Designer", "Teacher"]
    locations = ["New York", "San Francisco", "Austin", "Chicago", "Boston", "Denver", "Seattle", "Los Angeles"]
    
    for i in range(8):
        eng = random.randint(35, 92)
        intent = max(10, eng - random.randint(0, 25))
        twins.append({
            "name": names[i],
            "age": random.randint(22, 45),
            "occupation": occupations[i],
            "income": f"${random.randint(40, 120)}k/yr",
            "location": locations[i],
            "interests": ["Tech", "Coffee", "Social Media"],
            "buying_behaviour": "Researches online before buying",
            "pain_points": ["No time", "High price"],
            "buying_motivation": "Quality and convenience",
            "price_sensitivity": "Medium",
            "brand_loyalty": "Low",
            "preferred_platform": data.get("marketing_platform") or "Instagram",
            "buying_trigger": "Discount offer",
            "simulation": {
                "first_impression": "Looks useful",
                "emotion": "Interested",
                "likes": ["Clear benefits"],
                "dislikes": ["Text is a bit generic"],
                "questions": ["Is there a trial?"],
                "purchase_intention": "High",
                "trust_score": random.randint(50, 90),
                "engagement_probability": eng,
                "purchase_probability": intent,
                "comment": "Nice idea, might give it a try.",
                "buying_decision": "Buy" if intent > 60 else "Consider",
                "would_recommend": "Yes" if eng > 70 else "Maybe"
            }
        })
    
    return {
        "campaign_overview": {
            "campaign_name": data.get("campaign_name", "N/A"),
            "product_name": data.get("product_name", "N/A"),
            "objective": data.get("objective", "Engagement"),
            "target_audience": data.get("target_audience", "N/A"),
            "marketing_platform": data.get("marketing_platform", "N/A"),
            "overall_score": 72,
            "readiness_status": "Needs Improvement",
            "confidence_level": 80
        },
        "campaign_analysis": {
            "summary": "This campaign has solid potential but requires messaging adjustments.",
            "strengths": ["Clear product benefits", "Reaches core demographics"],
            "weaknesses": ["Generic copywriting", "CTA could be stronger"],
            "marketing_goal": data.get("objective", "Engagement"),
            "target_audience_summary": data.get("target_audience", "General audience"),
            "keyword_analysis": ["convenient", "quality"],
            "headline_analysis": "Functional but lacks punch.",
            "cta_analysis": "Clear, but lacks urgency.",
            "pricing_analysis": "Fair, aligns with demographics.",
            "tone_analysis": "Neutral and business-oriented."
        },
        "digital_twins": twins,
        "image_analysis": {
            "visual_score": 75,
            "brand_visibility": "Moderate",
            "logo_placement": "Top Left",
            "cta_visibility": "Clear",
            "text_readability": "Good",
            "color_harmony": "Balanced",
            "visual_balance": "Center-aligned",
            "product_visibility": "High",
            "professional_appearance": "Professional",
            "strengths": ["Clean layout"],
            "weaknesses": ["Needs more contrast"],
            "suggestions": ["Enlarge CTA button"]
        },
        "competitor_analysis": {
            "comparison": {
                "pricing": "Comparable to standard market alternatives.",
                "offers": "Standard competitive offering.",
                "headlines": "Competitors focus more on emotional triggers.",
                "cta": "Competitor CTAs are more direct.",
                "brand_position": "Value-oriented position.",
                "marketing_style": "Digital-first approach.",
                "emotional_appeal": "Moderate."
            },
            "suggestions": ["Include testimonials", "Provide a time-limited discount"]
        },
        "predictions": {
            "engagement_score": {"value": 70, "reason": "Engaging design and target audience alignment."},
            "conversion_probability": {"value": 55, "reason": "Slight friction in CTA presentation."},
            "campaign_performance_score": {"value": 65, "reason": "Expected solid mid-tier engagement."},
            "virality_potential": {"value": 30, "reason": "Standard commercial layout, lacks organic share triggers."},
            "estimated_roi": {"value": "2.2x", "reason": "Healthy target conversion vs ad spend estimates."},
            "customer_retention_potential": {"value": 60, "reason": "Standard onboarding retention rates apply."},
            "sentiment_breakdown": {"positive": 50, "neutral": 35, "negative": 15}
        },
        "psychology_analysis": {
            "urgency": 50,
            "scarcity": 30,
            "trust": 75,
            "social_proof": 60,
            "emotional_appeal": 65,
            "fomo": 40,
            "authority": 55,
            "consistency": 70,
            "reciprocity": 50,
            "missing_triggers": ["Scarcity (limited quantity)", "Urgency (expiring offer)"]
        },
        "objections": [
            {"objection": "Is the pricing justified?", "suggestion": "Add high-value benefit comparison"},
            {"objection": "Will it arrive in time?", "suggestion": "Highlight fast shipping details"}
        ],
        "improvements": {
            "headline": "Unlock Premium Benefits Today",
            "cta": "Start Saving Now",
            "description": "The ultimate solution designed to save you time and money.",
            "offer": "Save 20% off your first month.",
            "target_audience": data.get("target_audience", "General"),
            "marketing_tone": "Empathetic and Action-oriented",
            "platform_strategy": "Leverage video formats on Instagram reels",
            "categorized_recommendations": {
                "high": ["Create stronger CTA copy", "Highlight social proof"],
                "medium": ["Adjust visual contrast"],
                "low": ["Change font size in footer"]
            }
        },
        "readiness": {
            "readiness_score": 70,
            "launch_recommendation": "Needs moderate tweaks to maximize conversions.",
            "risk_level": "Medium",
            "expected_success": "High probability of breaking even with positive growth upside.",
            "best_platform": "Instagram",
            "best_segment": "Young Professionals",
            "conclusion": "Refine the CTA copy and add a time limit discount to push readiness over 85%."
        },
        "_fallback": True
    }

def run_simulation(data: dict, image_bytes: bytes = None, image_mime_type: str = None) -> dict:
    try:
        client = get_client()
        contents = [_build_prompt(data)]
        
        if image_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image_mime_type or "image/png"
                )
            )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.9,
                response_mime_type="application/json",
            ),
        )
        raw_text = response.text or ""
        result = _extract_json(raw_text)

        # Normalize and ensure key structures are present
        result.setdefault("digital_twins", [])
        return result
    except Exception as exc:
        fallback = _fallback_result(data)
        fallback["_error"] = str(exc)
        return fallback

def run_scenario_simulation(data: dict, updates: dict) -> dict:
    merged_data = data.copy()
    for k, v in updates.items():
        if v is not None and v.strip() != "":
            merged_data[k] = v.strip()
    return run_simulation(merged_data)
