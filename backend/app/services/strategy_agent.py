"""
Corporate Misinformation Strategy Agent

Module A: Fake News Input → Strategy Output
- Threat Severity Assessment (0-100 score)
- Public Message Generation (tone-adaptive)
- Recommended Company Actions (severity-based)

Module C: Strategy Assistant Chatbot
- Conversational refinement of responses
- Tone rewrites, media-ready versions
- Monitoring & escalation suggestions
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

import google.generativeai as genai
from dotenv import load_dotenv

from .analysis_engine import analyze_claim

logger = logging.getLogger(__name__)

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash").strip()


# ============================================================================
# MODULE A: FAKE NEWS INPUT → STRATEGY OUTPUT
# ============================================================================

async def assess_threat_severity(misinformation: str) -> Dict[str, Any]:
    """
    Assess threat severity of misinformation.
    
    Returns:
        {
            "threat_score": int (0-100),
            "classification": "Low" | "Medium" | "High" | "Critical",
            "justification": str
        }
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured")
        return {
            "threat_score": 50,
            "classification": "Medium",
            "justification": "AI assessment unavailable - defaulting to Medium threat"
        }
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""Analyze this misinformation claim and assess its threat severity for a company.

Misinformation: {misinformation}

Return ONLY a JSON object (no markdown, no explanations):
{{
    "threat_score": <integer 0-100>,
    "classification": "<Low|Medium|High|Critical>",
    "justification": "<brief explanation using evidence and logic>"
}}

Threat Score Guidelines:
- 0-25 (Low): Minor false claim, minimal potential impact, niche audience
- 26-50 (Medium): Moderate false claim, some potential spread, notable audience
- 51-75 (High): Serious false claim, high potential virality, large audience, brand/reputation risk
- 76-100 (Critical): Severe false claim, imminent viral spread, safety/legal implications, regulatory risk

Classification must match threat_score:
- 0-25 → "Low"
- 26-50 → "Medium"
- 51-75 → "High"
- 76-100 → "Critical"

Be factual and evidence-based. Return ONLY the JSON object."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1024,
            )
        )
        
        text = _extract_text_from_response(response)
        result = _parse_json_response(text)
        
        # Validate and normalize
        threat_score = max(0, min(100, int(result.get("threat_score", 50))))
        
        # Ensure classification matches score
        if threat_score <= 25:
            classification = "Low"
        elif threat_score <= 50:
            classification = "Medium"
        elif threat_score <= 75:
            classification = "High"
        else:
            classification = "Critical"
        
        return {
            "threat_score": threat_score,
            "classification": classification,
            "justification": result.get("justification", "Assessment completed")
        }
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            logger.warning(f"Quota exceeded, using fallback: {e}")
            # Dynamic fallback based on input hash to ensure different outputs for different inputs
            input_hash = hash(misinformation) % 100
            return {
                "threat_score": input_hash,
                "classification": _get_threat_classification(input_hash),
                "justification": "AI assessment unavailable due to quota limits. Fallback: This appears to be a claim requiring attention.",
                "is_fallback": True
            }
            
        logger.error(f"Threat assessment failed: {e}")
        return {
            "threat_score": 50,
            "classification": "Medium",
            "justification": f"Assessment error: {str(e)}",
            "error": str(e)
        }


async def generate_public_message(misinformation: str, threat_score: int, analysis_result: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate public-facing response message.
    
    Args:
        misinformation: The false claim
        threat_score: Threat severity score (0-100)
        analysis_result: Optional fact-check analysis result
    
    Returns:
        {
            "headline": str,
            "message": str,
            "tone": str
        }
    """
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY not configured")
        return {
            "headline": "Clarification Statement",
            "message": "We are aware of recent claims and are reviewing the matter. Official updates will be provided through our verified channels.",
            "tone": "Neutral"
        }
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Determine tone based on threat score
        if threat_score <= 25:
            tone_mode = "Calm, low amplification - simple clarification"
        elif threat_score <= 50:
            tone_mode = "Neutral & clarifying - factual correction"
        elif threat_score <= 75:
            tone_mode = "Firm with factual reinforcement - direct refutation"
        else:
            tone_mode = "Urgent, direct, safety-driven - immediate clarification"
        
        # Build fact-check context if available
        fact_context = ""
        if analysis_result:
            verdict = analysis_result.get("verdict", "")
            confidence = analysis_result.get("confidence", 0)
            sources = analysis_result.get("sources", [])[:3]
            
            fact_context = f"\n\nFact-Check Analysis:\n"
            fact_context += f"- Verdict: {verdict}\n"
            fact_context += f"- Confidence: {confidence}%\n"
            if sources:
                fact_context += f"- Sources: {', '.join(sources[:2])}\n"
        
        prompt = f"""Generate a professional, factual public response to correct misinformation.

Misinformation: {misinformation}
Threat Level: {threat_score}/100 ({_get_threat_classification(threat_score)})
Tone: {tone_mode}
{fact_context}

Requirements:
- Headline: Short, clear clarification title (max 10 words)
- Message: Factual correction that clearly addresses the misinformation
- Be professional, calm, and direct
- Never fabricate numbers or claims
- If data is uncertain, mention requirement for verification
- Provide reassurance to the public
- Keep message under 300 words

Return ONLY a JSON object:
{{
    "headline": "<clarification headline>",
    "message": "<full official response message>",
    "tone": "<actual tone used>"
}}

Return ONLY the JSON, no markdown, no code blocks."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
            )
        )
        
        text = _extract_text_from_response(response)
        result = _parse_json_response(text)
        
        return {
            "headline": result.get("headline", "Clarification Statement"),
            "message": result.get("message", "We are reviewing recent claims and will provide updates through official channels."),
            "tone": result.get("tone", "Professional")
        }
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            logger.warning(f"Quota exceeded, using fallback: {e}")
            return {
                "headline": "Clarification Statement (Fallback)",
                "message": "We are aware of recent claims and are reviewing the matter. Official updates will be provided through our verified channels. (System Note: AI generation unavailable due to quota limits)",
                "tone": "Professional",
                "is_fallback": True
            }

        logger.error(f"Public message generation failed: {e}")
        return {
            "headline": "Clarification Statement",
            "message": "We are aware of recent claims and are reviewing the matter. Official updates will be provided through our verified channels.",
            "tone": "Neutral",
            "error": str(e)
        }


def get_recommended_actions(threat_score: int) -> List[Dict[str, str]]:
    """
    Generate recommended company actions based on threat severity.
    
    Returns:
        List of action dictionaries with "action" and "priority" fields
    """
    actions = []
    
    if threat_score <= 25:
        # LOW
        actions = [
            {"action": "Soft clarification post on social media", "priority": "Low"},
            {"action": "Minimal escalation - monitor reach", "priority": "Low"},
            {"action": "Continued monitoring for 48-72 hours", "priority": "Low"}
        ]
    elif threat_score <= 50:
        # MEDIUM
        actions = [
            {"action": "Publish official response statement", "priority": "Medium"},
            {"action": "Monitor virality and engagement metrics for 48-72 hours", "priority": "Medium"},
            {"action": "Report content to internal PR/communications team", "priority": "Medium"},
            {"action": "Track mentions across platforms", "priority": "Medium"}
        ]
    elif threat_score <= 75:
        # HIGH
        actions = [
            {"action": "Immediate official statement publication", "priority": "High"},
            {"action": "Report to platform moderation teams (Twitter/X, Facebook, etc.)", "priority": "High"},
            {"action": "Active social media tracking and engagement monitoring", "priority": "High"},
            {"action": "Notify internal PR and legal teams", "priority": "High"},
            {"action": "Prepare escalation plan if virality increases", "priority": "Medium"}
        ]
    else:
        # CRITICAL
        actions = [
            {"action": "Emergency clarification post (immediate)", "priority": "Critical"},
            {"action": "Escalate to PR/legal team immediately", "priority": "Critical"},
            {"action": "Prepare and issue press release or media briefing", "priority": "Critical"},
            {"action": "Notify regulatory bodies if applicable", "priority": "Critical"},
            {"action": "Activate crisis communication protocol", "priority": "Critical"},
            {"action": "Monitor all platforms 24/7 for first 48 hours", "priority": "High"}
        ]
    
    return actions


async def generate_strategy_output(misinformation: str) -> Dict[str, Any]:
    """
    Complete Module A: Generate full strategy output from misinformation input.
    
    Returns:
        {
            "threat_assessment": {...},
            "public_message": {...},
            "recommended_actions": [...],
            "export_package": {...}
        }
    """
    # Step 1: Analyze the misinformation claim using fact-check engine
    logger.info(f"Analyzing misinformation claim: {misinformation[:100]}...")
    analysis_result = await analyze_claim(misinformation)
    
    # Step 2: Assess threat severity
    threat_assessment = await assess_threat_severity(misinformation)
    threat_score = threat_assessment["threat_score"]
    
    # Step 3: Generate public message
    public_message = await generate_public_message(misinformation, threat_score, analysis_result)
    
    # Step 4: Get recommended actions
    recommended_actions = get_recommended_actions(threat_score)
    
    # Step 5: Build export package (Module B)
    export_package = {
        "summary": f"Misinformation claim: {misinformation[:200]}",
        "threat_level": threat_assessment["classification"],
        "threat_score": threat_score,
        "public_post": public_message,
        "action_plan": recommended_actions,
        "fact_check_verdict": analysis_result.get("verdict", "Unverified"),
        "fact_check_confidence": analysis_result.get("confidence", 0),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    
    return {
        "threat_assessment": threat_assessment,
        "public_message": public_message,
        "recommended_actions": recommended_actions,
        "export_package": export_package,
        "fact_check": {
            "verdict": analysis_result.get("verdict", "Unverified"),
            "confidence": analysis_result.get("confidence", 0),
            "sources": analysis_result.get("sources", [])[:5]
        }
    }


# ============================================================================
# MODULE C: STRATEGY ASSISTANT CHATBOT
# ============================================================================

async def chatbot_query(
    user_message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Strategy Assistant Chatbot - Module C.
    
    Helps refine responses, suggest improvements, create media-ready versions.
    
    Args:
        user_message: User's query to the chatbot
        context: Optional context (e.g., current strategy output, message draft)
    
    Returns:
        {
            "response": str,
            "suggestions": List[str],
            "action": str | None  # Optional suggested action type
        }
    """
    if not GEMINI_API_KEY:
        return {
            "response": "I'm sorry, the AI assistant is currently unavailable. Please contact your administrator.",
            "suggestions": [],
            "action": None
        }
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Build context if available
        context_str = ""
        if context:
            if "current_message" in context:
                context_str += f"\nCurrent public message draft:\n{context['current_message']}\n"
            if "threat_score" in context:
                context_str += f"\nThreat level: {context['threat_score']}/100\n"
        
        prompt = f"""You are a Corporate Misinformation Strategy Assistant. Help refine public responses, suggest improvements, and guide strategic communication.

User Query: {user_message}
{context_str}

Capabilities:
- Rewrite public messages in different tones (professional, empathetic, urgent)
- Create media-ready versions (PR releases, Twitter/X posts, LinkedIn posts)
- Suggest monitoring & escalation workflows
- Compare multiple response drafts
- Improve wording and phrasing

Rules:
- Stay within misinformation strategy domain
- Never invent facts or statistics
- Be concise and actionable
- If user asks something unrelated, politely redirect to misinformation strategy

Return a JSON object:
{{
    "response": "<your conversational response>",
    "suggestions": ["<suggestion 1>", "<suggestion 2>", ...],
    "action": "<rewrite|compare|escalation|monitoring|none>"
}}

Return ONLY the JSON, no markdown."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=1024,
            )
        )
        
        text = _extract_text_from_response(response)
        result = _parse_json_response(text)
        
        # Validate action
        valid_actions = ["rewrite", "compare", "escalation", "monitoring", "none"]
        action = result.get("action", "none")
        if action not in valid_actions:
            action = "none"
        
        return {
            "response": result.get("response", "I understand. How can I help refine your strategy?"),
            "suggestions": result.get("suggestions", []),
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Chatbot query failed: {e}")
        return {
            "response": "I apologize, but I encountered an error. Please try rephrasing your question or contact support.",
            "suggestions": [],
            "action": None
        }


async def rewrite_message(
    original_message: str,
    target_tone: str,
    target_format: str = "general"
) -> Dict[str, Any]:
    """
    Rewrite a message in a different tone or format.
    
    Args:
        original_message: Original message text
        target_tone: "professional", "empathetic", "urgent", "calm"
        target_format: "general", "twitter", "linkedin", "pr_release"
    
    Returns:
        {
            "rewritten_message": str,
            "format": str,
            "tone": str
        }
    """
    if not GEMINI_API_KEY:
        return {
            "rewritten_message": original_message,
            "format": target_format,
            "tone": target_tone
        }
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        format_guidelines = {
            "twitter": "Twitter/X post - max 280 characters, direct, can use hashtags",
            "linkedin": "LinkedIn post - professional tone, 2-3 paragraphs, can include call-to-action",
            "pr_release": "Press release format - headline, dateline, body paragraphs, boilerplate",
            "general": "General public statement"
        }
        
        guideline = format_guidelines.get(target_format, format_guidelines["general"])
        
        prompt = f"""Rewrite this public message with the specified tone and format.

Original Message:
{original_message}

Target Tone: {target_tone}
Target Format: {target_format} ({guideline})

Requirements:
- Maintain factual accuracy
- Don't invent new information
- Match the requested tone and format
- Keep it professional and appropriate

Return ONLY a JSON object:
{{
    "rewritten_message": "<rewritten message>",
    "format": "{target_format}",
    "tone": "{target_tone}"
}}

Return ONLY the JSON, no markdown."""

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=1024,
            )
        )
        
        text = _extract_text_from_response(response)
        result = _parse_json_response(text)
        
        return {
            "rewritten_message": result.get("rewritten_message", original_message),
            "format": result.get("format", target_format),
            "tone": result.get("tone", target_tone)
        }
        
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Quota exceeded" in error_str:
            return {
                "rewritten_message": f"(Fallback) {original_message}",
                "format": target_format,
                "tone": target_tone,
                "is_fallback": True
            }

        logger.error(f"Message rewrite failed: {e}")
        return {
            "rewritten_message": original_message,
            "format": target_format,
            "tone": target_tone,
            "error": str(e)
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _extract_text_from_response(response) -> str:
    """Extract text from Gemini response."""
    try:
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content'):
                    content = candidate.content
                    if hasattr(content, 'parts'):
                        text_parts = []
                        for part in content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                        if text_parts:
                            return "".join(text_parts)
        
        # Fallback
        if hasattr(response, 'text'):
            return response.text
        
        return str(response)
    except Exception as e:
        logger.error(f"Failed to extract text from response: {e}")
        return ""


def _parse_json_response(text: str) -> Dict[str, Any]:
    """Parse JSON from text response, handling markdown code blocks."""
    try:
        cleaned = text.strip()
        
        # Remove markdown code fences
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        
        # Extract first JSON object
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]
        
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Raw Text causing error: {text}")
        return {}
    except Exception as e:
        logger.error(f"Parse error: {e}")
        logger.error(f"Raw Text causing error: {text}")
        return {}


def _get_threat_classification(score: int) -> str:
    """Get threat classification from score."""
    if score <= 25:
        return "Low"
    elif score <= 50:
        return "Medium"
    elif score <= 75:
        return "High"
    else:
        return "Critical"

