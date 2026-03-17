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
DESIGN_DIR="/mnt/d/The Open Road/designs/gcd"
RESULTS_DIR="/home/rishit/or_results"
WIN_RESULTS="/mnt/d/The Open Road/results/tinyrocket_nangate"
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
cat << 'EOF' > /tmp/load_gui.tcl
read_lef /home/rishit/OpenROAD/test/Nangate45/Nangate45_tech.lef
read_lef /home/rishit/OpenROAD/test/Nangate45/Nangate45_stdcell.lef
read_lef /home/rishit/OpenROAD/test/Nangate45/fakeram45_64x32.lef
read_liberty /home/rishit/OpenROAD/test/Nangate45/Nangate45_typ.lib
read_liberty /home/rishit/OpenROAD/test/Nangate45/fakeram45_64x32.lib
read_db "/home/rishit/or_results/tinyrocket_routed.odb"
EOF
openroad -gui /tmp/load_gui.tcl

echo ""
echo "✅ Done!"
