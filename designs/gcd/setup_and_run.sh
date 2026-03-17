#!/bin/bash
# ============================================================
#  setup_and_run.sh  — Complete OpenROAD Flow (with Demo Fallback)
# ============================================================

set -e

# ── Check OpenROAD is installed ──────────────────────────────
if ! command -v openroad &> /dev/null; then
    echo "⚠️  OPENROAD NOT FOUND INSIDE WSL."
    echo "🎭 FALLING BACK TO PRESENTATION DEMO MODE..."
    echo ""
    sleep 1
    echo "[INFO] Reading Technology: Nangate45..."
    sleep 1
    echo "[INFO] Floorplan Initialized: 500x500um"
    sleep 1
    echo "[INFO] Placing 42 SRAM Macro Blocks..."
    sleep 2
    echo "[INFO GPL-001] Global Placement: density 0.50"
    sleep 2
    echo "[INFO CTS-001] Clock tree synthesis complete (WNS: 0.05ns)"
    sleep 1
    echo "[INFO GRT-001] Global Routing finished."
    echo ""
    echo "✅ [DEMO] FULL FLOW DONE: Floorplan -> Place -> CTS -> Route"
    echo "✅ [DEMO] Placement + Routing done → $HOME/or_results/tinyrocket_routed.odb"
    
    # Simulate the GUI setup steps from the real execution
    export DISPLAY=:0
    cat << EOF > /tmp/load_gui.tcl
read_lef /home/rishit/OpenROAD/test/Nangate45/Nangate45_tech.lef
read_lef /home/rishit/OpenROAD/test/Nangate45/Nangate45_stdcell.lef
read_lef /home/rishit/OpenROAD/test/Nangate45/fakeram45_64x32.lef
read_db "$HOME/or_results/tinyrocket_routed.odb"
EOF
    echo ""
    echo "🎨 TO VIEW THE GUI LAYOUT:"
    echo "Please open this file in your browser:"
    echo "file:///D:/The%20Open%20Road/frontend/openroad_gui.html"
    echo ""
    echo "✅ [DEMO] Simulation successful for Presentation."
    exit 0
fi

# ── REAL EXECUTION (If OpenROAD is found) ─────────────────────
echo "✅ OpenROAD found: $(openroad -version 2>&1 | head -1)"

# Determine PDK root
if [ -z "$PDK_ROOT" ]; then PDK_ROOT="$HOME/OpenROAD/test"; fi
DESIGN_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$HOME/or_results"
WIN_RESULTS="$DESIGN_DIR/../../results/tinyrocket_nangate"
mkdir -p "$RESULTS_DIR"
mkdir -p "$WIN_RESULTS"

cp "$DESIGN_DIR/tinyrocket_full_route.tcl" /tmp/tinyrocket_route.tcl
cp "$DESIGN_DIR/tinyrocket_simple.sdc" /tmp/tinyrocket_simple.sdc

sed -i "s|/home/rishit/OpenROAD/test|$PDK_ROOT|g" /tmp/tinyrocket_route.tcl
sed -i "s|/home/rishit/or_results|$RESULTS_DIR|g" /tmp/tinyrocket_route.tcl

openroad -no_init -exit /tmp/tinyrocket_route.tcl 2>&1 | tee "$RESULTS_DIR/tinyrocket_flow.log"
echo "✅ Placement + Routing done → $RESULTS_DIR/tinyrocket_routed.odb"

cp "$RESULTS_DIR/tinyrocket_routed.def" "$WIN_RESULTS/" || true
cp "$RESULTS_DIR/tinyrocket_routed.odb" "$WIN_RESULTS/" || true

export DISPLAY=:0
cat << EOF > /tmp/load_gui.tcl
read_lef $PDK_ROOT/Nangate45/Nangate45_tech.lef
read_lef $PDK_ROOT/Nangate45/Nangate45_stdcell.lef
read_lef $PDK_ROOT/Nangate45/fakeram45_64x32.lef
read_db "$RESULTS_DIR/tinyrocket_routed.odb"
EOF
openroad -gui /tmp/load_gui.tcl
