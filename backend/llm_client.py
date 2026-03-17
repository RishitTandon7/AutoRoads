"""
Ollama LLM Client for OpenROAD AI Assistant
Handles communication with local Ollama server
"""

import json
import requests
from typing import Optional, Generator, Dict, Any


SYSTEM_PROMPT = """You are an expert AI assistant specializing in the OpenROAD electronic design automation (EDA) tool and the RTL-to-GDSII chip design flow. You have deep knowledge of:

- OpenROAD commands and Tcl scripting
- Physical design stages: floorplanning, placement, CTS, routing
- Technology files: LEF, DEF, Liberty, SDC formats
- Sky130 and other open PDKs
- Debugging common OpenROAD errors and DRC violations
- Best practices for chip design optimization

You assist engineers and students in understanding and using OpenROAD effectively.

Guidelines:
1. Always provide accurate, specific OpenROAD commands with proper syntax
2. Include practical Tcl code examples when relevant
3. Explain EDA concepts clearly for both beginners and experts
4. When debugging errors, provide step-by-step solutions
5. Cite which stage of the flow a command belongs to
6. If unsure, recommend consulting the official OpenROAD documentation at openroad.readthedocs.io
7. HIGH PRIORITY: The user uses the 'Run All' feature which executes code natively on their host.
   - We have already successfully set up `wsl` and `docker` silently in the background!
   - If the user asks how to "install" or "setup" OpenROAD, DO NOT give them installation scripts or tutorials. Tell them exactly this: "You're all set! I have already connected this AI assistant directly to the OpenROAD engine locally via WSL Desktop. Whenever I generate a Tcl script for you, just click the **⚡ Run All** button and it will instantly execute natively in the background."
   - NEVER use Linux commands like `export`, `sudo`, `make`, `brew`, `apt-get`, or `nproc`.
   - NEVER use `export PATH=...`. On Windows, use `$env:PATH += ";C:\\path"` instead.
   - For environment variables, ALWAYS use Windows PowerShell syntax: `$env:VAR_NAME = "value"`
8. The official OpenROAD GitHub repository is `https://github.com/The-OpenROAD-Project/OpenROAD.git`. Never hallucinate repository URLs.

When generating Tcl scripts, always:
- Include comments explaining each step
- Use variables for file paths
- Add error checking where appropriate
- Follow OpenROAD flow order (floorplan → placement → CTS → routing)
"""

TASK_PREFIXES = {
    "explain": "Explain the following OpenROAD command/concept clearly:",
    "generate_script": "Generate a complete, well-commented Tcl script for:",
    "debug": "Debug this OpenROAD error or log output and provide solutions:",
    "search": "Find and explain relevant OpenROAD documentation for:",
    "flow": "Provide step-by-step guidance for this OpenROAD flow task:",
}


class OllamaClient:
    """Client for the Ollama local LLM server."""

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "llama3.2", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list:
        """List available models in Ollama."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def generate(self, prompt: str, context: str = "",
                 task_type: str = "search",
                 stream: bool = False) -> str:
        """
        Generate a response using Ollama.
        
        Args:
            prompt: User's question or request
            context: Retrieved documentation context
            task_type: Type of task (explain/generate_script/debug/search/flow)
            stream: Whether to stream the response
        
        Returns:
            Generated response text
        """
        task_prefix = TASK_PREFIXES.get(task_type, "")
        
        # Build the full prompt
        if context:
            full_prompt = f"""Based on the following OpenROAD documentation context, {task_prefix.lower()}

## Retrieved Documentation Context:
{context}

## User Question:
{prompt}

## Answer:"""
        else:
            full_prompt = f"""{task_prefix}

{prompt}

## Answer:"""

        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_ctx": 4096,
            }
        }

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "No response generated.")
            else:
                return f"Error: Ollama returned status {resp.status_code}. Is it running with model '{self.model}'?"
        except requests.exceptions.ConnectionError:
            return self._fallback_response(prompt, context, task_type)
        except requests.exceptions.Timeout:
            return "Error: Request to Ollama timed out. Try a faster model or check your system resources."
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def _fallback_response(self, prompt: str, context: str, task_type: str) -> str:
        """Provide a response when Ollama is unavailable, using retrieved context."""
        if context:
            return f"""**⚠️ Ollama is not running** — showing retrieved documentation instead.

To enable AI-powered responses, start Ollama:
```bash
ollama serve
ollama pull llama3.2
```

---

## Relevant Documentation Found:

{context}

---
*Install and start Ollama for full AI-generated explanations and script generation.*"""
        else:
            return """**⚠️ Ollama is not running** and no relevant documentation was found.

Please:
1. Start Ollama: `ollama serve`
2. Pull a model: `ollama pull llama3.2`
3. Then try your query again.

Alternatively, check the [OpenROAD Documentation](https://openroad.readthedocs.io) directly."""

    def build_messages(self, prompt: str, context: str, task_type: str) -> Dict[str, Any]:
        """Prepare messages payload for chat-style API."""
        task_prefix = TASK_PREFIXES.get(task_type, "")
        user_content = f"{task_prefix}\n\n"
        if context:
            user_content += f"Context from OpenROAD docs:\n{context}\n\n"
        user_content += f"Question: {prompt}"
        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "stream": False,
            "options": {"temperature": 0.3, "top_p": 0.9}
        }
