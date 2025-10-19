import asyncio
import os
from typing import Any, Dict, List

import httpx
import google.generativeai as genai

from .vector_store import upsert_embeddings, embed_texts
from .graph_service import write_entities_and_relationships
from .db import create_analysis_record
from .ws_logger import send_ws_log
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_SENTIMENT_URL = os.getenv(
    "HF_SENTIMENT_URL",
    "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment",
)

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


async def fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL."""
    await send_ws_log("INFO", "Starting URL fetch", {"url": url})
    print(f"\n🌐 [URL FETCH] Starting to fetch: {url}")
    try:
        from bs4 import BeautifulSoup
        
        async with httpx.AsyncClient(
            timeout=30, 
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        ) as client:
            await send_ws_log("DEBUG", "Making HTTP request", {"url": url})
            print(f"📡 [URL FETCH] Making HTTP request...")
            response = await client.get(url)
            response.raise_for_status()
            await send_ws_log("DEBUG", "Got HTTP response", {"status_code": response.status_code, "size": len(response.text)})
            print(f"✅ [URL FETCH] Got response: {response.status_code}, size: {len(response.text)} chars")
            
            # Extract text using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and other non-content tags
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
                tag.decompose()
            
            # Try to find main content area first
            main_content = soup.find('article') or soup.find('main') or soup.find('body')
            
            if main_content:
                # Extract text from paragraphs and headings
                text_elements = []
                
                # Get title
                title = soup.find('h1')
                if title:
                    text_elements.append(title.get_text(strip=True))
                
                # Get all paragraphs and headings from main content
                for element in main_content.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = element.get_text(strip=True)
                    if len(text) > 20:  # Filter out very short snippets
                        text_elements.append(text)
                
                content = '\n\n'.join(text_elements)
            else:
                content = soup.get_text(separator='\n', strip=True)
            
            # Clean up extra whitespace
            content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
            
            # Limit to first 8000 characters for analysis
            final_content = content[:8000] if len(content) > 8000 else content
            await send_ws_log("INFO", "Extracted text content", {"chars": len(final_content)})
            print(f"✅ [URL FETCH] Extracted {len(final_content)} chars of text content")
            return final_content
            
    except Exception as e:
        await send_ws_log("ERROR", "URL fetch failed", {"error": str(e)})
        print(f"❌ [URL FETCH] Error: {str(e)}")
        return f"Failed to fetch URL content: {str(e)}"


async def call_gemini_analyze(text: str, source_url: str = None) -> Dict[str, Any]:
    """Real Gemini API integration for misinformation detection and credibility analysis."""
    await send_ws_log("INFO", "Starting Gemini analysis", {"text_chars": len(text)})
    print(f"\n🤖 [GEMINI] Starting AI analysis (text length: {len(text)} chars)...")

    if not GEMINI_API_KEY:
        await send_ws_log("ERROR", "Gemini API key not configured")
        print("❌ [GEMINI] API key not configured!")
        return {
            "summary": "Gemini API not configured. Cannot analyze content.",
            "verdict": "Unknown",
            "confidence": 0.0,
            "reasoning": "API key missing",
            "evidence_sources": [],
        }

    try:
        await send_ws_log("DEBUG", "Invoking Gemini model")
        print(f"🔑 [GEMINI] API key found, creating model...")
        model = genai.GenerativeModel('gemini-2.5-flash')

        source_info = f"\n\nSource URL: {source_url}" if source_url else ""

        prompt = f"""You are an expert misinformation detection AI. Analyze the following content for credibility, bias, and potential misinformation.

Content to analyze:
{text}
{source_info}

Provide your analysis in the following format:

VERDICT: [Choose one: "Likely True" / "Likely False" / "Misleading" / "Uncertain" / "Satire"]

CONFIDENCE: [0.0 to 1.0]

SUMMARY: [2-3 sentence summary of the main claims]

REASONING: [Detailed explanation of why you reached this verdict, including:
- Factual accuracy assessment
- Source credibility indicators
- Potential bias or manipulation
- Red flags or supporting evidence
- Cross-verification suggestions]

EVIDENCE_SOURCES: [List 2-4 suggested reputable sources to verify these claims, one per line]

Keep your response factual, objective, and actionable."""

        await send_ws_log("DEBUG", "Sending prompt to Gemini AI", {"prompt_length": len(prompt)})
        print(f"📤 [GEMINI] Sending prompt to Gemini AI...")

        response = model.generate_content(prompt)
        text_response = response.text

        await send_ws_log("INFO", "Received Gemini response", {"chars": len(text_response)})
        print(f"✅ [GEMINI] Got response from AI ({len(text_response)} chars)")
        await send_ws_log("DEBUG", "Parsing Gemini response")
        print(f"📝 [GEMINI] Parsing structured response...")

        # Parse the structured response
        verdict = "Uncertain"
        confidence = 0.5
        summary = ""
        reasoning = ""
        evidence_sources = []

        lines = text_response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith('VERDICT:'):
                verdict = line.replace('VERDICT:', '').strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.replace('CONFIDENCE:', '').strip())
                except Exception:
                    confidence = 0.5
            elif line.startswith('SUMMARY:'):
                current_section = 'summary'
                summary = line.replace('SUMMARY:', '').strip()
            elif line.startswith('REASONING:'):
                current_section = 'reasoning'
                reasoning = line.replace('REASONING:', '').strip()
            elif line.startswith('EVIDENCE_SOURCES:'):
                current_section = 'evidence'
            elif line and current_section == 'summary' and not any(line.startswith(x) for x in ['VERDICT:', 'CONFIDENCE:', 'REASONING:', 'EVIDENCE_SOURCES:']):
                summary += ' ' + line
            elif line and current_section == 'reasoning' and not any(line.startswith(x) for x in ['VERDICT:', 'CONFIDENCE:', 'SUMMARY:', 'EVIDENCE_SOURCES:']):
                reasoning += ' ' + line
            elif line and current_section == 'evidence' and (line.startswith(('-', '*', '•')) or (line and not line.startswith(('VERDICT:', 'CONFIDENCE:', 'SUMMARY:', 'REASONING:')))):
                evidence_sources.append(line.lstrip('-*• '))

        result = {
            "summary": summary.strip() or text_response[:200],
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning.strip() or "Analysis completed",
            "evidence_sources": evidence_sources[:4] if evidence_sources else ["factcheck.org", "snopes.com", "politifact.com"],
        }

        await send_ws_log("INFO", "Gemini analysis complete", {"verdict": verdict, "confidence": confidence})
        print(f"✅ [GEMINI] Analysis complete - Verdict: {verdict}, Confidence: {confidence}")
        return result

    except Exception as e:
        await send_ws_log("ERROR", "Gemini analysis error", {"error": str(e)})
        print(f"❌ [GEMINI] Error during analysis: {str(e)}")
        return {
            "summary": f"Analysis error: {str(e)}",
            "verdict": "Unknown",
            "confidence": 0.0,
            "reasoning": "Failed to complete analysis",
            "evidence_sources": [],
        }


async def call_hf_sentiment(text: str) -> Dict[str, Any]:
    await send_ws_log("INFO", "Starting sentiment analysis", {"text_chars": len(text)})
    print(f"\n💭 [SENTIMENT] Analyzing sentiment (text length: {len(text)} chars)...")
    headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACEHUB_API_TOKEN', '')}"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(HF_SENTIMENT_URL, headers=headers, json={"inputs": text})
            res.raise_for_status()
            data = res.json()
            await send_ws_log("INFO", "Sentiment analysis result", {"result_preview": str(data)[:200]})
            print(f"✅ [SENTIMENT] Got sentiment result: {data}")
            return {"raw": data}
    except Exception as e:
        await send_ws_log("WARN", "Sentiment analysis failed", {"error": str(e)})
        print(f"⚠️ [SENTIMENT] Using default sentiment due to error: {str(e)}")
        return {"raw": [{"label": "NEUTRAL", "score": 0.5}]}


async def run_agent_workflow(input_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Implements the Scout → Verify → Synthesize → Respond workflow for misinformation detection.

    - Scout: parse input, extract/fetch text content
    - Verify: run sentiment analysis, generate embeddings, store in vector DB and graph
    - Synthesize: deep analysis with Gemini for credibility assessment
    - Respond: return structured verification result with evidence
    """
    import time
    start_time = time.time()
    await send_ws_log("INFO", "Workflow started", {"type": input_type})
    print(f"\n{'='*80}")
    print(f"🚀 [WORKFLOW] Starting agent workflow - Type: {input_type}")
    print(f"{'='*80}")

    # Scout: Extract or fetch content
    await send_ws_log("DEBUG", "SCOUT - Extracting content")
    print(f"\n📍 [STEP 1/5] SCOUT - Extracting content...")
    text = ""
    source_url = None
    
    if input_type == "url":
        source_url = payload.get("url", "")
        print(f"🔗 [SCOUT] URL provided: {source_url}")
        await send_ws_log("DEBUG", "SCOUT - fetching URL", {"url": source_url})
        text = await fetch_url_content(source_url)
    elif input_type == "text":
        text = str(payload.get("text", "")).strip() or "No text provided"
        print(f"📝 [SCOUT] Text provided ({len(text)} chars)")
    elif input_type == "image":
        text = "Image analysis not yet implemented"
        print(f"🖼️ [SCOUT] Image analysis requested (not implemented yet)")
    elif input_type == "video":
        text = "Video analysis not yet implemented"
        print(f"🎥 [SCOUT] Video analysis requested (not implemented yet)")
    else:
        text = "Unsupported input type"
        print(f"❌ [SCOUT] Unsupported input type: {input_type}")

    scout_time = time.time()
    await send_ws_log("INFO", "SCOUT completed", {"duration_s": round(scout_time - start_time, 2), "chars": len(text)})
    print(f"✅ [SCOUT] Content extracted in {scout_time - start_time:.2f}s")

    # Verify: Run parallel analysis tasks
    await send_ws_log("DEBUG", "VERIFY - starting parallel tasks")
    print(f"\n📍 [STEP 2/5] VERIFY - Running parallel analysis...")
    print(f"🔄 [VERIFY] Starting 3 parallel tasks: Sentiment, Embeddings, Gemini AI")
    
    sentiment_task = asyncio.create_task(call_hf_sentiment(text[:512]))  # Limit for sentiment
    embedding_task = asyncio.create_task(embed_texts([text[:1000]]))  # Limit for embeddings
    gemini_task = asyncio.create_task(call_gemini_analyze(text, source_url))

    await send_ws_log("DEBUG", "VERIFY - waiting for sentiment")
    print(f"⏳ [VERIFY] Waiting for sentiment analysis...")
    sentiment = await sentiment_task
    sentiment_time = time.time()
    await send_ws_log("INFO", "Sentiment completed", {"duration_s": round(sentiment_time - scout_time, 2)})
    print(f"✅ [VERIFY] Sentiment completed in {sentiment_time - scout_time:.2f}s")
    
    await send_ws_log("DEBUG", "VERIFY - waiting for embeddings")
    print(f"⏳ [VERIFY] Waiting for embeddings...")
    vectors = await embedding_task
    embedding_time = time.time()
    await send_ws_log("INFO", "Embeddings completed", {"duration_s": round(embedding_time - sentiment_time, 2)})
    print(f"✅ [VERIFY] Embeddings completed in {embedding_time - sentiment_time:.2f}s")
    
    await send_ws_log("DEBUG", "VERIFY - waiting for Gemini AI")
    print(f"⏳ [VERIFY] Waiting for Gemini AI analysis...")
    gemini_analysis = await gemini_task
    gemini_time = time.time()
    await send_ws_log("INFO", "Gemini completed", {"duration_s": round(gemini_time - embedding_time, 2)})
    print(f"✅ [VERIFY] Gemini AI completed in {gemini_time - embedding_time:.2f}s")

    # Store in vector database and knowledge graph
    await send_ws_log("DEBUG", "STORE - starting storage operations")
    print(f"\n📍 [STEP 3/5] STORE - Saving to Vector DB and Knowledge Graph...")
    store_start = time.time()
    try:
        await send_ws_log("DEBUG", "STORE - upserting embeddings")
        print(f"💾 [STORE] Upserting embeddings to Pinecone...")
        await upsert_embeddings(vectors)
        await send_ws_log("INFO", "STORE - embeddings upserted")
        print(f"✅ [STORE] Embeddings stored")

        await send_ws_log("DEBUG", "STORE - writing graph entities")
        print(f"🕸️ [STORE] Writing entities to Neo4j graph...")
        await write_entities_and_relationships(text[:2000])  # Limit for graph processing
        await send_ws_log("INFO", "STORE - graph entities written")
        print(f"✅ [STORE] Graph entities stored")
    except Exception as e:
        await send_ws_log("WARN", "STORE failed", {"error": str(e)})
        print(f"⚠️ [STORE] Warning: Failed to store in vector DB or graph: {e}")
    
    store_time = time.time()
    print(f"✅ [STORE] Storage completed in {store_time - gemini_time:.2f}s")

    # Synthesize: Build evidence list from Gemini suggestions
    await send_ws_log("DEBUG", "SYNTHESIZE - building evidence")
    print(f"\n📍 [STEP 4/5] SYNTHESIZE - Building evidence list...")
    evidence = []
    for idx, source in enumerate(gemini_analysis.get("evidence_sources", [])[:4]):
        confidence = gemini_analysis.get("confidence", 0.5)
        # Vary confidence slightly for different sources
        source_confidence = max(0.1, min(0.99, confidence + (idx * 0.05) - 0.05))
        evidence.append({
            "source": source,
            "confidence": round(source_confidence, 2)
        })
    
    # Add source URL if available
    if source_url and gemini_analysis.get("confidence", 0) > 0.3:
        evidence.insert(0, {
            "source": source_url,
            "confidence": round(gemini_analysis.get("confidence", 0.5), 2)
        })
    
    await send_ws_log("INFO", "SYNTHESIZE completed", {"evidence_count": len(evidence)})
    print(f"✅ [SYNTHESIZE] Built evidence list with {len(evidence)} sources")

    # Respond: Craft comprehensive result
    await send_ws_log("DEBUG", "RESPOND - crafting final result")
    print(f"\n📍 [STEP 5/5] RESPOND - Crafting final result...")
    result = {
        "status": "completed",
        "summary": gemini_analysis.get("summary", "Analysis completed"),
        "verdict": gemini_analysis.get("verdict", "Uncertain"),
        "confidence": gemini_analysis.get("confidence", 0.5),
        "reasoning": gemini_analysis.get("reasoning", ""),
        "evidence": evidence[:5],  # Limit to top 5 sources
        "sentiment": sentiment,
        "input_type": input_type,
        "analyzed_text_length": len(text)
    }
    
    # Persist to MongoDB if configured
    await send_ws_log("DEBUG", "RESPOND - saving to MongoDB")
    print(f"💾 [RESPOND] Saving to MongoDB...")
    try:
        record_id = await create_analysis_record(input_type, payload, result)
        if record_id:
            await send_ws_log("INFO", "Saved analysis to MongoDB", {"id": record_id})
            print(f"✅ [RESPOND] Saved to MongoDB with ID: {record_id}")
        else:
            await send_ws_log("WARN", "MongoDB not configured or insert failed")
            print(f"⚠️ [RESPOND] MongoDB not configured, skipping persistence")
    except Exception as e:
        await send_ws_log("ERROR", "RESPOND - failed to persist to MongoDB", {"error": str(e)})
        print(f"⚠️ [RESPOND] Warning: Failed to persist to MongoDB: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    await send_ws_log("INFO", "WORKFLOW completed", {"total_time_s": round(total_time, 2), "verdict": result.get("verdict")})
    print(f"\n{'='*80}")
    print(f"✅ [WORKFLOW] COMPLETED - Total time: {total_time:.2f}s")
    print(f"📊 [WORKFLOW] Breakdown:")
    print(f"   - Scout (fetch): {scout_time - start_time:.2f}s")
    print(f"   - Verify (AI): {gemini_time - scout_time:.2f}s")
    print(f"   - Store (DB): {store_time - gemini_time:.2f}s")
    print(f"   - Result: Verdict={result['verdict']}, Confidence={result['confidence']}")
    print(f"{'='*80}\n")
    
    return result





