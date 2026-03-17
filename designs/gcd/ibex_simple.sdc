# SDC for ibex_core — sky130hd 
# Standard commands only — no test-helper macros

create_clock -name core_clock -period 15.155 [get_ports clk_i]

# I/O delays
set_input_delay  -clock core_clock 6.0 [all_inputs]
set_output_delay -clock core_clock 6.0 [all_outputs]
