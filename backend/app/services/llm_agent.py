"""
Clean Gemini-based news verifier.
Returns confidence percentage (0-100) and verdict for news validation.
"""
import asyncio
import json
import logging
import os
from typing import Any, Dict, List

import google.generativeai as genai
from dotenv import load_dotenv
from .fact_checker import check_fact
from .gnews_service import search_gnews

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


async def run_agent_workflow(input_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
	"""
	Main entry point for news verification.
	
	Returns:
		{
			"summary": str,
			"verdict": "Likely True" | "Likely False" | "Uncertain",
			"confidence": float (0-100),
			"evidence": list of dicts with source/confidence/rationale,
			"sources": list of URLs
		}
	"""
	try:
		text = extract_text(input_type, payload)
		
		# First, check Google Fact Check API
		fact_check_result = await asyncio.to_thread(check_fact, text[:500])  # Limit query length
		
		# If no fact-checks found, try GNews for additional context
		gnews_result = None
		if not fact_check_result.get("has_claims"):
			gnews_result = await asyncio.to_thread(search_gnews, text[:200], max_results=3)
		
		api_key = os.getenv("GEMINI_API_KEY", "").strip()
		model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash").strip()
		
		# Handle both "gemini-pro" and "models/gemini-pro" formats
		if not model_name or model_name == "":
			model_name = "gemini-1.5-flash"
		
		if not api_key:
			return _fallback_result("GEMINI_API_KEY not configured", text)
		
		genai.configure(api_key=api_key)
		result = await _verify_with_gemini(model_name, text, fact_check_result, gnews_result)
		return result
		
	except Exception as e:
		logger.exception("Verification failed: %s", e)
		return _fallback_result(str(e), text)


async def _verify_with_gemini(model_name: str, text: str, fact_check_data: Dict[str, Any] = None, gnews_data: Dict[str, Any] = None) -> Dict[str, Any]:
	"""Call Gemini to verify news and return structured result with confidence %."""
	
	def _call_gemini():
		model = genai.GenerativeModel(model_name)
		
		# Build prompt with fact-check context if available
		fact_check_context = ""
		if fact_check_data and fact_check_data.get("has_claims"):
			fact_check_context = f"\n\nGoogle Fact Check Results:\n{fact_check_data.get('summary', '')}\n"
			for claim in fact_check_data.get("claims", [])[:3]:
				fact_check_context += f"- {claim.get('publisher', 'Unknown')}: {claim.get('rating', 'Unrated')} - {claim.get('title', '')}\n"
		
		# Add GNews context if available
		gnews_context = ""
		if gnews_data and gnews_data.get("has_articles"):
			gnews_context = f"\n\nRelated News Articles:\n"
			for article in gnews_data.get("articles", [])[:3]:
				gnews_context += f"- {article.get('source', 'Unknown')}: {article.get('title', '')} ({article.get('url', '')})\n"
		
		prompt = f"""Analyze this news claim and return ONLY a JSON object (no explanations, no markdown).

News: {text}
{fact_check_context}{gnews_context}
Return this exact JSON structure:
{{"summary":"your brief assessment","verdict":"Likely True","confidence":85,"evidence":[{{"source":"source name","confidence":0.9,"rationale":"why"}}],"sources":["url"]}}

Rules:
- verdict MUST be exactly: "Likely True" OR "Likely False" OR "Uncertain"
- confidence is 0-100 integer
- Consider the Google Fact Check results and news articles if provided above
- Keep summary under 200 characters
- Return ONLY the JSON, no backticks, no markdown"""
		
		response = model.generate_content(
			prompt,
			generation_config=genai.types.GenerationConfig(
				temperature=0.0,  # Deterministic output for consistency
				max_output_tokens=2048,
			)
		)
		
		# Extract text from response - handle multi-part responses
		text_parts = []
		
		# Handle multi-part responses by iterating through candidates and parts
		if hasattr(response, 'candidates') and response.candidates:
			for candidate in response.candidates:
				if hasattr(candidate, 'content'):
					content = candidate.content
					if hasattr(content, 'parts'):
						for part in content.parts:
							if hasattr(part, 'text') and part.text:
								text_parts.append(part.text)
		
		if text_parts:
			return "".join(text_parts)
		
		raise ValueError("No text content found in Gemini response")
	
	raw_response = await asyncio.to_thread(_call_gemini)
	result = _parse_response(raw_response, text)
	
	# Add fact-check data to the result
	if fact_check_data and fact_check_data.get("has_claims"):
		result["fact_check"] = fact_check_data
		
		# Add fact-check sources to evidence
		for claim in fact_check_data.get("claims", []):
			if claim.get("url"):
				result["evidence"].append({
					"source": f"Fact Check: {claim.get('publisher', 'Unknown')}",
					"confidence": 0.9,  # Fact-check sources are highly reliable
					"rationale": f"{claim.get('rating', 'Unrated')}: {claim.get('title', '')}",
					"url": claim.get("url")
				})
				if claim.get("url") not in result["sources"]:
					result["sources"].append(claim.get("url"))
	
	# Add GNews data to the result
	if gnews_data and gnews_data.get("has_articles"):
		result["news_articles"] = gnews_data
		
		# Add news article sources to evidence
		for article in gnews_data.get("articles", [])[:3]:
			if article.get("url"):
				result["evidence"].append({
					"source": f"News: {article.get('source', 'Unknown')}",
					"confidence": 0.7,  # News articles have moderate reliability
					"rationale": f"{article.get('title', '')}",
					"url": article.get("url")
				})
				if article.get("url") not in result["sources"]:
					result["sources"].append(article.get("url"))
	
	return result


def _extract_first_json(s: str) -> str:
	"""Return the first complete top-level JSON object substring from s.
	Scans braces while being string/escape aware.
	"""
	i = 0
	n = len(s)
	in_str = False
	esc = False
	start = -1
	depth = 0
	while i < n:
		ch = s[i]
		if in_str:
			if esc:
				esc = False
			elif ch == "\\":
				esc = True
			elif ch == '"':
				in_str = False
		else:
			if ch == '"':
				in_str = True
			elif ch == '{':
				if depth == 0:
					start = i
				depth += 1
			elif ch == '}':
				if depth > 0:
					depth -= 1
					if depth == 0 and start != -1:
						return s[start:i+1]
		i += 1
	raise ValueError("No complete JSON object found")


def _parse_response(raw: str, original_text: str) -> Dict[str, Any]:
	"""Parse Gemini response and ensure proper format with confidence %."""
	
	try:
		cleaned = raw.strip()
		# Remove code fences if present
		if "```" in cleaned:
			cleaned = cleaned.replace("```json", "").replace("```", "")
		# Extract the first complete JSON object robustly
		cleaned = _extract_first_json(cleaned)
		# Parse JSON
		data = json.loads(cleaned)
		
		# Extract and validate fields
		summary = str(data.get("summary", "")).strip()
		verdict = str(data.get("verdict", "Uncertain")).strip()
		
		if verdict not in ["Likely True", "Likely False", "Uncertain"]:
			verdict = "Uncertain"
		
		# Get confidence as 0-100
		confidence_raw = data.get("confidence", 0)
		try:
			confidence = float(confidence_raw)
			confidence = max(0.0, min(100.0, confidence))
		except (TypeError, ValueError):
			confidence = 0.0
		
		# Process evidence
		evidence: List[Dict[str, Any]] = []
		for item in data.get("evidence", []):
			if isinstance(item, dict):
				ev = {
					"source": str(item.get("source", "Unknown")).strip(),
					"confidence": float(item.get("confidence", 0.5)),
					"rationale": str(item.get("rationale", "")).strip()
				}
				if "url" in item:
					ev["url"] = str(item["url"])
				evidence.append(ev)
		
		# Process sources
		sources: List[str] = []
		for s in data.get("sources", []):
			if isinstance(s, str) and s.strip():
				sources.append(s.strip())
		
		return {
			"summary": summary or f"Analysis of: {original_text[:100]}...",
			"verdict": verdict,
			"confidence": confidence,
			"evidence": evidence,
			"sources": sources
		}
		
	except json.JSONDecodeError as e:
		logger.error("JSON parse failed: %s", e)
		logger.error("Raw (first 1000 chars): %s", raw[:1000])
		return {
			"summary": "Verification unavailable: Could not parse model response.",
			"verdict": "Uncertain",
			"confidence": 0.0,
			"evidence": [{
				"source": "System",
				"confidence": 0.0,
				"rationale": "JSON parse error"
			}],
			"sources": []
		}
	except Exception as e:
		logger.exception("Response processing error: %s", e)
		return _fallback_result(str(e), original_text)


def _fallback_result(reason: str, text: str) -> Dict[str, Any]:
	"""Return a safe fallback response."""
	snippet = " ".join(text.strip().split())[:200]
	return {
		"summary": f"Verification unavailable: {reason}. Snippet: {snippet}",
		"verdict": "Uncertain",
		"confidence": 0.0,
		"evidence": [],
		"sources": []
	}


def extract_text(input_type: str, payload: Dict[str, Any]) -> str:
	"""Extract text from input payload."""
	
	if input_type == "text":
		return str(payload.get("text", "")).strip() or "No text provided"
	
	if input_type == "url":
		url = str(payload.get("url", "")).strip()
		if not url:
			return "No URL provided"
		
		try:
			import httpx
			import re
			
			with httpx.Client(timeout=10.0, follow_redirects=True) as client:
				response = client.get(url)
				response.raise_for_status()
				html = response.text
			
			# Strip HTML tags
			text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html, flags=re.I)
			text = re.sub(r"<[^>]+>", " ", text)
			text = re.sub(r"\s+", " ", text).strip()
			
			return f"URL: {url}\n\nContent:\n{text[:3000]}"
			
		except Exception as e:
			logger.warning("URL fetch failed for %s: %s", url, e)
			return f"URL: {url} (could not fetch content)"
	
	if input_type == "image":
		return "Image analysis not implemented"
	
	if input_type == "video":
		return "Video analysis not implemented"
	
	return "Unsupported input type"


