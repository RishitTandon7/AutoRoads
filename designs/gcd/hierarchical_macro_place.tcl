# ============================================================
#  Automatic Hierarchical Macro Placement — REAL OpenROAD Script
#  Uses the AES design + sky130hd files bundled with OpenROAD
#  Run:  openroad -no_init -exit /mnt/d/The\ Open\ Road/designs/gcd/hierarchical_macro_place.tcl
# ============================================================

# ── Point to the OpenROAD built-in test directory ────────────
set TEST_DIR "/home/rishit/OpenROAD/test"
set RESULTS  "/tmp/or_results"

# Create output dir (no spaces in path — avoids Tcl arg-splitting bug)
file mkdir $RESULTS

# ── 1. Read Technology LEF (tracks / layers / vias) ──────────
read_lef $TEST_DIR/sky130hd/sky130hd.tlef

# ── 2. Read Standard-Cell LEF (cell shapes and pins) ─────────
read_lef $TEST_DIR/sky130hd/sky130hd_std_cell.lef

# ── 3. Read Liberty timing library ───────────────────────────
read_liberty $TEST_DIR/sky130hd/sky130hd_tt.lib

# ── 4. Read the synthesised gate-level netlist ────────────────
read_verilog $TEST_DIR/aes_sky130hd.v
link_design aes_cipher_top

# ── 5. Apply timing constraints ──────────────────────────────
read_sdc /tmp/aes_simple.sdc

# ── 6. Floorplan ─────────────────────────────────────────────
initialize_floorplan \
    -die_area  {0 0 2000 2000} \
    -core_area {30 30 1770 1770} \
    -site      unithd

# ── 6b. Initialize routing tracks (REQUIRED before place_pins) ─
source $TEST_DIR/sky130hd/sky130hd.tracks
puts "INFO FP: Floorplan + tracks initialized."

# ── 7. I/O Pin placement (met3=horizontal, met2=vertical in sky130hd) ─
place_pins \
    -hor_layers met3 \
    -ver_layers met2
puts "INFO FP: I/O pins placed."

# ── 8. Power / Ground using sky130hd PDN config ──────────────
add_global_connection -net VDD -pin_pattern {^VPWR$} -power
add_global_connection -net VDD -pin_pattern {^VPB$}  -power
add_global_connection -net VSS -pin_pattern {^VGND$} -ground
add_global_connection -net VSS -pin_pattern {^VNB$}  -ground
global_connect

source $TEST_DIR/sky130hd/sky130hd.pdn.tcl
pdngen
puts "INFO PDN: Power distribution network generated."

# ── 9. HIERARCHICAL MACRO PLACEMENT ──────────────────────────
#  macro_placement only runs when the design actually contains macros.
#  The AES design is pure standard-cell, so we skip it gracefully.
# -------------------------------------------------------------
set macro_count [llength [get_cells -filter "is_macro == true"]]
puts "INFO MPL: Found $macro_count macro block(s)."

if {$macro_count > 0} {
    macro_placement \
        -halo_width  2.0 \
        -halo_height 2.0
    puts "INFO MPL: Hierarchical macro placement complete."
} else {
    puts "INFO MPL: No macros found — skipping macro_placement (not needed for standard-cell designs)."
}

# ── 11. Wire RC values (MUST be set before global_placement -timing_driven) ─
source $TEST_DIR/sky130hd/sky130hd.rc
set_wire_rc -layer met2          ;# signal wire RC
set_wire_rc -clock -layer met5   ;# clock wire RC

# ── 12. Global placement of standard cells ───────────────────
global_placement \
    -density     0.30 \
    -timing_driven

puts "INFO GPL: Global placement complete."

# ── 13. Estimate parasitic resistances / capacitances ────────
estimate_parasitics -placement

# ── 14. Repair design rule violations ────────────────────────
repair_design
repair_timing -hold -slack_margin 0.1
puts "INFO: Design repairs done."

# ── 13. Detailed placement (legalisation) ────────────────────
detailed_placement
check_placement -verbose
puts "INFO DPL: Detailed placement + legalisation done."

# ── 14. Clock Tree Synthesis ──────────────────────────────────
clock_tree_synthesis
repair_clock_nets

# repair_timing -hold is optional — catch any STA errors gracefully
if {[catch {repair_timing -hold -slack_margin 0.05} err]} {
    puts "WARNING: repair_timing -hold skipped: $err"
}
puts "INFO CTS: Clock tree synthesis done."

# ── 15. Reports (all wrapped in catch — non-fatal) ────────────
puts ""
puts "══════════════════════════════════════════════"
puts " DESIGN REPORTS"
puts "══════════════════════════════════════════════"
catch { report_design_area }
catch { report_power       }
catch { report_timing -path_count 5 }

# ── 16. Write output files (always runs) ──────────────────────
write_def  $RESULTS/aes_placed.def
write_db   $RESULTS/aes_placed.odb

puts ""
puts "✅ DONE. Output written to $RESULTS"
puts "   View in GUI:  openroad -gui"
puts "   Then run:     read_db $RESULTS/aes_placed.odb"
