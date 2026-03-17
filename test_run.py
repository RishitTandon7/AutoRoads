from backend.openroad_flow import execute_openroad_flow, RunFlowRequest

req = dict(
    design_name="gcd",
    verilog_path="/home/rishit/OpenROAD/test/gcd_sky130hd.v",
    sdc_path="/mnt/d/The Open Road/valid_api_test.sdc",
    tech_lef_path="/home/rishit/OpenROAD/test/sky130hd/sky130hd.tlef",
    stdcell_lef_path="/home/rishit/OpenROAD/test/sky130hd/sky130hd_std_cell.lef",
    liberty_path="/home/rishit/OpenROAD/test/sky130hd/sky130hd_tt.lib",
    tracks_path="/home/rishit/OpenROAD/test/sky130hd/sky130hd.tracks",
    cts_buf_cell="sky130_fd_sc_hd__clkbuf_1",
    die_area="0 0 300 300",
    core_area="10 10 290 290",
    results_dir="/home/rishit/or_results"
)

try:
    request = RunFlowRequest(**req)
    response = execute_openroad_flow(request)
    print("STATUS:", response.status)
    print("MESSAGE:", response.message)
    print("TIMING:", response.timing_report)
    print("DEF PATH:", response.def_path)
    print("STDOUT:", response.log_output[-1000:])
    print("STDERR:", response.error_output[-1000:])
    
except Exception as e:
    import traceback
    traceback.print_exc()
