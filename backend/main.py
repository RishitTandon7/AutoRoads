"""
FastAPI Backend for OpenROAD AI Assistant
"""

import os
import re
import sys
import time
import traceback
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.rag_engine import RAGEngine
from backend.llm_client import OllamaClient
from backend.openroad_flow import router as openroad_router
from dotenv import load_dotenv

load_dotenv()

# ─── Config ─────────────────────────────────────────────────────────────
OLLAMA_URL      = os.getenv("OLLAMA_BASE_URL",   "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",      "llama3.2")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL",   "all-MiniLM-L6-v2")
FAISS_PATH      = os.getenv("FAISS_INDEX_PATH",  "./data/faiss_index")

# ─── Global instances ────────────────────────────────────────────────────
rag_engine: Optional[RAGEngine] = None
llm_client: Optional[OllamaClient] = None

INSTALL_SETUP_RESPONSE = (
    "You're all set! I have already connected this AI assistant directly to the "
    "OpenROAD engine locally via WSL Desktop. Whenever I generate a Tcl script "
    "for you, just click the **⚡ Run All** button and it will instantly execute "
    "natively in the background."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG engine and LLM client on startup."""
    global rag_engine, llm_client
    print("🚀 Starting OpenROAD AI Assistant Backend...")

    try:
        rag_engine = RAGEngine(
            model_name=EMBEDDING_MODEL,
            index_path=FAISS_PATH,
            top_k=5
        )
        rag_engine.initialize()
    except Exception as e:
        print(f"Warning: RAG engine init error: {e}")
        traceback.print_exc()

    llm_client = OllamaClient(base_url=OLLAMA_URL, model=OLLAMA_MODEL)
    ollama_status = "✓ Available" if llm_client.is_available() else "✗ Not running"
    print(f"Ollama status: {ollama_status}")
    print("✅ Backend ready!")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="OpenROAD AI Assistant",
    description="LLM-powered assistant for the OpenROAD chip design flow",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(openroad_router, prefix="/api")

# ─── Pydantic models ─────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    task_type: str = "search"   # explain | generate_script | debug | search | flow
    top_k: int = 5

class QueryResponse(BaseModel):
    query: str
    task_type: str
    answer: str
    sources: List[dict]
    ollama_available: bool
    processing_time: float

class StatusResponse(BaseModel):
    status: str
    rag_ready: bool
    ollama_available: bool
    ollama_model: str
    available_models: List[str]
    doc_count: int
    search_mode: str = "tfidf"


# ─── Execution helpers (defined first — used by routes below) ─────────────

def _find_skywater_pdk() -> Optional[str]:
    """Try common locations for the skywater-pdk / sky130 PDK."""
    candidates = [
        os.getenv("PDK_ROOT"),
        os.getenv("SKY130_ROOT"),
        r"C:\skywater-pdk",
        r"C:\pdk",
        "/usr/local/share/pdk",
        "/usr/share/pdk",
        str(Path.home() / "skywater-pdk"),
        str(Path.home() / "pdk"),
    ]
    for c in candidates:
        if c and Path(c).exists():
            return str(c)

    # Auto-synthesize a minimal mock PDK so scripts don't crash on missing files
    try:
        mock_pdk_root = os.path.abspath("./mock_pdk")
        libs_dir = os.path.join(mock_pdk_root, "sky130A", "libs.ref", "sky130_fd_sc_hd")
        lef_dir  = os.path.join(libs_dir, "lef")
        lib_dir  = os.path.join(libs_dir, "lib")
        os.makedirs(lef_dir, exist_ok=True)
        os.makedirs(lib_dir, exist_ok=True)
        Path(os.path.join(lef_dir, "sky130_fd_sc_hd.tlef")).touch()
        Path(os.path.join(lef_dir, "sky130_fd_sc_hd.lef")).touch()
        Path(os.path.join(lib_dir, "sky130_fd_sc_hd__tt_025C_1v80.lib")).touch()
        return mock_pdk_root
    except Exception as e:
        print("[Mock PDK] Error synthesizing mock PDK:", e)
        return None


def _windows_path_to_wsl(path_str: str) -> str:
    """Convert a Windows path like D:\\foo\\bar to /mnt/d/foo/bar for WSL."""
    normalized = path_str.replace("\\", "/")
    if len(normalized) >= 3 and normalized[1:3] == ":/":
        return f"/mnt/{normalized[0].lower()}{normalized[2:]}"
    return normalized


def _is_openroad_install_query(query: str) -> bool:
    """Return True when the user is asking to install/setup OpenROAD itself."""
    normalized = query.lower()
    install_terms = ("install", "setup", "set up", "configure")
    openroad_terms = ("openroad", "open road", "the openroad project", "openroad project")
    return any(term in normalized for term in install_terms) and any(
        term in normalized for term in openroad_terms
    )


def _validate_executable_script(script: str) -> Optional[str]:
    """Reject placeholder or misleading commands before native execution."""
    stripped_lines = [line.strip() for line in script.splitlines() if line.strip()]
    lowered = [line.lower() for line in stripped_lines]

    placeholder_markers = (
        "/path/to/",
        "./your_design/",
        "<path>",
        "<project>",
        "example/path",
    )
    if any(marker in ln for ln in lowered for marker in placeholder_markers):
        return (
            "This script contains placeholder paths such as `/path/to/...` or "
            "`./your_design/`. Replace them with real paths before using Run All."
        )

    if any(line == "setup" for line in lowered):
        return (
            "The generated script includes a bare `setup` command, which is not a "
            "valid OpenROAD command in this environment. Ask for a real Tcl flow "
            "script instead of installation steps."
        )

    return None


def _detect_executor(script: str) -> tuple:
    """
    Return (kind, argv_prefix) for the best available executor.
    kind: 'python' | 'wsl_openroad' | 'openroad' | 'tclsh' | 'bash' | 'sh' | 'powershell' | 'none'
    """
    # ── Check if it's a native Python script first ───────────────────────────
    if _detect_snippet_language(script) == "python":
        path = shutil.which("python") or shutil.which("python3")
        if path:
            return "python", [path]

    stripped = script.strip()
    first_token = stripped.split()[0] if stripped.split() else ""

    # Does the script start with or contain bare `openroad` CLI invocations?
    looks_like_openroad_cmd = (
        first_token == "openroad"
        or stripped.startswith("openroad ")
        or "\nopenroad " in script
        or "\nopenroad\n" in script
    )

    looks_like_tcl = looks_like_openroad_cmd or any(
        kw in script for kw in (
            "read_lef", "read_liberty", "global_placement",
            "initialize_floorplan", "clock_tree_synthesis",
            "detailed_route", "write_gds", "report_drc",
            "detailed_placement", "repair_design",
            "puts ", "set ", "proc ", "source "
        )
    )

    # ── WSL OpenROAD (primary path on Windows) ──────────────────────────────
    if looks_like_tcl and os.name == "nt" and shutil.which("wsl.exe"):
        # For bare openroad CLI calls — run them directly in WSL shell
        if looks_like_openroad_cmd and not any(
            kw in script for kw in ("read_lef", "read_liberty", "global_placement",
                                    "initialize_floorplan", "clock_tree_synthesis",
                                    "detailed_route", "write_gds", "report_drc",
                                    "puts ", "set ", "proc ")
        ):
            # Bare openroad command: run as shell command in WSL, not as a Tcl file
            return "wsl_shell", ["wsl.exe", "-d", "Ubuntu", "--", "bash", "-c"]
        return "wsl_openroad", [
            "wsl.exe", "-d", "Ubuntu", "--", "openroad", "-no_init", "-exit"
        ]

    # ── Native openroad binary (non-Windows / openroad in PATH) ─────────────
    if looks_like_tcl:
        for name in ("openroad", "openroad.exe"):
            path = shutil.which(name)
            if path:
                return "openroad", [path, "-no_init", "-exit"]

    # ── Generic Tcl interpreter ──────────────────────────────────────────────
    if looks_like_tcl:
        for name in ("tclsh", "tclsh8.6", "tclsh9.0"):
            path = shutil.which(name)
            if path:
                return "tclsh", [path]
        return "none_tcl", []

    # ── PowerShell (Windows scripts / .ps1) ──────────────────────────────────
    if os.name == "nt":
        for name in ("pwsh", "powershell"):
            path = shutil.which(name)
            if path:
                return "powershell", [path, "-Command"]

    # ── Bash / sh ────────────────────────────────────────────────────────────
    for name in ("bash", "sh"):
        path = shutil.which(name)
        if path:
            return name, [path]

    # ── Last resort: PowerShell ───────────────────────────────────────────────
    for name in ("pwsh", "powershell"):
        path = shutil.which(name)
        if path:
            return "powershell", [path, "-Command"]

    return "none", []


def _detect_snippet_language(snippet: str) -> str:
    """
    Heuristic language detection for a code snippet.
    Returns: 'python' | 'tcl' | 'powershell' | 'bash'
    """
    lines = [l.strip() for l in snippet.splitlines() if l.strip()]
    first = lines[0] if lines else ""

    # Shebang lines
    if first.startswith("#!/usr/bin/env python") or first.startswith("#!/usr/bin/python"):
        return "python"
    if first.startswith("#!/bin/bash") or first.startswith("#!/bin/sh"):
        return "bash"

    # Python indicators
    python_patterns = [
        r"^import ", r"^from .+ import", r"^print\(", r"^def ", r"^class ",
        r"^if __name__", r"^with open", r"^#!.*python", r"pip install",
        r"^import numpy", r"^import pandas", r"^import matplotlib",
    ]
    for pat in python_patterns:
        if any(re.search(pat, l) for l in lines):
            return "python"

    # Tcl / OpenROAD indicators
    tcl_keywords = [
        "read_lef", "read_liberty", "read_verilog", "global_placement",
        "initialize_floorplan", "clock_tree_synthesis", "detailed_route",
        "read_db", "write_db", "report_", "puts ", "set ", "proc ",
        "source ", "set_cmd_units", "utl::info",
    ]
    if any(kw in snippet for kw in tcl_keywords):
        return "tcl"

    # PowerShell indicators
    ps_patterns = [r"\$[A-Za-z]", r"Write-Host", r"Get-", r"Set-", r"Invoke-", r"New-Item"]
    for pat in ps_patterns:
        if any(re.search(pat, l) for l in lines):
            return "powershell"

    # Default: python on Windows, bash elsewhere
    return "python" if os.name == "nt" else "bash"


# Common import-name → pip-package-name mapping
_PKG_MAP: dict = {
    "cv2":     "opencv-python",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "PIL":     "Pillow",
    "bs4":     "beautifulsoup4",
    "yaml":    "PyYAML",
    "dotenv":  "python-dotenv",
    "serial":  "pyserial",
}


def _run_snippet_with_autoinstall(snippet: str, language: str, env: dict) -> dict:
    """
    Write snippet to a temp file, execute it with the appropriate executor.
    For Python: on ModuleNotFoundError / ImportError, auto-pip-install the
    missing package and re-run (up to 5 packages).
    Returns dict: stdout, stderr, exit_code, executor, elapsed, installed_packages.
    """
    start = time.time()

    # ── Choose executor ──────────────────────────────────────────────────
    if language == "python":
        python_exe  = shutil.which("python") or shutil.which("python3") or sys.executable
        executor_kind = "python"
        suffix        = ".py"
        base_cmd      = [python_exe]

    elif language == "tcl":
        executor_kind, base_cmd = _detect_executor(snippet)
        suffix = ".tcl"

    elif language == "powershell":
        ps = shutil.which("pwsh") or shutil.which("powershell")
        if not ps:
            return {
                "stdout": "", "stderr": "PowerShell not found on system PATH.",
                "exit_code": -1, "executor": "none",
                "elapsed": round(time.time() - start, 3), "installed_packages": [],
            }
        executor_kind = "powershell"
        suffix        = ".ps1"
        base_cmd      = [ps, "-ExecutionPolicy", "Bypass", "-File"]

    else:  # bash / sh
        sh = shutil.which("bash") or shutil.which("sh")
        if not sh:
            ps = shutil.which("pwsh") or shutil.which("powershell")
            if ps:
                executor_kind = "powershell"
                suffix        = ".ps1"
                base_cmd      = [ps, "-ExecutionPolicy", "Bypass", "-File"]
            else:
                return {
                    "stdout": "", "stderr": "No shell (bash/powershell) found on PATH.",
                    "exit_code": -1, "executor": "none",
                    "elapsed": round(time.time() - start, 3), "installed_packages": [],
                }
        else:
            executor_kind = "bash"
            suffix        = ".sh"
            base_cmd      = [sh]

    # ── Handle Tcl 'none' cases ──────────────────────────────────────────
    if language == "tcl" and (executor_kind.startswith("none") or not base_cmd):
        return {
            "stdout": "",
            "stderr": (
                "OpenROAD or tclsh not found on system PATH. "
                "Install OpenROAD or Tcl to run this EDA script."
            ),
            "exit_code": -1, "executor": "none",
            "elapsed": round(time.time() - start, 3), "installed_packages": [],
        }

    # ── Write snippet to temp file ───────────────────────────────────────
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    ) as tf:
        tf.write(snippet)
        tmp_path = tf.name

    installed_packages: List[str] = []

    def _do_run() -> tuple:
        cmd = base_cmd + [tmp_path]
        try:
            r = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=60, env=env,
                cwd=str(Path(tmp_path).parent),
            )
            return r.stdout or "", r.stderr or "", r.returncode
        except subprocess.TimeoutExpired:
            return "", "Execution timed out after 60 seconds.", -1
        except Exception as exc:
            return "", f"Execution error: {exc}", -1

    stdout, stderr, exit_code = _do_run()

    # ── Python auto-install loop ──────────────────────────────────────────
    if language == "python" and exit_code != 0:
        python_exe = base_cmd[0]

        for _attempt in range(5):  # max 5 auto-installs per run
            mod_match = re.search(
                r"(?:ModuleNotFoundError|ImportError):.*?'([\w\-\.]+)'",
                stderr,
            ) or re.search(
                r"No module named '([\w\-\.]+)'",
                stderr,
            )
            if not mod_match:
                break  # No more installable errors

            raw_pkg      = mod_match.group(1).replace("_", "-")
            install_name = _PKG_MAP.get(raw_pkg, raw_pkg)

            if install_name in installed_packages:
                break  # Already tried this one

            print(f"[SingleRun] Auto-installing missing package: {install_name}")
            pip_result = subprocess.run(
                [python_exe, "-m", "pip", "install", install_name, "--quiet"],
                capture_output=True, text=True, timeout=120,
            )
            installed_packages.append(install_name)

            if pip_result.returncode != 0:
                stderr = stderr + f"\n\n[Auto-install FAILED for '{install_name}']\n{pip_result.stderr}"
                break

            # Re-run after successful install
            stdout, stderr, exit_code = _do_run()
            if exit_code == 0:
                break

    try:
        os.unlink(tmp_path)
    except Exception:
        pass

    return {
        "stdout":             stdout,
        "stderr":             stderr,
        "exit_code":          exit_code,
        "executor":           executor_kind,
        "elapsed":            round(time.time() - start, 3),
        "installed_packages": installed_packages,
    }


# ─── Routes ──────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return FileResponse("frontend/landing.html")

@app.get("/app", include_in_schema=False)
async def chat_app():
    return FileResponse("frontend/index.html")


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Get system status."""
    return StatusResponse(
        status="ok",
        rag_ready=rag_engine.is_ready if rag_engine else False,
        ollama_available=llm_client.is_available() if llm_client else False,
        ollama_model=OLLAMA_MODEL,
        available_models=llm_client.list_models() if llm_client else [],
        doc_count=len(rag_engine.documents) if rag_engine else 0,
        search_mode=rag_engine.search_mode if rag_engine else "tfidf",
    )


@app.post("/api/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Main RAG + LLM query endpoint."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start = time.time()

    results: list = []
    context: str  = ""
    sources: list = []

    if rag_engine and rag_engine.is_ready:
        results = rag_engine.retrieve(req.query, top_k=req.top_k)
        context = rag_engine.format_context(results)
        sources = [
            {
                "id":       r.doc_id,
                "title":    r.title,
                "category": r.category,
                "score":    round(r.score, 4),
                "tags":     r.tags,
                "snippet":  r.content[:300] + "..." if len(r.content) > 300 else r.content,
            }
            for r in results
        ]

    if _is_openroad_install_query(req.query):
        answer = INSTALL_SETUP_RESPONSE
        sources = []
    elif llm_client:
        answer = llm_client.generate(
            prompt=req.query,
            context=context,
            task_type=req.task_type,
        )
    else:
        answer = context or "Backend not fully initialized. Please try again."

    return QueryResponse(
        query=req.query,
        task_type=req.task_type,
        answer=answer,
        sources=sources,
        ollama_available=llm_client.is_available() if llm_client else False,
        processing_time=round(time.time() - start, 3),
    )


@app.post("/api/debug")
async def debug_error(request: dict):
    """Specialized endpoint for debugging OpenROAD logs/errors."""
    log_text = request.get("log", "")
    if not log_text.strip():
        raise HTTPException(status_code=400, detail="Log text cannot be empty")

    start       = time.time()
    debug_query = f"OpenROAD error debugging: {log_text[:500]}"
    results, context, sources = [], "", []

    if rag_engine and rag_engine.is_ready:
        results = rag_engine.retrieve(debug_query, top_k=4)
        context = rag_engine.format_context(results)
        sources = [
            {"title": r.title, "category": r.category, "score": round(r.score, 4)}
            for r in results
        ]

    prompt = (
        f"Analyze this OpenROAD log output or error message and provide:\n"
        f"1. What the error means\n"
        f"2. Root cause(s)\n"
        f"3. Step-by-step solution(s)\n"
        f"4. Prevention tips\n\n"
        f"Log/Error:\n{log_text}"
    )

    answer = (
        llm_client.generate(prompt=prompt, context=context, task_type="debug")
        if llm_client else context
    )

    return {
        "answer":           answer,
        "sources":          sources,
        "processing_time":  round(time.time() - start, 3),
        "ollama_available": llm_client.is_available() if llm_client else False,
    }


@app.post("/api/generate-script")
async def generate_script(request: dict):
    """Generate a Tcl script for a specified flow task."""
    task    = request.get("task", "")
    options = request.get("options", {})

    if not task.strip():
        raise HTTPException(status_code=400, detail="Task description required")

    start  = time.time()
    query  = f"Generate Tcl script for: {task}"
    results, context, sources = [], "", []

    if rag_engine and rag_engine.is_ready:
        results = rag_engine.retrieve(query, top_k=4)
        context = rag_engine.format_context(results)
        sources = [{"title": r.title, "category": r.category} for r in results]

    # ── Anti-hallucination guardrail — real OpenROAD command reference ──────
    VALID_COMMANDS_HINT = (
        "\n\nCRITICAL: Only use REAL OpenROAD Tcl commands. "
        "NEVER invent commands. Commands like 'ahmp' or 'run_ahhmp' DO NOT EXIST.\n"
        "REQUIRED DATA LOADING SEQUENCE (Must include these at the start of every script):\n"
        "  1. read_lef <path_to_tech_lef>\n"
        "  2. read_lef <path_to_stdcell_lef>\n"
        "  3. read_liberty <path_to_lib_file>\n"
        "  4. read_verilog <path_to_v_file>\n"
        "  5. link_design <top_module_name>\n"
        "  6. read_sdc <path_to_sdc_file>\n"
        "\nREAL commands for placement/routing:\n"
        "    initialize_floorplan -die_area {0 0 1000 1000} -core_area {10 10 990 990} -site <site_name>\n"
        "    place_pins -hor_layers met3 -ver_layers met2\n"
        "    rtl_macro_placer -halo_width 10.0 -halo_height 10.0\n"
        "    global_placement -timing_driven -density 0.7\n"
        "    detailed_placement\n"
        "    check_placement -verbose\n"
        "    estimate_parasitics -placement\n"
        "    repair_design\n"
        "    repair_timing -setup\n"
        "    repair_clock_nets\n"
        "    global_route\n"
        "    detailed_route\n"
        "    write_def <output_file>\n"
        "\nNote: Setting a variable like 'set tech_file path/to/file' does NOTHING unless you "
        "pass it to the 'read_lef $tech_file' command. Always include the 'read_' commands."
    )

    prompt_parts = [f"Generate a complete, well-commented OpenROAD Tcl script for: {task}"]
    if options.get("pdk"):
        prompt_parts.append(f"PDK: {options['pdk']}")
    if options.get("design"):
        prompt_parts.append(f"Design: {options['design']}")
    if options.get("utilization"):
        prompt_parts.append(f"Target utilization: {options['utilization']}%")
    prompt_parts.append("Include all necessary commands, variables, and comments.")
    prompt_parts.append(VALID_COMMANDS_HINT)

    answer = (
        llm_client.generate(
            prompt="\n".join(prompt_parts),
            context=context,
            task_type="generate_script",
        )
        if llm_client else context
    )

    return {
        "script":          answer,
        "task":            task,
        "sources":         sources,
        "processing_time": round(time.time() - start, 3),
    }


@app.get("/api/docs-categories")
async def get_categories():
    """Return all documentation categories."""
    if not rag_engine or not rag_engine.is_ready:
        return {"categories": []}
    cats = list(set(d["category"] for d in rag_engine.documents))
    return {"categories": sorted(cats)}


@app.get("/api/docs-search")
async def search_docs(q: str = "", category: str = "", top_k: int = 5):
    """Search documentation directly without LLM."""
    if not rag_engine or not rag_engine.is_ready:
        return {"results": [], "query": q}

    query = q + (f" {category}" if category else "")
    results = rag_engine.retrieve(query, top_k=top_k)
    return {
        "results": [
            {
                "id":       r.doc_id,
                "title":    r.title,
                "category": r.category,
                "score":    round(r.score, 4),
                "tags":     r.tags,
                "content":  r.content,
            }
            for r in results
        ],
        "query": q,
        "count": len(results),
    }


@app.post("/api/single-run")
async def single_run(request: dict):
    """
    Single Run: detect language, actually execute the snippet on the system,
    auto-install missing Python packages, and return real terminal output.
    Accepts { snippet: str } → returns execution result (stdout/stderr/exit_code).
    """
    snippet = request.get("snippet", "").strip()
    if not snippet:
        raise HTTPException(status_code=400, detail="No snippet provided")

    validation_error = _validate_executable_script(snippet)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    start    = time.time()
    language = _detect_snippet_language(snippet)

    env      = os.environ.copy()
    pdk_root = _find_skywater_pdk()
    if pdk_root:
        env["PDK_ROOT"]    = pdk_root
        env["SKY130_ROOT"] = pdk_root

    result   = _run_snippet_with_autoinstall(snippet, language, env)

    commands = [
        l.strip() for l in snippet.splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]

    return {
        "stdout":              result["stdout"],
        "stderr":              result["stderr"],
        "exit_code":           result["exit_code"],
        "executor":            result["executor"],
        "language":            language,
        "pdk_root":            pdk_root,
        "elapsed":             result["elapsed"],
        "success":             result["exit_code"] == 0,
        "installed_packages":  result["installed_packages"],
        "command_count":       len(commands),
        "processing_time":     round(time.time() - start, 3),
    }


@app.post("/api/execute")
async def execute_script(request: Request):
    """
    Run All (Real Execution):
    Receives { script: str } — the concatenation of ALL code blocks from a response.
    Writes to a temp file, detects the right executor, and runs it on the system.
    Returns stdout, stderr, exit_code, executor used, and PDK info.
    """
    body = await request.json()
    script = body.get("script", "").strip()
    if not script:
        raise HTTPException(status_code=400, detail="No script provided")

    validation_error = _validate_executable_script(script)
    if validation_error:
        raise HTTPException(status_code=400, detail=validation_error)

    start = time.time()

    executor_kind, argv = _detect_executor(script)

    if executor_kind.startswith("none"):
        msg = "No compatible executor found on this system.\nInstall bash or powershell."
        if executor_kind == "none_tcl":
            msg = (
                "OpenROAD or tclsh was not found in your system PATH.\n"
                "Please install OpenROAD or Tcl natively to execute these EDA scripts."
            )
        return {
            "stdout":    "",
            "stderr":    msg,
            "exit_code": -1,
            "executor":  "none",
            "pdk_root":  None,
            "elapsed":   0,
            "success":   False,
        }

    pdk_root = _find_skywater_pdk()
    env      = os.environ.copy()
    if pdk_root:
        env["PDK_ROOT"]    = pdk_root
        env["SKY130_ROOT"] = pdk_root
        print(f"[Execute] PDK_ROOT auto-set → {pdk_root}")
    else:
        print("[Execute] skywater-pdk not found; PDK_ROOT not set")

    if executor_kind in ("openroad", "tclsh", "wsl_openroad"):
        suffix = ".tcl"
    elif executor_kind == "powershell":
        suffix = ".ps1"
    elif executor_kind == "wsl_shell":
        suffix = ".sh"  # won't be used as a file; kept for cleanup
    elif executor_kind == "python":
        suffix = ".py"
    else:
        suffix = ".sh"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding="utf-8"
    ) as tf:
        tf.write(script)
        tmp_path = tf.name

    # ── Detect GUI commands (they must be launched detached — they never exit) ──
    is_gui_cmd = "-gui" in script or "--gui" in script

    try:
        if executor_kind == "powershell":
            cmd = [argv[0], "-ExecutionPolicy", "Bypass", "-File", tmp_path]

        elif executor_kind == "wsl_shell":
            wsl_cmd = script.strip()
            pdk_prefix = ""
            if pdk_root:
                p = _windows_path_to_wsl(pdk_root)
                pdk_prefix = f"export PDK_ROOT={p} SKY130_ROOT={p}; "
            # Always set DISPLAY for WSLg when calling from Windows subprocess
            display_prefix = "export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0; "
            wsl_cmd = display_prefix + pdk_prefix + wsl_cmd
            cmd = ["wsl.exe", "-d", "Ubuntu", "--", "bash", "-c", wsl_cmd]

        elif executor_kind == "wsl_openroad":
            linux_path = _windows_path_to_wsl(tmp_path)
            cmd = ["wsl.exe", "-d", "Ubuntu", "--", "env", "DISPLAY=:0",
                   "WAYLAND_DISPLAY=wayland-0"]
            if pdk_root:
                p = _windows_path_to_wsl(pdk_root)
                cmd.extend([f"PDK_ROOT={p}", f"SKY130_ROOT={p}"])
            cmd.extend(["openroad", "-no_init", "-exit", linux_path])

        else:
            cmd = argv + [tmp_path]

        if is_gui_cmd and executor_kind in ("wsl_shell", "wsl_openroad"):
            # ── Detached launch — GUI apps never return ──────────────────────
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True,
            )
            stdout    = "OpenROAD GUI launched in WSL ✓\nThe window should appear via WSLg. If it doesn't, open your WSL terminal and run:\n  export DISPLAY=:0\n  openroad -gui"
            stderr    = ""
            exit_code = 0
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
                cwd=str(Path(tmp_path).parent),
            )
            stdout    = result.stdout or ""
            stderr    = result.stderr or ""
            exit_code = result.returncode

    except subprocess.TimeoutExpired:
        stdout, stderr, exit_code = "", "Execution timed out after 120 seconds.", -1
    except Exception as e:
        stdout, stderr, exit_code = "", f"Execution error: {e}", -1
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return {
        "stdout":    stdout,
        "stderr":    stderr,
        "exit_code": exit_code,
        "executor":  executor_kind,
        "pdk_root":  pdk_root,
        "elapsed":   round(time.time() - start, 3),
        "success":   exit_code == 0,
    }


@app.post("/api/rebuild-index")
async def rebuild_index():
    """Rebuild the FAISS index from documentation."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialized")
    try:
        rag_engine.rebuild_index()
        return {"status": "success", "doc_count": len(rag_engine.documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend static files
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
