#!/bin/bash
# ============================================================
#  run_mpw.sh  — Launch the MPW Shuttle (Wafer View) Flow
# ============================================================

export DISPLAY=:0

# Determine script directory
DESIGN_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DESIGN_DIR"

# Run OpenROAD flow
openroad -no_init -exit mpw_shuttle.tcl

# Launch the visualizer GUI
openroad -gui load_gui_mpw.tcl
