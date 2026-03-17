# Single Run CLI Mode

The **OpenROAD AI Assistant** supports a powerful Single Run CLI system that lets you query the RAG engine and local LLM directly from your terminal —no browser, no server, no setup friction. You can use it for quick questions, running entire generated scripts, or processing a batch of commands all at once.

---

## Modes at a Glance

| Mode | Command | When to Use |
|---|---|---|
| **Web Server** | `python run.py` | Full UI + API server |
| **Single Query** | `python run.py "query"` | Quick one-off questions |
| **Snippet Run** | `python run.py --run script.tcl` | Run a generated Tcl script through the AI |
| **Batch Run** | `python run.py --file queries.txt` | Multiple commands/queries at once |

---

## 🧠 Auto-Dependency Management (Agent Mode)

Every time you run `run.py`, the agent **automatically checks** whether all required Python packages are installed. If anything is missing, it installs it for you before proceeding — no manual `pip install` needed.

```
[Agent] Detected 2 missing package(s). Auto-installing...
  → Installing rich==13.9.4 ...
  ✓ Installed rich==13.9.4
  → Installing numpy==2.2.1 ...
  ✓ Installed numpy==2.2.1
[Agent] All dependencies resolved.
```

> [!NOTE]
> This works for all modes — single query, batch, snippet, and server. The agent always self-heals before running.

---

## 1 — Single Query Mode

Run a natural language query directly against the RAG engine and LLM.

```bash
python run.py "How do I do floorplanning in OpenROAD?"
```

```bash
python run.py "What does the set_global_routing_layer_adjustment command do?"
```

```bash
python run.py "Debug this error: ERROR (CTS-003): Max routing congestion reached"
```

The assistant will:
1. Initialize the TF-IDF RAG engine.
2. Retrieve the most relevant documentation chunks.
3. Feed your query + context to the local Ollama LLM.
4. Print the response and exit.

---

## 2 — Snippet Run Mode (`--run`)

If the assistant has already **generated a Tcl script** for you (via the web UI or an earlier query), you can feed it back directly for analysis, explanation, and optimization advice — in a single run.

```bash
python run.py --run my_generated_script.tcl
```

### What it does:
- **Single command in the file** → Explains the command and provides usage guidance.
- **Multiple commands in the file** → Analyzes the full flow, explains each step, flags issues, and suggests optimizations.

### Example Tcl snippet file (`place_design.tcl`):
```tcl
# Place the design
initialize_floorplan -utilization 75 -aspect_ratio 1.0
global_placement -timing_driven
detailed_placement
check_placement -verbose
```

Run it:
```bash
python run.py --run place_design.tcl
```

> [!TIP]
> This is the fastest way to verify a generated script. You don't need to open the browser — just save the output and pass it straight back to `run.py`.

---

## 3 — Batch Run Mode (`--file`)

If you have **many queries or commands** to process, put them all in a plain text file — one query per line — and run them all in one shot.

```bash
python run.py --file my_queries.txt
```

### Example batch file (`my_queries.txt`):
```
# OpenROAD study session — March 2026
What is the purpose of the global placement stage?
How do I set up clock tree synthesis in OpenROAD?
Generate a Tcl script for detailed routing with sky130 PDK
What does set_wire_rc do?
How do I fix hold violations after CTS?
```

- Lines starting with `#` are treated as **comments** and skipped.
- Each query is processed one at a time, with labeled headers showing progress.
- The same RAG engine instance is reused across all queries for efficiency.

---

## Running the Web Server (Default Mode)

Running without arguments starts the full FastAPI backend + frontend on port 8000:

```bash
python run.py
```

---

## Summary of Flags

```
python run.py                        → Start web server (default)
python run.py "query text"           → Single CLI run
python run.py --run  <file.tcl>      → Run/analyze a Tcl snippet
python run.py --file <queries.txt>   → Batch run all queries in file
```
