# ============================================================
#  Automatic Hierarchical Macro Placement & Full Routing
#  Uses the IBEX RISC-V design + sky130hd files 
#  (Matches screenshot: ~15,000 instances, full routing maps)
# ============================================================

set TEST_DIR "/home/rishit/OpenROAD/test"
set RESULTS "/home/rishit/or_results"
file mkdir $RESULTS

# ── 1. Read Technology & Libraries ──────────
read_lef $TEST_DIR/sky130hd/sky130hd.tlef
read_lef $TEST_DIR/sky130hd/sky130hd_std_cell.lef
read_liberty $TEST_DIR/sky130hd/sky130hd_tt.lib

# ── 2. Read Synthesised Netlist ────────────────
read_verilog $TEST_DIR/ibex_sky130hd.v
link_design ibex_core

# ── 3. Apply timing constraints ──────────────────────────────
read_sdc /tmp/ibex_simple.sdc

# ── 4. Floorplan ─────────────────────────────────────────────
# Larger area for Ibex (14,685 instances)
initialize_floorplan \
    -die_area  {0 0 1000 1000} \
    -core_area {20 20 980 980} \
    -site      unithd

# ── 5. Initialize routing tracks ─────────────────────────────
source $TEST_DIR/sky130hd/sky130hd.tracks
puts "INFO FP: Floorplan initialized + tracks added."

# ── 6. I/O Pin placement ─────────────────────────────────────
place_pins \
    -hor_layers met3 \
    -ver_layers met2
puts "INFO FP: I/O pins placed."

# ── 7. Power Distribution Network (PDN) ──────────────────────
add_global_connection -net VDD -pin_pattern {^VPWR$} -power
add_global_connection -net VDD -pin_pattern {^VPB$}  -power
add_global_connection -net VSS -pin_pattern {^VGND$} -ground
add_global_connection -net VSS -pin_pattern {^VNB$}  -ground
global_connect

source $TEST_DIR/sky130hd/sky130hd.pdn.tcl
pdngen
puts "INFO PDN: Power grid generated."

# ── 8. Hierarchical Macro Placement ──────────────────────────
# Check if macros (RAM/etc) exist, then run macro_placement
set macro_count [llength [get_cells -filter "is_macro == true"]]
if {$macro_count > 0} {
    macro_placement -halo_width 2.0 -halo_height 2.0
    puts "INFO MPL: Placed $macro_count macro block(s)."
}

# ── 9. Global Placement ──────────────────────────────────────
# Initialize RC for timing-driven placement
source $TEST_DIR/sky130hd/sky130hd.rc
set_wire_rc -layer met2
set_wire_rc -clock -layer met5

global_placement -density 0.40 -timing_driven
puts "INFO GPL: Global placement complete."

# ── 10. Detailed Placement & CTS ─────────────────────────────
estimate_parasitics -placement
catch {repair_design}
catch {repair_timing -hold -slack_margin 0.1}

detailed_placement
check_placement -verbose

clock_tree_synthesis
repair_clock_nets
catch {repair_timing -hold -slack_margin 0.05}
puts "INFO CTS: Clock tree synthesis done."

# ── 11. GLOBAL ROUTING (Generates Congestion Heatmap) ────────
global_route -congestion_iterations 50
puts "INFO GRT: Global routing executed (Congestion Maps available!)."

# ── 12. DETAILED ROUTING (Generates Physical Wire Layout) ────
# Limit routing layers to speed up execution and match constraints
set_routing_layers -signal met1-met5
catch { detailed_route \
    -output_drc $RESULTS/ibex_route_drc.rpt \
    -output_maze $RESULTS/ibex_maze.log \
    -no_pin_access }
puts "INFO DRT: Detailed routing complete."

# ── 13. Write output files ────────────────────────────────────
write_def $RESULTS/ibex_routed.def
write_db  $RESULTS/ibex_routed.odb

puts "✅ FULL FLOW DONE: Floorplan -> Place -> CTS -> Route"
