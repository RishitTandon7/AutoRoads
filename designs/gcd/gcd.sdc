# ============================================================
#  Timing Constraints — GCD Design (sky130 @ 100 MHz)
#  gcd.sdc — read by OpenROAD after read_verilog / link_design
# ============================================================

# Primary clock: 100 MHz → 10 ns period
create_clock -name clk -period 10 [get_ports clk]

# Input / output delays (40% of period)
set_input_delay  -clock clk 4.0 [all_inputs]
set_output_delay -clock clk 4.0 [all_outputs]

# False paths on async reset
set_false_path -from [get_ports reset]

# Drive strength for inputs
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 [all_inputs]
set_load 10.0 [all_outputs]
