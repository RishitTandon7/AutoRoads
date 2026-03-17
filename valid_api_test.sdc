create_clock -name core_clock -period 20.0 [get_ports clk]
set_input_delay  -clock [get_clocks core_clock] 2.0 [all_inputs]
set_output_delay -clock [get_clocks core_clock] 2.0 [all_outputs]
