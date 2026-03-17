# ============================================================
#  Automatic Hierarchical Macro Placement — Real OpenROAD Tcl
#  Uses: mpl2 (macro_placement), global_placement, detailed_placement
#  Run via:  openroad -no_init -exit this_file.tcl  (in WSL)
# ============================================================

# ── 1. Set PDK root (auto-detected from env, edit if needed) ─
set PDK_ROOT $::env(PDK_ROOT)
set LIB_DIR  $PDK_ROOT/sky130A/libs.ref/sky130_fd_sc_hd

# ── 2. Read technology LEF (tracks, layers, vias) ────────────
read_lef $LIB_DIR/lef/sky130_fd_sc_hd.tlef

# ── 3. Read standard-cell LEF (cell shapes & pins) ───────────
read_lef $LIB_DIR/lef/sky130_fd_sc_hd.lef

# ── 4. Read Liberty timing library ───────────────────────────
read_liberty $LIB_DIR/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

# ── 5. Read synthesised gate-level netlist ────────────────────
#       (supply your own .v from Yosys synthesis)
read_verilog /mnt/d/The\ Open\ Road/results/gcd/1_synth.v

# ── 6. Link / elaborate the top-level design ─────────────────
link_design gcd

# ── 7. Apply SDC timing constraints ──────────────────────────
read_sdc /mnt/d/The\ Open\ Road/designs/gcd/gcd.sdc

# ── 8. Floorplan — die/core area ────────────────────────────
initialize_floorplan \
    -utilization 40 \
    -aspect_ratio 1.0 \
    -core_space {5.0 5.0 5.0 5.0}

# ── 9. Place I/O pins around the boundary ────────────────────
place_pins -hor_layers met3 -ver_layers met2

# ── 10. Power Distribution Network (PDN) ─────────────────────
add_global_connection -net VDD -pin_pattern "^VPB$"  -power
add_global_connection -net VDD -pin_pattern "^VPWR$" -power
add_global_connection -net VSS -pin_pattern "^VNB$"  -ground
add_global_connection -net VSS -pin_pattern "^VGND$" -ground

pdngen

# ── 11. AUTOMATIC HIERARCHICAL MACRO PLACEMENT ───────────────
#  This is the real OpenROAD command (mpl2 tool).
#  set_macro_placement / replace_io are NOT valid commands.
#
#  Key options:
#    -halo_width     : keep-out margin around each macro (microns)
#    -halo_height    : keep-out height
#    -channel_width  : minimum routing channel between macros
#    -channel_height : minimum routing channel height
#    -fence_region   : optional bounding box to restrict placement
# --------------------------------------------------------------
macro_placement \
    -halo_width  4.0 \
    -halo_height 4.0

puts "INFO: Macro placement complete."

# ── 12. Global placement of standard cells ───────────────────
global_placement \
    -density 0.60 \
    -timing_driven \
    -skip_io

puts "INFO: Global placement done."

# ── 13. Estimate wire parasitics ─────────────────────────────
estimate_parasitics -placement

# ── 14. Repair design-rule and timing violations ─────────────
repair_design
repair_timing -hold -slack_margin 0.05

# ── 15. Detailed (legalisation) placement ────────────────────
detailed_placement
check_placement -verbose

puts "INFO: Detailed placement complete."

# ── 16. CTS — Clock Tree Synthesis ───────────────────────────
clock_tree_synthesis
repair_clock_nets
repair_timing -hold -slack_margin 0.05

puts "INFO: CTS complete."

# ── 17. Reports ──────────────────────────────────────────────
report_design_area
report_timing -path_count 5
report_power

# ── 18. Save the placed database ─────────────────────────────
write_def  /mnt/d/The\ Open\ Road/results/gcd/4_place.def
write_db   /mnt/d/The\ Open\ Road/results/gcd/4_place.odb

puts "INFO: All done. Files written to results/gcd/"
