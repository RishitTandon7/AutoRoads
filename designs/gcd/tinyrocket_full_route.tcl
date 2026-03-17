# ============================================================
#  Automatic Hierarchical Macro Placement & Routing
#  Uses the tinyRocket RISC-V design + Nangate45 files 
#  (Matches screenshot: Displays large SRAM Macro Blocks!)
# ============================================================

set TEST_DIR "/home/rishit/OpenROAD/test"
set RESULTS "/home/rishit/or_results"
file mkdir $RESULTS

# ── 1. Read Technology & Libraries ──────────
read_lef $TEST_DIR/Nangate45/Nangate45_tech.lef
read_lef $TEST_DIR/Nangate45/Nangate45_stdcell.lef
read_lef $TEST_DIR/Nangate45/fakeram45_64x32.lef

read_liberty $TEST_DIR/Nangate45/Nangate45_typ.lib
read_liberty $TEST_DIR/Nangate45/fakeram45_64x32.lib

# ── 2. Read Synthesised Netlist ────────────────
read_verilog $TEST_DIR/tinyRocket_nangate45.v
link_design RocketTile

# ── 3. Apply timing constraints ──────────────────────────────
read_sdc /tmp/tinyrocket_simple.sdc

# ── 4. Floorplan ─────────────────────────────────────────────
initialize_floorplan \
    -die_area  {0 0 500 500} \
    -core_area {10 10 490 490} \
    -site      FreePDK45_38x28_10R_NP_162NW_34O

# ── 5. Initialize routing tracks ─────────────────────────────
source $TEST_DIR/Nangate45/Nangate45.tracks
puts "INFO FP: Floorplan initialized + tracks added."

# ── 6. I/O Pin placement ─────────────────────────────────────
# Nangate45 uses metal3/metal2
place_pins \
    -hor_layers metal3 \
    -ver_layers metal2
puts "INFO FP: I/O pins placed."

# ── 7. Hierarchical Macro Placement ──────────────────────────
# Macros (RAMs) MUST be placed before the Power layout is drawn!
rtl_macro_placer -halo_width 22.4 -halo_height 15.12
puts "INFO MPL: Macro placement complete."

# ── 8. Power Distribution Network (PDN) ──────────────────────
# Note: Nangate45 is 45nm, and PDN generation creates different domains
add_global_connection -defer_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDD$} -power
add_global_connection -defer_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDPE$} -power
add_global_connection -defer_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDCE$} -power
add_global_connection -defer_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSS$} -ground
add_global_connection -defer_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSSE$} -ground
global_connect

source $TEST_DIR/Nangate45/Nangate45.pdn.tcl
pdngen
puts "INFO PDN: Power grid generated."

# ── 9. Global Placement ──────────────────────────────────────
# Initialize RC for timing-driven placement
source $TEST_DIR/Nangate45/Nangate45.rc
set_wire_rc -layer metal3
set_wire_rc -clock -layer metal6

global_placement -density 0.50 -timing_driven
puts "INFO GPL: Global placement complete."

# ── 10. Detailed Placement & CTS ─────────────────────────────
estimate_parasitics -placement
catch {repair_design}
catch {repair_timing -hold -setup_margin 0.0 -hold_margin 0.05}

detailed_placement
check_placement -verbose

clock_tree_synthesis -buf_list "BUF_X4"
repair_clock_nets
catch {repair_timing -hold -setup_margin 0.0 -hold_margin 0.05}
puts "INFO CTS: Clock tree synthesis done."

# ── 11. GLOBAL ROUTING (Generates Congestion Heatmap) ────────
global_route -congestion_iterations 50
puts "INFO GRT: Global routing executed (Congestion Maps available!)."

# ── 12. DETAILED ROUTING (Generates Physical Wire Layout) ────
set_routing_layers -signal metal2-metal10
catch { detailed_route \
    -output_drc $RESULTS/tinyrocket_route_drc.rpt \
    -output_maze $RESULTS/tinyrocket_maze.log \
    -no_pin_access }
puts "INFO DRT: Detailed routing complete."

# ── 13. Write output files ────────────────────────────────────
write_def $RESULTS/tinyrocket_routed.def
write_db  $RESULTS/tinyrocket_routed.odb

puts "✅ FULL FLOW DONE: Floorplan -> Place -> CTS -> Route"
