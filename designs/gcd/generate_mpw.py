import os

verilog_path = "d:/The Open Road/designs/gcd/mpw_shuttle.v"
tcl_path = "d:/The Open Road/designs/gcd/mpw_shuttle.tcl"
sh_path = "d:/The Open Road/designs/gcd/run_mpw.sh"

with open(verilog_path, "w") as f:
    f.write('''module mpw_shuttle(
  input clk,
  input ce,
  input we,
  input [5:0] addr,
  input [31:0] din
);

''')
    for i in range(42):
        f.write(f'''  fakeram45_64x32 sram_{i} (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
''')
    f.write("endmodule\n")

with open(tcl_path, "w") as f:
    f.write('''set TEST_DIR /home/rishit/OpenROAD/test

read_lef $TEST_DIR/Nangate45/Nangate45_tech.lef
read_lef $TEST_DIR/Nangate45/Nangate45_stdcell.lef
read_lef $TEST_DIR/Nangate45/fakeram45_64x32.lef
read_liberty $TEST_DIR/Nangate45/Nangate45_typ.lib
read_liberty $TEST_DIR/Nangate45/fakeram45_64x32.lib

read_verilog /mnt/d/The\\ Open\\ Road/designs/gcd/mpw_shuttle.v
link_design mpw_shuttle

initialize_floorplan -die_area {0 0 1000 900} -core_area {20 20 980 880} -site FreePDK45_38x28_10R_NP_162NW_34O
source $TEST_DIR/Nangate45/Nangate45.tracks

# Place the macros explicitly in a 6x7 grid
set pitch_x 110
set pitch_y 110
set start_x 30
set start_y 30

set block [ord::get_db_block]
set dbu [$block getDbUnitsPerMicron]

for {set row 0} {$row < 6} {incr row} {
  for {set col 0} {$col < 7} {incr col} {
    set i [expr {(${row} * 7) + ${col}}]
    set x_um [expr {$start_x + ($col * $pitch_x)}]
    set y_um [expr {$start_y + ($row * $pitch_y)}]
    
    set x_dbu [expr {int($x_um * $dbu)}]
    set y_dbu [expr {int($y_um * $dbu)}]
    
    set inst_name "sram_${i}"
    set inst [$block findInst $inst_name]
    $inst setOrigin $x_dbu $y_dbu
    $inst setOrient R0
    $inst setPlacementStatus FIRM
  }
}

# PDN
add_global_connection -defer_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDD$} -power
add_global_connection -defer_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDPE$} -power
add_global_connection -defer_connection -net {VDD} -inst_pattern {.*} -pin_pattern {^VDDCE$} -power
add_global_connection -defer_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSS$} -ground
add_global_connection -defer_connection -net {VSS} -inst_pattern {.*} -pin_pattern {^VSSE$} -ground
global_connect
source $TEST_DIR/Nangate45/Nangate45.pdn.tcl
pdngen

# IO Pins
place_pins -hor_layers metal3 -ver_layers metal2

# Standard Cell + Routing prep
source $TEST_DIR/Nangate45/Nangate45.rc
set_wire_rc -layer metal3
set_wire_rc -clock -layer metal6

global_placement -density 0.40 -timing_driven
estimate_parasitics -placement
clock_tree_synthesis -buf_list BUF_X4
global_route -congestion_iterations 20

puts "===== 42-MACRO WAFER MPW DONE ====="
write_db /home/rishit/or_results/mpw_shuttle.odb
''')

tcl_gui_path = "d:/The Open Road/designs/gcd/load_gui_mpw.tcl"
sh_path = "d:/The Open Road/designs/gcd/run_mpw.sh"

with open(tcl_gui_path, "w") as f:
    f.write('''read_lef /home/rishit/OpenROAD/test/Nangate45/Nangate45_tech.lef
read_lef /home/rishit/OpenROAD/test/Nangate45/Nangate45_stdcell.lef
read_lef /home/rishit/OpenROAD/test/Nangate45/fakeram45_64x32.lef
read_liberty /home/rishit/OpenROAD/test/Nangate45/Nangate45_typ.lib
read_liberty /home/rishit/OpenROAD/test/Nangate45/fakeram45_64x32.lib
read_db /home/rishit/or_results/mpw_shuttle.odb
''')

with open(sh_path, "w", newline='\n') as f:
    f.write('''#!/bin/bash
export DISPLAY=:0
cd "/mnt/d/The Open Road/designs/gcd"
openroad -no_init -exit mpw_shuttle.tcl

openroad -gui load_gui_mpw.tcl
''')
