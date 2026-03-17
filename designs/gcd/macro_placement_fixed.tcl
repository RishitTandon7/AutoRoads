# ============================================================
#  Corrected Automatic Hierarchical Macro Placement (AHHMP)
#  Replaced 'run_ahhmp' with standard 'rtl_macro_placer'
# ============================================================

set TEST_DIR "/home/rishit/OpenROAD/test"
set RESULTS "/home/rishit/or_results"

# 1. Read Technology & Libraries
read_lef $TEST_DIR/Nangate45/Nangate45_tech.lef
read_lef $TEST_DIR/Nangate45/Nangate45_stdcell.lef
read_lef $TEST_DIR/Nangate45/fakeram45_64x32.lef

read_liberty $TEST_DIR/Nangate45/Nangate45_typ.lib
read_liberty $TEST_DIR/Nangate45/fakeram45_64x32.lib

# 2. Read Design
read_verilog $TEST_DIR/tinyRocket_nangate45.v
link_design RocketTile

# 3. Floorplan
initialize_floorplan \
    -die_area  {0 0 500 500} \
    -core_area {10 10 490 490} \
    -site      FreePDK45_38x28_10R_NP_162NW_34O

# 4. Corrected Macro Placement Command
# 'run_ahhmp' is replaced by 'rtl_macro_placer' in modern OpenROAD
rtl_macro_placer \
    -halo_width 10.0 \
    -halo_height 10.0

puts "INFO MPL: Hierarchical macro placement complete."

# 5. Run standard placement cleanup
detailed_placement
check_placement -verbose

# 6. Final parasitics estimation
estimate_parasitics -placement

puts "✅ FIXED: Macro placement successful using rtl_macro_placer."
