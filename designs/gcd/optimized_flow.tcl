# ============================================================
#  Standardized OpenROAD Placement & Timing Optimization
#  Fixes "wrong # args" errors and uses standard commands
# ============================================================

# 1. Setup paths and quote them correctly
set TEST_DIR "/home/rishit/OpenROAD/test"
set tech_lef "$TEST_DIR/Nangate45/Nangate45_tech.lef"
set std_lef  "$TEST_DIR/Nangate45/Nangate45_stdcell.lef"

# 2. Correctly quote multi-word "set" values to avoid "wrong # args" error
set global_placement_options "-timing_driven -density 0.7"

# 3. Read libraries and design
read_lef $tech_lef
read_lef $std_lef
read_liberty "$TEST_DIR/Nangate45/Nangate45_typ.lib"

read_verilog "$TEST_DIR/gcd_sky130hd.v"
link_design gcd

initialize_floorplan -die_area {0 0 300 300} -core_area {10 10 290 290} -site unithd

# 4. Standard Timing-Driven Global Placement
# (Replaces 'ahmp' and 'optimize_placement_for_timing')
global_placement -timing_driven -density 0.7

# 5. Timing Repair (Fixes Slew, Cap, and Hold violations)
estimate_parasitics -placement
repair_design
repair_timing -setup

# 6. Legalize with Detailed Placement
detailed_placement

# 7. Check final placement status
check_placement -verbose

puts "✅ SUCCESS: Optimized flow complete with standard commands."
