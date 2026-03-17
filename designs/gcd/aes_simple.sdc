# SDC for aes_cipher_top — sky130hd @ ~267 MHz (3.74 ns period)
# Standard commands only — no test-helper macros

create_clock [get_ports clk] -name clk -period 3.74

# I/O delays (40% of period)
set_input_delay  -clock clk 1.5 [all_inputs]
set_output_delay -clock clk 1.5 [all_outputs]
