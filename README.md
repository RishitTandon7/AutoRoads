# 🛣️ OpenROAD AI Assistant - Project Guide

This project combines an AI RAG (Retrieval Augmented Generation) system with automated EDA (Electronic Design Automation) flow execution. Below is a guide on which scripts to run for different tasks.

---

## 🤖 1. The AI Assistant (Web & CLI)
Use these to interact with the OpenROAD documentation and generate/run Tcl snippets.

| File | Command | Description |
| :--- | :--- | :--- |
| **`run.py`** | `python run.py` | **Start the Web Server.** Access the AI UI at [localhost:8000](http://localhost:8000). |
| **`run.py`** | `python run.py "query"` | **Single Run CLI.** Ask a question about OpenROAD directly from terminal. |
| **`run.py`** | `python run.py --run snippet.tcl` | **Explanation Mode.** Analyzing a Tcl script and providing optimizations. |

---

## 🎨 2. Design Execution (The "Visual" Flows)
These scripts run full RTL-to-GDSII pipelines and launch the OpenROAD GUI to see the layouts.

### 🔳 42-Macro MPW Shuttle (Wafer View)
*Replicates the dense "blocky" look of EFabless MPW tapeout wafers.*
1. **`designs/gcd/generate_mpw.py`**: Run this first (Windows) to generate the procedurally placed 42-SRAM grid.
2. **`designs/gcd/run_mpw.sh`**: Run this in **WSL** (`bash run_mpw.sh`). It executes the flow and opens the GUI.

### 🚀 TinyRocket (SoC View)
*A full RISC-V SoC with integrated SRAM macros and standard cells.*
*   **`designs/gcd/setup_and_run.sh`**: Run this in **WSL**. It will run the `tinyrocket_full_route.tcl` flow and launch the GUI.

---

## ⚙️ 3. Backend & API
For developers looking to integrate the OpenROAD flow into other applications via REST.

| File | Description |
| :--- | :--- |
| **`backend/openroad_flow.py`** | Core Python module that handles the "Single-Run" logic (Tcl generation -> Subprocess -> Log Parsing). |
| **`backend/main.py`** | FastAPI entry point where the `/api/run-flow` endpoint is defined. |
| **`test_run.py`** | A standalone local test script to verify that the Python API can talk to the OpenROAD engine correctly. |

---

## 🛠️ Environment Requirements
- **WSL (Ubuntu)**: Required for running the actual OpenROAD binary.
- **X-Server (e.g., VcXsrv or GWSL)**: Must be running on Windows for the GUI to appear.
- **PDKs**: Assumes Nangate45 and Sky130 tracks are available in `/home/rishit/OpenROAD/test`.

---

> [!TIP]
> If you encounter a `DISPLAY` error, ensure you have set `export DISPLAY=:0` in your WSL terminal before running any `.sh` script.
