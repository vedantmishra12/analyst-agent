"""Ollama LLM service — model management, prompting, streaming."""

import requests
import json
from typing import Generator
from config.settings import OLLAMA_HOST


class OllamaService:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host

    # ── Connection ──────────────────────────────────────────────────────────
    def is_running(self) -> bool:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=5)
            if r.status_code == 200:
                return [m["name"] for m in r.json().get("models", [])]
        except Exception:
            pass
        return []

    # ── Generation ──────────────────────────────────────────────────────────
    def generate(self, prompt: str, model: str, system: str = "") -> str:
        payload = {
            "model":  model,
            "prompt": prompt,
            "stream": False,
            "system": system,
            "options": {"temperature": 0.1, "num_predict": 2048},
        }
        try:
            r = requests.post(f"{self.host}/api/generate", json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["response"]
        except Exception as e:
            return f"⚠️ Ollama error: {e}"

    def stream(self, prompt: str, model: str, system: str = "") -> Generator[str, None, None]:
        payload = {
            "model":  model,
            "prompt": prompt,
            "stream": True,
            "system": system,
            "options": {"temperature": 0.1, "num_predict": 2048},
        }
        try:
            with requests.post(f"{self.host}/api/generate", json=payload, stream=True, timeout=120) as r:
                for line in r.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if token := chunk.get("response", ""):
                            yield token
                        if chunk.get("done"):
                            break
        except Exception as e:
            yield f"⚠️ Stream error: {e}"

    def chat(self, messages: list[dict], model: str) -> str:
        payload = {
            "model":    model,
            "messages": messages,
            "stream":   False,
            "options":  {"temperature": 0.1, "num_predict": 2048},
        }
        try:
            r = requests.post(f"{self.host}/api/chat", json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["message"]["content"]
        except Exception as e:
            return f"⚠️ Ollama error: {e}"
