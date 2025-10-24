# src/generate_quiz.py
"""
Quiz Generator using Groq API (OpenAI-compatible endpoint)

Improvements over original:
 - Loads GROQ_API_KEY from .env (via python-dotenv)
 - Supports GROQ_BASE_URL override
 - Lazy client initialization with a clear error path
 - USE_MOCK environment flag to explicitly allow using MOCK when key missing or API fails
 - Attempts to extract first JSON array substring from model output (robust against extra text)
 - Better logging and explicit exceptions when configured to fail loudly
"""

# src/generate_quiz.py
from dotenv import load_dotenv
from pathlib import Path
import os

# This builds an explicit path to your .env file
# It assumes .env is in the 'backend' directory, one level above 'src'
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI
from httpx import HTTPError

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Environment-configurable behavior
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
USE_MOCK = os.getenv("USE_MOCK", "1").lower() in ("1", "true", "yes")

# Mock fallback questions for offline/dev mode
MOCK_QUIZ = [
    {
        "question": "What is supervised learning?",
        "choices": {
            "A": "Learning without labels",
            "B": "Learning from labeled data",
            "C": "Learning from rewards only",
            "D": "A type of clustering"
        },
        "answer": "B",
        "explanation": "Supervised learning uses labeled examples to train models."
    },
    {
        "question": "Which algorithm is commonly used for classification?",
        "choices": {
            "A": "K-means",
            "B": "Linear regression",
            "C": "Logistic regression",
            "D": "PCA"
        },
        "answer": "C",
        "explanation": "Logistic regression is widely used for binary classification."
    },
    {
        "question": "What is overfitting?",
        "choices": {
            "A": "Model fits training noise and fails on unseen data",
            "B": "Model generalizes perfectly",
            "C": "Model has too little capacity",
            "D": "Model underfits training data"
        },
        "answer": "A",
        "explanation": "Overfitting happens when a model memorizes noise in training data."
    }
]

# internal cached client
_client: Optional[OpenAI] = None


def _init_client() -> Optional[OpenAI]:
    """Initialize and cache the OpenAI/Groq client. Returns None if no API key and USE_MOCK is True."""
    global _client
    if _client is not None:
        return _client

    if not GROQ_API_KEY:
        msg = "GROQ_API_KEY / OPENAI_API_KEY not found in environment."
        if USE_MOCK:
            logger.warning("%s Running in MOCK mode (USE_MOCK=%r).", msg, USE_MOCK)
            return None
        else:
            logger.error("%s Set USE_MOCK=1 to allow mocks, or provide a valid key.", msg)
            raise RuntimeError(msg)

    # instantiate client
    try:
        logger.debug("Initializing Groq/OpenAI client (model=%s, base_url=%s)", MODEL, GROQ_BASE_URL)
        _client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
        return _client
    except Exception as e:
        logger.exception("Failed to initialize OpenAI client: %s", e)
        if USE_MOCK:
            logger.warning("Falling back to mock quiz because client init failed and USE_MOCK=%r", USE_MOCK)
            return None
        raise


def _try_parse_json(text: str) -> Any:
    """Try to parse the whole text as JSON; on failure return None."""
    try:
        return json.loads(text)
    except Exception:
        return None


def _extract_first_json_array(text: str) -> Optional[str]:
    """
    Attempts to extract the first JSON array substring from the text.
    This helps when the model prints extra commentary around the JSON.
    Returns the JSON substring or None.
    """
    start = text.find("[")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                # quick sanity check: parseable?
                try:
                    json.loads(candidate)
                    return candidate
                except Exception:
                    return None
    return None


def generate_quiz(topic: str, top_k: int = 3, use_mock_on_fail: Optional[bool] = None) -> Dict[str, Any]:
    """
    Generate quiz questions about `topic`.

    Returns:
      {"from_mock": bool, "questions": [...]}

    Behavior:
     - If environment variable USE_MOCK is truthy and no API key is present, returns the MOCK_QUIZ.
     - If API calls fail and use_mock_on_fail (param or env) is true, returns mock; otherwise raises.
    """
    # resolve final decision about mock fallback
    if use_mock_on_fail is None:
        use_mock_on_fail = USE_MOCK

    client = _init_client()
    if client is None:
        # no client available -> return mock if allowed
        if use_mock_on_fail:
            logger.info("No API client available; returning mock quiz (top_k=%d).", top_k)
            return {"from_mock": True, "questions": MOCK_QUIZ[:top_k]}
        raise RuntimeError("No API client available and mock fallback disabled.")

    try:
        prompt = (
            f"Generate {top_k} multiple-choice questions about '{topic}'. "
            "Respond in strict JSON array format (top-level array). "
            "Each element must be an object with keys: question (string), "
            "choices (object with keys A,B,C,D), answer (A/B/C/D), explanation (string). "
            "Return only the JSON array (no surrounding text) if possible."
        )

        logger.debug("Sending prompt to model: %s", prompt)
        response = client.responses.create(
            input=prompt,
            model=MODEL,
        )

        # Attempt to get output text cleanly. The new OpenAI client typically exposes output_text,
        # but be defensive if shape differs.
        output_text = ""
        if hasattr(response, "output_text") and isinstance(response.output_text, str):
            output_text = response.output_text.strip()
        else:
            # best-effort fallback: try to stringify top-level response object
            try:
                output_text = json.dumps(response, default=str)
            except Exception:
                output_text = str(response)

        logger.debug("Model raw output (first 400 chars): %s", output_text[:400])

        # 1) Try direct parse
        parsed = _try_parse_json(output_text)
        if parsed is None:
            # 2) Try to extract first JSON array substring
            json_sub = _extract_first_json_array(output_text)
            if json_sub:
                parsed = _try_parse_json(json_sub)

        if isinstance(parsed, list):
            # optionally trim to top_k
            logger.info("Successfully parsed %d questions from model output.", len(parsed))
            return {"from_mock": False, "questions": parsed[:top_k]}
        # if parsing failed, return raw_text wrapper (or fallback to mock)
        logger.warning("Could not parse model output as JSON array. Returning raw_text.")
        if use_mock_on_fail:
            logger.info("Falling back to mock quiz due to parse failure and use_mock_on_fail=%r", use_mock_on_fail)
            return {"from_mock": True, "questions": MOCK_QUIZ[:top_k]}
        return {"from_mock": False, "questions": [{"raw_text": output_text}]}

    except (HTTPError, Exception) as e:
        logger.exception("Groq API call failed: %s", e)
        if use_mock_on_fail:
            logger.info("Returning mock quiz due to API failure and use_mock_on_fail=%r", use_mock_on_fail)
            return {"from_mock": True, "questions": MOCK_QUIZ[:top_k]}
        raise
