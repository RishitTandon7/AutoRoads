#!/bin/bash
# ============================================================
#  setup_and_run.sh  — Complete OpenROAD Flow in WSL (tinyRocket)
#  (Includes Macro Placement to show large SRAM blocks!)
# ============================================================

set -e   # stop on first error

# ── Check OpenROAD is installed ──────────────────────────────
if ! command -v openroad &> /dev/null; then
    echo "❌ ERROR: openroad not found in PATH."
    exit 1
fi
echo "✅ OpenROAD found: $(openroad -version 2>&1 | head -1)"

# ── Output dirs ───────────────────────────────────────────────
# Determine PDK root - try to find it automatically
if [ -z "$PDK_ROOT" ]; then
    PDK_ROOT="$HOME/OpenROAD/test"
fi

DESIGN_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$HOME/or_results"
WIN_RESULTS="$DESIGN_DIR/../../results/tinyrocket_nangate"
mkdir -p "$RESULTS_DIR"
mkdir -p "$WIN_RESULTS"

# ── Step 1: OpenROAD Full Flow + Routing ─────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  STEP 1: OpenROAD — Place + CTS + Macros + Route"
echo "  (Running tinyRocket: Shows large SRAM blocks!)"
echo "═══════════════════════════════════════════════════"
cp "$DESIGN_DIR/tinyrocket_full_route.tcl" /tmp/tinyrocket_route.tcl
cp "$DESIGN_DIR/tinyrocket_simple.sdc" /tmp/tinyrocket_simple.sdc

# Adjust paths in the TCL script to be portable
sed -i "s|/home/rishit/OpenROAD/test|$PDK_ROOT|g" /tmp/tinyrocket_route.tcl
sed -i "s|/home/rishit/or_results|$RESULTS_DIR|g" /tmp/tinyrocket_route.tcl

openroad -no_init -exit /tmp/tinyrocket_route.tcl 2>&1 | tee "$RESULTS_DIR/tinyrocket_flow.log"

echo "✅ Placement + Routing done → $RESULTS_DIR/tinyrocket_routed.odb"

# Copy to Windows side
cp "$RESULTS_DIR/tinyrocket_routed.def" "$WIN_RESULTS/" || true
cp "$RESULTS_DIR/tinyrocket_routed.odb" "$WIN_RESULTS/" || true

# ── Step 2: View result in GUI ───────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════"
echo "  STEP 2: OpenROAD GUI (Showing Macro Blocks & Congestion)"
echo "═══════════════════════════════════════════════════"
export DISPLAY=:0
cat << EOF > /tmp/load_gui.tcl
read_lef $PDK_ROOT/Nangate45/Nangate45_tech.lef
read_lef $PDK_ROOT/Nangate45/Nangate45_stdcell.lef
read_lef $PDK_ROOT/Nangate45/fakeram45_64x32.lef
read_liberty $PDK_ROOT/Nangate45/Nangate45_typ.lib
read_liberty $PDK_ROOT/Nangate45/fakeram45_64x32.lib
read_db "$RESULTS_DIR/tinyrocket_routed.odb"
EOF
openroad -gui /tmp/load_gui.tcl

echo ""
echo "✅ Done!"
