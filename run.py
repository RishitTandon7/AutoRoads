"""
Startup script for OpenROAD AI Assistant
Run with: python run.py               → starts the web server
          python run.py "query"       → single run CLI mode
          python run.py --file q.txt  → batch mode (one query per line)
          python run.py --run s.tcl   → generate + run a Tcl snippet query
"""
import sys
import os
import subprocess

# ─── Auto-dependency manager ─────────────────────────────────────────────────
REQUIRED_PACKAGES = {
    "fastapi":          "fastapi==0.115.6",
    "uvicorn":          "uvicorn[standard]==0.34.0",
    "pydantic":         "pydantic==2.10.4",
    "requests":         "requests==2.32.3",
    "numpy":            "numpy==2.2.1",
    "dotenv":           "python-dotenv==1.0.1",
    "rich":             "rich==13.9.4",
    "colorama":         "colorama==0.4.6",
    "bs4":              "beautifulsoup4==4.12.3",
    "aiofiles":         "aiofiles==24.1.0",
    "multipart":        "python-multipart==0.0.20",
}

def ensure_dependencies():
    """Check all required packages and auto-install any that are missing."""
    missing = []
    for module, package in REQUIRED_PACKAGES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"[Agent] Detected {len(missing)} missing package(s). Auto-installing...")
        for pkg in missing:
            print(f"  → Installing {pkg} ...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"  ✗ Failed to install {pkg}:\n{result.stderr.strip()}")
            else:
                print(f"  ✓ Installed {pkg}")
        print("[Agent] All dependencies resolved.\n")

# Run dependency check before anything else
ensure_dependencies()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─── Helpers ─────────────────────────────────────────────────────────────────

def run_single_query(query: str):
    """Initialize RAG + LLM and answer a single query, then exit."""
    from backend.rag_engine import RAGEngine
    from backend.llm_client import OllamaClient
    from dotenv import load_dotenv
    import time

    load_dotenv()
    start_time = time.time()

    rag = RAGEngine()
    rag.initialize()
    llm = OllamaClient()

    print(f"\nRetrieving context from OpenROAD docs...")
    results = rag.retrieve(query)
    context = rag.format_context(results)
    print(f"Found {len(results)} relevant source(s).")
    print("Generating response from LLM...\n")

    print("-" * 60)
    answer = llm.generate(prompt=query, context=context)
    print(answer)
    print("-" * 60)
    print(f"\nDone in {round(time.time() - start_time, 2)}s.")


def run_batch_file(filepath: str):
    """Read queries line-by-line from a file and run each one."""
    from backend.rag_engine import RAGEngine
    from backend.llm_client import OllamaClient
    from dotenv import load_dotenv
    import time

    if not os.path.isfile(filepath):
        print(f"[Error] File not found: {filepath}")
        sys.exit(1)

    load_dotenv()

    with open(filepath, "r", encoding="utf-8") as f:
        queries = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not queries:
        print("[Error] No queries found in the file.")
        sys.exit(1)

    print(f"\n[Batch Mode] Running {len(queries)} queries from '{filepath}'\n")

    rag = RAGEngine()
    rag.initialize()
    llm = OllamaClient()

    for i, query in enumerate(queries, 1):
        print(f"\n{'=' * 60}")
        print(f"  Query {i}/{len(queries)}: {query}")
        print("=" * 60)
        start = time.time()
        results = rag.retrieve(query)
        context = rag.format_context(results)
        answer = llm.generate(prompt=query, context=context)
        print(answer)
        print(f"\n  [Done in {round(time.time() - start, 2)}s]")

    print(f"\n{'=' * 60}")
    print(f"  [Batch Complete] Ran {len(queries)} queries.")
    print("=" * 60)


def run_snippet_file(filepath: str):
    """
    Treat a generated Tcl script as a query:
    reads the file, sends its content to the LLM for explanation/execution advice,
    and prints a response. If multiple commands exist, they're handled as a batch query.
    """
    from backend.rag_engine import RAGEngine
    from backend.llm_client import OllamaClient
    from dotenv import load_dotenv
    import time

    if not os.path.isfile(filepath):
        print(f"[Error] File not found: {filepath}")
        sys.exit(1)

    load_dotenv()

    with open(filepath, "r", encoding="utf-8") as f:
        snippet = f.read().strip()

    if not snippet:
        print("[Error] The snippet file is empty.")
        sys.exit(1)

    commands = [line.strip() for line in snippet.splitlines()
                if line.strip() and not line.strip().startswith("#")]

    print(f"\n[Snippet Run Mode] Loaded '{filepath}'")
    print(f"  → Detected {len(commands)} command(s) in the snippet.\n")

    rag = RAGEngine()
    rag.initialize()
    llm = OllamaClient()
    start = time.time()

    if len(commands) == 1:
        # Single command → explain and advise
        query = f"Explain and provide usage guidance for this OpenROAD command:\n\n{commands[0]}"
    else:
        # Multiple commands → treat as a full flow snippet
        query = (
            f"Analyze this OpenROAD Tcl script snippet, explain what each step does, "
            f"identify any issues, and suggest optimizations:\n\n{snippet}"
        )

    results = rag.retrieve(query)
    context = rag.format_context(results)
    answer = llm.generate(prompt=query, context=context)

    print("-" * 60)
    print(answer)
    print("-" * 60)
    print(f"\nDone in {round(time.time() - start, 2)}s.")


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  OpenROAD AI Assistant")

    args = sys.argv[1:]

    if not args:
        # ── Server mode ──────────────────────────────────────────
        print("  http://localhost:8000")
        print("=" * 60)
        import uvicorn
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=False
        )

    elif args[0] == "--file" and len(args) >= 2:
        # ── Batch mode: --file queries.txt ───────────────────────
        print(f"  Mode: Batch Run  |  File: {args[1]}")
        print("=" * 60)
        run_batch_file(args[1])

    elif args[0] == "--run" and len(args) >= 2:
        # ── Snippet run mode: --run script.tcl ───────────────────
        print(f"  Mode: Snippet Run  |  Script: {args[1]}")
        print("=" * 60)
        run_snippet_file(args[1])

    else:
        # ── Single query mode ─────────────────────────────────────
        query = " ".join(args)
        print(f"  Mode: Single Run CLI")
        print("=" * 60)
        print(f"\nQuery: '{query}'")
        run_single_query(query)
