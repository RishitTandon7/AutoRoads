# SDC for tinyRocket — Nangate45
# Standard commands only — no test-helper macros

create_clock -name core_clock -period 2.03 [get_ports clock]

set_input_delay  -clock core_clock 0.5 [all_inputs]
set_output_delay -clock core_clock 0.5 [all_outputs]
