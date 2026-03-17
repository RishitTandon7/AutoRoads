"""
OpenROAD Curated Knowledge Base
Comprehensive documentation chunks for RAG indexing
"""

OPENROAD_DOCS = [
    # ===== OVERVIEW =====
    {
        "id": "overview_001",
        "title": "OpenROAD Project Overview",
        "category": "overview",
        "content": """
OpenROAD is an open-source, integrated chip physical design tool that performs RTL-to-GDSII translation using open-source components.
The OpenROAD application is the core of the OpenROAD flow and provides an integrated framework for:
- Floorplanning
- Placement (global and detailed)
- Clock Tree Synthesis (CTS)
- Global Routing
- Detailed Routing
- Parasitic Extraction
- Timing Analysis

OpenROAD uses a Tcl scripting interface to drive the design flow. Users can run individual steps
or chain them together in a complete flow script. The tool is built around the OpenDB database
which stores the design state throughout the flow.
        """,
        "tags": ["overview", "rtl-to-gdsii", "flow", "introduction"]
    },
    {
        "id": "overview_002",
        "title": "OpenROAD RTL-to-GDSII Flow Stages",
        "category": "overview",
        "content": """
The complete RTL-to-GDSII flow in OpenROAD consists of these stages:

1. **Logic Synthesis** (Yosys) - Convert RTL Verilog to gate-level netlist
2. **Floorplanning** (init_floorplan) - Define die/core area, aspect ratio, utilization
3. **I/O Placement** (place_pins) - Place I/O pins on the chip boundary
4. **PDN Generation** (pdngen) - Create power distribution network
5. **Global Placement** (global_placement) - First-pass placement of standard cells
6. **Resize/Optimization** (repair_design) - Fix setup/hold timing, max fanout, capacitance
7. **Detailed Placement** (detailed_placement) - Legalize cell positions on placement grid
8. **Clock Tree Synthesis** (clock_tree_synthesis) - Build balanced clock trees
9. **Clock Network Repair** (repair_clock_nets) - Fix clock network timing
10. **Global Routing** (global_route) - Route approximate wire paths
11. **Antenna Repair** (repair_antenna) - Fix antenna DRC violations
12. **Detailed Routing** (detailed_route) - Final wire routing
13. **Parasitic Extraction** (estimate_parasitics) - Extract RC parasitics
14. **Timing Signoff** (report_timing) - Generate final timing reports
15. **GDSII Export** (write_gds) - Export to GDSII format
        """,
        "tags": ["flow", "stages", "rtl-to-gdsii", "overview"]
    },

    # ===== FLOORPLANNING =====
    {
        "id": "floor_001",
        "title": "Floorplanning with init_floorplan",
        "category": "floorplanning",
        "content": """
The init_floorplan command initializes the floorplan for a design. It sets up the die area,
core area, and basic chip dimensions.

**Syntax:**
```tcl
init_floorplan
  -utilization <float>        # Core utilization percentage (0-100)
  -aspect_ratio <float>       # Height/Width ratio of the core
  -core_space <float>         # Space between die and core boundary (microns)
  [-die_area {x0 y0 x1 y1}]  # Explicit die area in microns
  [-core_area {x0 y0 x1 y1}] # Explicit core area in microns
  [-site <site_name>]         # Placement site name from LEF
```

**Example - Utilization-based:**
```tcl
init_floorplan \
  -utilization 30 \
  -aspect_ratio 1.0 \
  -core_space 2.0
```

**Example - Explicit die area:**
```tcl
init_floorplan \
  -die_area {0 0 200.0 200.0} \
  -core_area {10 10 190 190}
```

The utilization specifies what fraction of the core area will be occupied by standard cells.
Lower utilization means more whitespace and easier routing. Typical values are 30-70%.
        """,
        "tags": ["floorplan", "init_floorplan", "utilization", "die_area", "core_area"]
    },
    {
        "id": "floor_002",
        "title": "I/O Pin Placement with place_pins",
        "category": "floorplanning",
        "content": """
The place_pins command places I/O pins on the boundaries of the chip. This is a critical step
before global placement.

**Syntax:**
```tcl
place_pins
  -hor_layers <layer_list>    # Horizontal pin layers
  -ver_layers <layer_list>    # Vertical pin layers
  [-random]                   # Random pin placement
  [-corner_avoidance <float>] # Distance to avoid corners (microns)
  [-min_distance <float>]     # Minimum distance between pins (microns)
```

**Example:**
```tcl
place_pins \
  -hor_layers metal2 \
  -ver_layers metal3
```

**Example with distance control:**
```tcl
place_pins \
  -hor_layers {metal2 metal4} \
  -ver_layers {metal3 metal5} \
  -corner_avoidance 1 \
  -min_distance 0.4
```

Pins should be placed after floorplan initialization. The layers specified must exist in your
technology LEF file. Horizontal layers are used for pins on top/bottom edges, vertical layers
for left/right edges.
        """,
        "tags": ["place_pins", "io_placement", "pins", "floorplan"]
    },
    {
        "id": "floor_003",
        "title": "Power Distribution Network Generation",
        "category": "floorplanning",
        "content": """
The pdngen command generates the power distribution network (PDN). PDN connects VDD and GND
rails across the chip to supply power to all cells.

**Basic PDN setup in Tcl:**
```tcl
# Define PDN configuration
set pdnconfig {
  pdngen::specify_grid stdcell {
    rails {
      metal1 {width 0.17 pitch 2.4 offset 0}
    }
    straps {
      metal4 {width 1.6 pitch 50.0 offset 2}
      metal7 {width 1.6 pitch 50.0 offset 2}
    }
    connect {{metal1 metal4} {metal4 metal7}}
  }
}
pdngen
```

**Key PDN concepts:**
- **Rails**: Horizontal power/ground stripes running through each standard cell row (usually metal1)
- **Straps**: Wider power/ground stripes running vertically or horizontally on upper metal layers
- **Rings**: Power rings around macros or the entire core
- **Connect**: Specifies which layer pairs to connect with vias

**Voltage domains:**
- VDD: Positive supply
- VSS/GND: Ground reference
        """,
        "tags": ["pdngen", "power", "pdn", "vdd", "gnd", "rails", "straps"]
    },

    # ===== PLACEMENT =====
    {
        "id": "place_001",
        "title": "Global Placement with global_placement",
        "category": "placement",
        "content": """
Global placement distributes standard cells across the chip floorplan, minimizing wire length
while respecting density constraints. OpenROAD uses RePlAce (via replace_io) for global placement.

**Syntax:**
```tcl
global_placement
  [-timing_driven]            # Enable timing-driven placement
  [-density <float>]          # Target cell density (0-1), default 0.7
  [-pad_left <int>]           # Left padding in placement grid units
  [-pad_right <int>]          # Right padding in placement grid units
  [-skip_initial_place]       # Skip initial placement step
  [-overflow <float>]         # Overflow threshold
```

**Example - Basic:**
```tcl
global_placement -skip_initial_place
```

**Example - Timing driven with density:**
```tcl
global_placement \
  -timing_driven \
  -density 0.6 \
  -pad_left 2 \
  -pad_right 2
```

After global placement, cells overlap each other. Detailed placement (legalization) must be run
next to ensure cells are on valid grid sites and don't overlap.

**Common issues:**
- High overflow: Reduce density or increase core area
- Poor timing: Use -timing_driven flag, adjust utilization
        """,
        "tags": ["global_placement", "placement", "density", "timing_driven", "replace"]
    },
    {
        "id": "place_002",
        "title": "Detailed Placement and Legalization",
        "category": "placement",
        "content": """
Detailed placement legalizes the cell positions from global placement. Cells are moved to valid
placement sites, overlaps are resolved, and design rules are met.

**Key commands:**
```tcl
# Legalize cell positions
detailed_placement

# Check placement validity
check_placement -verbose

# Optimize placement for timing
optimize_mirroring
```

**repair_design - Fix timing and design rule violations:**
```tcl
repair_design
  [-max_wire_length <float>]  # Maximum wire length (microns)
  [-max_slew_margin <float>]  # Setup slew margin (%)
  [-max_cap_margin <float>]   # Cap margin (%)
```

**Example flow after global placement:**
```tcl
global_placement -timing_driven

# Estimate parasitics for repair
estimate_parasitics -placement

# Fix design rule violations
repair_design

# Legalize
detailed_placement

# Verify
check_placement -verbose
```

Detailed placement uses OpenDP (from the ioPlacer suite) for legalization.
        """,
        "tags": ["detailed_placement", "legalization", "repair_design", "check_placement"]
    },

    # ===== CLOCK TREE SYNTHESIS =====
    {
        "id": "cts_001",
        "title": "Clock Tree Synthesis with clock_tree_synthesis",
        "category": "cts",
        "content": """
Clock Tree Synthesis (CTS) builds a balanced clock distribution network. OpenROAD uses TritonCTS
for this step. CTS inserts clock buffers to balance skew and meet timing constraints.

**Syntax:**
```tcl
clock_tree_synthesis
  -root_buf <buffer_cell>     # Buffer cell for root of clock tree
  -buf_list <buffer_list>     # List of allowed buffer cells
  [-wire_unit <float>]        # Unit wire resistance (ohm/unit)
  [-clk_nets <net_list>]      # Specific clock nets to synthesize
  [-distance_between_buffers <float>]  # Max buffer distance (microns)
  [-branching_point_buffers_distance <float>]  # Branching point distance
```

**Example:**
```tcl
clock_tree_synthesis \
  -root_buf CLKBUF_1 \
  -buf_list {CLKBUF_1 CLKBUF_2 CLKBUF_4 CLKBUF_8} \
  -clk_nets {clk} \
  -distance_between_buffers 100
```

**Post-CTS steps:**
```tcl
# Legalize buffers inserted by CTS
detailed_placement

# Repair clock network timing
repair_clock_nets

# Fix hold/setup timing
estimate_parasitics -placement
repair_timing
```

**Key metrics to check after CTS:**
- Clock skew: should be < 100ps typically
- Clock latency: total delay from clock source to flip-flop
- Tree depth: number of buffer levels
        """,
        "tags": ["cts", "clock_tree_synthesis", "tritoncts", "clock", "skew", "buffer"]
    },
    {
        "id": "cts_002",
        "title": "Timing Repair and Optimization",
        "category": "cts",
        "content": """
After CTS, timing violations may exist that need to be fixed. OpenROAD provides commands for
repairing setup and hold violations.

**repair_timing - Fix setup/hold violations:**
```tcl
repair_timing
  [-setup]                    # Repair setup violations
  [-hold]                     # Repair hold violations
  [-slack_margin <float>]     # Target slack margin (seconds)
  [-allow_setup_violations]   # Allow setup violations during hold fix
  [-max_buffer_percent <float>]  # Max area increase from buffering (%)
```

**Example:**
```tcl
# Repair setup violations
repair_timing -setup -slack_margin 0.0

# Repair hold violations (use hold buffers)
repair_timing -hold -allow_setup_violations

# Re-legalize after timing repair
detailed_placement
```

**Reporting timing:**
```tcl
# Report worst negative slack paths
report_timing -path_delay max -slack_max -0.0 -fields {slew cap input nets fanout} -format full_clock_expanded

# Report all paths with violations
report_timing -path_delay max -group_count 10

# Check timing constraints
check_setup_timing
```

**Common timing metrics:**
- WNS (Worst Negative Slack): Most critical timing violation
- TNS (Total Negative Slack): Sum of all negative slacks
- WHS (Worst Hold Slack): Worst hold violation
        """,
        "tags": ["repair_timing", "setup", "hold", "wns", "tns", "slack", "timing"]
    },

    # ===== ROUTING =====
    {
        "id": "route_001",
        "title": "Global Routing with global_route",
        "category": "routing",
        "content": """
Global routing finds approximate paths for all wires. It determines which routing tracks each
net will use on each routing layer without specifying exact geometry.

**Syntax:**
```tcl
global_route
  [-congestion_iterations <int>]    # Number of congestion iterations
  [-congestion_report_file <file>]  # Write congestion report
  [-guide_clean_threshold <float>]  # Minimum wire length to keep
  [-overflow_iterations <int>]      # Overflow reduction iterations
  [-verbose]                        # Enable verbose output
  [-allow_congestion]               # Allow routing congestion
```

**Example:**
```tcl
global_route \
  -congestion_iterations 100 \
  -verbose
```

**Check routing congestion:**
```tcl
# Report routing congestion
report_route_congestion

# Check routing guides
check_route_congestion
```

**Layer adjustments:**
```tcl
# Adjust routing resources per layer
set_global_routing_layer_adjustment metal1 0.5
set_global_routing_layer_adjustment metal2 0.3

# Set layer RC values
set_layer_rc -layer metal1 -resistance 1.67e-4 -capacitance 1.5e-4
```

**Common issues:**
- Routing congestion: Increase iterations, adjust layer resources, improve placement
- DRC violations in global route guides: Adjust routing rules
        """,
        "tags": ["global_route", "routing", "congestion", "guides"]
    },
    {
        "id": "route_002",
        "title": "Detailed Routing with detailed_route",
        "category": "routing",
        "content": """
Detailed routing converts global routing guides into actual physical wires meeting all DRC rules.
OpenROAD uses TritonRoute for detailed routing.

**Syntax:**
```tcl
detailed_route
  [-param <file>]             # TritonRoute parameter file
  [-output_drc <file>]        # Output DRC report file
  [-output_maze <file>]       # Output maze routing file
  [-verbose <int>]            # Verbosity level (0-5)
  [-bottom_routing_layer <layer>]  # Lowest routing layer
  [-top_routing_layer <layer>]     # Highest routing layer
  [-droute_end_iter <int>]    # Maximum routing iterations
```

**Example:**
```tcl
detailed_route \
  -output_drc ./reports/route.drc \
  -droute_end_iter 64 \
  -verbose 0
```

**Repair antenna violations:**
```tcl
# Before detailed routing
repair_antenna

# Or during routing workflow
global_route
repair_antenna
detailed_placement
detailed_route
```

**Check DRC after routing:**
```tcl
# Report DRC violations
check_drc
report_drc_violations

# Report via count statistics
report_wire_length
```

**TritonRoute parameter file example:**
```
guide ./results/route.guide
outputguide ./results/output.guide
outputDRC ./results/route.drc
threads 8
verbose 1
```
        """,
        "tags": ["detailed_route", "tritonroute", "drc", "antenna", "routing"]
    },
    {
        "id": "route_003",
        "title": "Antenna Violations and Repair",
        "category": "routing",
        "content": """
Antenna violations occur during manufacturing when long metal wires act as antennas and collect
charge that can damage gate oxide. OpenROAD detects and repairs these automatically.

**Check for antenna violations:**
```tcl
check_antennas -report_violating_nets
```

**Repair antenna violations:**
```tcl
repair_antenna
```

**During routing flow:**
```tcl
# 1. Run global routing
global_route -congestion_iterations 100

# 2. Repair antenna violations after global route
repair_antenna

# 3. Re-legalize if diodes were inserted
detailed_placement

# 4. Run detailed routing
detailed_route -output_drc ./reports/detailed.drc
```

**Antenna ratio:**
- Metal antenna ratio = cumulative metal area / gate oxide area
- Via antenna ratio = via area / gate oxide area
- Standard limits vary by technology (e.g., 400:1 for metal, 50:1 for vias)

**Repair methods:**
1. Insert antenna diodes (extra cells connected to net)
2. Use jumper via to break long metal runs
3. Use wire spreading to reduce sequential antenna accumulation
        """,
        "tags": ["antenna", "repair_antenna", "drc", "manufacturing", "diode"]
    },

    # ===== READING DESIGN =====
    {
        "id": "read_001",
        "title": "Reading Design Files - LEF, DEF, Liberty",
        "category": "design_input",
        "content": """
Before running any OpenROAD flow steps, you must read in the design files.

**Reading LEF files (Library Exchange Format):**
```tcl
# Read technology/process LEF (always first)
read_lef ./pdk/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.tlef

# Read cell LEF (standard cells)
read_lef ./pdk/sky130A/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
```

**Reading Liberty files (timing library):**
```tcl
# Read timing library for synthesis corner
read_liberty ./pdk/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
```

**Reading Verilog netlist:**
```tcl
# Link synthesized Verilog to design
read_verilog ./results/synth/design.v
link_design <top_module_name>
```

**Reading DEF file:**
```tcl
# Read existing DEF placement file
read_def ./results/floorplan/design.def
```

**Reading SDC constraints:**
```tcl
# Read timing constraints
read_sdc ./constraints/design.sdc
```

**Complete setup example:**
```tcl
# Technology and cell libraries
read_lef $techLefFile
read_lef $cellLefFile
read_liberty $libFile

# Design netlist
read_verilog $verilogFile
link_design $designName

# Timing constraints
read_sdc $sdcFile
```
        """,
        "tags": ["read_lef", "read_def", "read_liberty", "read_verilog", "link_design", "input", "files"]
    },
    {
        "id": "read_002",
        "title": "Writing Output Files - DEF, GDSII, Verilog",
        "category": "design_output",
        "content": """
After completing design stages, you can write out results in various formats.

**Write DEF (Design Exchange Format):**
```tcl
write_def ./results/floorplan/design.def
```

**Write Verilog netlist:**
```tcl
write_verilog ./results/synth/design_final.v
```

**Write GDSII (final output):**
```tcl
# Requires KLayout or magic for GDSII merge
write_gds -merge_pdk_gds $mergeFile ./results/final.gds
```

**Write SDC (timing constraints):**
```tcl
write_sdc ./results/design.sdc
```

**Write timing reports:**
```tcl
# Write setup timing report
report_timing -path_delay max > ./reports/timing_setup.rpt

# Write hold timing report
report_timing -path_delay min > ./reports/timing_hold.rpt
```

**Save design snapshot:**
```tcl
# Save OpenDB binary
write_db ./results/design_checkpoint.odb
# Load it back later
read_db ./results/design_checkpoint.odb
```
        """,
        "tags": ["write_def", "write_gds", "write_verilog", "output", "gdsii", "odb"]
    },

    # ===== TIMING =====
    {
        "id": "timing_001",
        "title": "Timing Analysis and Reporting",
        "category": "timing",
        "content": """
OpenROAD uses OpenSTA for static timing analysis. Timing analysis checks that all signals
arrive at their destinations within clock cycle constraints.

**Basic timing commands:**
```tcl
# Estimate parasitics for timing
estimate_parasitics -placement  # After placement
estimate_parasitics -global_routing  # After global routing

# Report timing summary
report_checks -path_delay max -slack_max 0.0
report_wns  # Worst Negative Slack
report_tns  # Total Negative Slack

# Detailed timing path report
report_checks \
  -path_delay max \
  -fields {slew cap input nets fanout} \
  -format full_clock_expanded \
  -group_count 5
```

**Setup timing (hold-path max delay):**
```tcl
report_timing -path_delay max -slack_max 0.0
```

**Hold timing (min delay):**
```tcl
report_timing -path_delay min -slack_min 0.0
```

**Timing constraints (SDC format):**
```tcl
# Define clock
create_clock -name clk -period 10.0 -waveform {0 5} [get_ports clk]

# Input/output delays
set_input_delay  -clock clk 2.0 [get_ports {in_*}]
set_output_delay -clock clk 2.0 [get_ports {out_*}]

# Driving cell
set_driving_cell -lib_cell sky130_fd_sc_hd__inv_2 -pin Y [all_inputs]

# Load capacitance
set_load 0.01 [all_outputs]
```
        """,
        "tags": ["timing", "report_timing", "wns", "tns", "setup", "hold", "slack", "opensta", "sdc"]
    },

    # ===== COMMON ERRORS =====
    {
        "id": "error_001",
        "title": "Common OpenROAD Errors - Floorplanning",
        "category": "debugging",
        "content": """
Common floorplanning errors and solutions in OpenROAD:

**Error: [ERROR ODB-0229] LEF file not found**
```
[ERROR ODB-0229] LEF file not found: /path/to/file.lef
```
Solution: Verify the LEF file path exists. Check for typos in the path. Ensure the file has read permissions.

**Error: [ERROR FLW-0004] Design not linked**
```
[ERROR FLW-0004] Design must be linked before floorplanning
```
Solution: Run `link_design <top_module_name>` before calling `init_floorplan`.

**Error: [ERROR IFP-0001] Illegal aspect ratio**
```
[ERROR IFP-0001] Illegal aspect ratio: must be between 0.1 and 10
```
Solution: Adjust the `-aspect_ratio` parameter to be between 0.1 and 10.0.

**Error: [ERROR IFP-0024] No floorplan found**
```
[ERROR IFP-0024] No floorplan found. Run init_floorplan first
```
Solution: Initialize the floorplan before placing pins or other operations.

**Error: [ERROR ODB-0432] Site not found**
```
[ERROR ODB-0432] Site 'core' not found in LEF
```
Solution: Check available sites in your LEF: `puts [[[ord::get_db_tech] findSite "core"] getName]`. Use the correct site name.

**Warning: Placement utilization too high**
```
[WARNING GPL-0042] Illegal overflow detected
```
Solution: Reduce utilization (increase core area or reduce cell density), or add more pads/macaros placement.
        """,
        "tags": ["error", "floorplan", "debugging", "lef", "site", "utilization"]
    },
    {
        "id": "error_002",
        "title": "Common OpenROAD Errors - Routing",
        "category": "debugging",
        "content": """
Common routing errors and solutions in OpenROAD:

**Error: [ERROR GRT-0045] Insufficient routing resources**
```
[ERROR GRT-0045] Routing layer metal1 has insufficient routing resources
```
Solution:
- Increase core area
- Adjust layer usage with `set_global_routing_layer_adjustment`
- Reduce placement density
- Use more routing layers

**Error: [ERROR DRT-0022] Routing DRC violations**
```
[ERROR DRT-0022] 15 DRC violations remain after detailed routing
```
Solution:
- After detailed routing, check the DRC report: `check_drc`
- Re-run with more iterations: `-droute_end_iter 100`
- Some violations may require manual intervention or PDK rule fixes

**Error: [ERROR ANT-0001] Antenna violations detected**
```
[ERROR ANT-0001] Antenna violation: net clk ratio 523 > limit 400
```
Solution:
- Run `repair_antenna` after global routing
- Insert antenna diodes near gate inputs
- Break long metal nets with jumper vias

**Error: Routing congestion hotspot**
```
[WARNING GRT-0048] Congestion in region (x1,y1)-(x2,y2): overflow 1.25
```
Solution:
- Increase congestion iterations
- Identify and spread dense placement areas
- Use layer adjustments in congested region
- Check for routing blockages

**DRC violation types:**
- Short: Two wires on same layer overlap
- Space: Wires too close together
- Width: Wire narrower than minimum
- Enclosure: Via not properly enclosed
        """,
        "tags": ["error", "routing", "drc", "antenna", "congestion", "debugging"]
    },
    {
        "id": "error_003",
        "title": "Common OpenROAD Errors - Timing and CTS",
        "category": "debugging",
        "content": """
Common timing and CTS errors and solutions:

**Error: [ERROR CTS-0007] No clock found**
```
[ERROR CTS-0007] No clock nets found. Check clock definitions in SDC
```
Solution:
- Verify create_clock in SDC file
- Check that clock port name matches netlist: `get_ports clk`
- Ensure SDC is loaded: `read_sdc design.sdc`

**Warning: Large clock skew**
```
[WARNING CTS-0041] Target skew 0.1 not achievable, actual skew: 0.35
```
Solution:
- Adjust buffer list to include more drive strengths
- Reduce clock tree target skew
- Check placement quality (cells too spread out)

**Error: [ERROR RSZ-0004] No liberty files**
```
[ERROR RSZ-0004] No liberty files. Cannot resize.
```
Solution:
- Load liberty file: `read_liberty <lib_file>`
- Verify timing library matches technology used

**Timing not meeting constraints (WNS < 0):**
```
Worst Negative Slack: -0.42
```
Solutions:
- Reduce clock frequency (-period in create_clock)
- Run more aggressive optimization: `repair_timing -setup`
- Check for long combinational paths
- Review placement density and congestion

**Hold violations after CTS:**
```
Worst Hold Slack: -0.15
```
Solutions:
- Run `repair_timing -hold` 
- Ensure hold buffers are available in library
- Check minimum path constraints in SDC
        """,
        "tags": ["error", "timing", "cts", "clock", "wns", "hold", "setup", "debugging"]
    },

    # ===== SCRIPTS =====
    {
        "id": "script_001",
        "title": "Complete RTL-to-GDSII Flow Script",
        "category": "scripts",
        "content": """
Complete OpenROAD RTL-to-GDSII Tcl flow script:

```tcl
# ============================================================
# Complete OpenROAD RTL-to-GDSII Flow Script
# ============================================================

# --- Configuration Variables ---
set DESIGN_NAME  "my_design"
set TECH_LEF     "./pdk/tech.tlef"
set CELL_LEF     "./pdk/cells.lef"
set LIB_FILE     "./pdk/cells.lib"
set VERILOG_FILE "./results/synth/design.v"
set SDC_FILE     "./constraints/design.sdc"

set RESULTS_DIR  "./results"
file mkdir $RESULTS_DIR

# --- 1. Read Libraries and Design ---
puts "=== Reading Libraries ==="
read_lef $TECH_LEF
read_lef $CELL_LEF
read_liberty $LIB_FILE

puts "=== Reading Design ==="
read_verilog $VERILOG_FILE
link_design $DESIGN_NAME
read_sdc $SDC_FILE

# --- 2. Floorplanning ---
puts "=== Floorplanning ==="
initialize_floorplan \
  -utilization 30 \
  -aspect_ratio 1.0 \
  -core_space 2.0 \
  -site FreePDK45_38x28_10R_NP_162NW_34O

place_pins -hor_layers metal2 -ver_layers metal3

pdngen -verbose
write_def $RESULTS_DIR/floorplan.def

# --- 3. Global Placement ---
puts "=== Global Placement ==="
global_placement -timing_driven -density 0.6
estimate_parasitics -placement
repair_design
write_def $RESULTS_DIR/global_placement.def

# --- 4. Detailed Placement ---
puts "=== Detailed Placement ==="
detailed_placement
optimize_mirroring
check_placement -verbose
write_def $RESULTS_DIR/detailed_placement.def

# --- 5. Clock Tree Synthesis ---
puts "=== Clock Tree Synthesis ==="
clock_tree_synthesis \
  -root_buf CLKBUF_X1 \
  -buf_list {CLKBUF_X1 CLKBUF_X2 CLKBUF_X4}
estimated_parasitics -placement
repair_timing
detailed_placement
write_def $RESULTS_DIR/cts.def

# --- 6. Global Routing ---
puts "=== Global Routing ==="
global_route -congestion_iterations 100 -verbose
estimate_parasitics -global_routing
repair_timing
write_def $RESULTS_DIR/global_route.def

# --- 7. Detailed Routing ---
puts "=== Detailed Routing ==="
repair_antenna
detailed_placement
detailed_route -output_drc $RESULTS_DIR/route.drc -verbose 0
write_def $RESULTS_DIR/detailed_route.def

# --- 8. Timing Signoff ---
puts "=== Timing Signoff ==="
estimate_parasitics -global_routing
report_checks -path_delay max -fields {slew cap input nets fanout} -format full_clock_expanded -group_count 5

# --- 9. GDSII Export ---
puts "=== Writing GDSII ==="
write_gds $RESULTS_DIR/final.gds

puts "=== Flow Complete! ==="
```
        """,
        "tags": ["script", "flow", "tcl", "complete", "rtl-to-gdsii", "example"]
    },
    {
        "id": "script_002",
        "title": "Floorplanning Tcl Script",
        "category": "scripts",
        "content": """
Standalone floorplanning Tcl script for OpenROAD:

```tcl
# ============================================================
# Floorplanning Script
# ============================================================

# Load design (assumed already read)
# read_lef, read_liberty, read_verilog, link_design

# Initialize floorplan with utilization
init_floorplan \
  -utilization 45 \
  -aspect_ratio 1.0 \
  -core_space {2.0 2.0 2.0 2.0}

# OR use explicit die area (in microns)
# init_floorplan \
#   -die_area {0 0 500 500} \
#   -core_area {10 10 490 490}

# Place I/O pins
place_pins \
  -hor_layers metal2 \
  -ver_layers metal3 \
  -corner_avoidance 1 \
  -min_distance 0.4

# Generate Power Distribution Network
source ./scripts/pdn.tcl  
# or inline:
pdngen -verbose

# Check current placement
check_placement -verbose

# Report design statistics
report_design_area
report_net_fanout -high_fanout 100

# Save floorplan result
write_def ./results/floorplan/design_floorplan.def
puts "Floorplan complete."
```

**PDN Configuration Script (pdn.tcl):**
```tcl
add_global_connection -net VDD -pin_pattern {^VDD$} -power
add_global_connection -net VSS -pin_pattern {^VSS$} -ground

set_voltage_domain -power VDD -ground VSS

define_pdn_grid -name "Core" -voltage_domains {CORE}
add_pdn_stripe -followpins -layer metal1 -width 0.48
add_pdn_stripe -layer metal4 -width 1.6 -pitch 27.2 -offset 13.6
add_pdn_connect -layers {metal1 metal4}

pdngen
```
        """,
        "tags": ["script", "floorplan", "tcl", "pdn", "example"]
    },
    {
        "id": "script_003",
        "title": "CTS and Timing Optimization Script",
        "category": "scripts",
        "content": """
Clock Tree Synthesis and timing optimization Tcl script:

```tcl
# ============================================================
# CTS and Timing Optimization Script  
# ============================================================

# Assume placement is done. Load from checkpoint:
# read_db ./results/placement.odb

# --- Estimate parasitics before CTS ---
estimate_parasitics -placement

# --- Report pre-CTS timing ---
puts "=== Pre-CTS Timing ==="
report_checks -path_delay max -group_count 3

# --- Run Clock Tree Synthesis ---
clock_tree_synthesis \
  -root_buf sky130_fd_sc_hd__clkbuf_16 \
  -buf_list {sky130_fd_sc_hd__clkbuf_2 
             sky130_fd_sc_hd__clkbuf_4
             sky130_fd_sc_hd__clkbuf_8
             sky130_fd_sc_hd__clkbuf_16} \
  -clk_nets clk \
  -distance_between_buffers 100

# --- Legalize CTS cells ---
detailed_placement

# --- Repair clock network ---
repair_clock_nets

# --- Estimate parasitics after CTS ---
estimate_parasitics -placement

# --- Repair timing violations ---
repair_timing -setup -slack_margin 0.1
repair_timing -hold -allow_setup_violations

# --- Final legalization ---
detailed_placement
check_placement -verbose

# --- Report post-CTS timing ---
puts "=== Post-CTS Timing ==="
report_wns
report_tns
report_checks -path_delay max -slack_max 0.0

# --- Save checkpoint ---
write_db ./results/cts.odb
write_def ./results/cts/design_cts.def
puts "CTS complete."
```
        """,
        "tags": ["script", "cts", "timing", "tcl", "clock", "example"]
    },

    # ===== SKY130 SPECIFIC =====
    {
        "id": "sky130_001",
        "title": "Sky130 PDK Setup for OpenROAD",
        "category": "pdk",
        "content": """
Setting up Sky130 PDK (SkyWater 130nm) for use with OpenROAD:

**File structure:**
```
sky130A/
├── libs.ref/
│   └── sky130_fd_sc_hd/    # High-density standard cells
│       ├── lef/
│       │   ├── sky130_fd_sc_hd.tlef   # Technology LEF
│       │   └── sky130_fd_sc_hd.lef    # Cell LEF
│       └── lib/
│           └── sky130_fd_sc_hd__tt_025C_1v80.lib  # Timing lib
└── libs.tech/
    └── openroad/            # OpenROAD-specific files
        └── sky130A.rc       # RC extraction values
```

**Sky130 standard cell naming:**
- `sky130_fd_sc_hd__<cell>_<drive_strength>`
- Examples:
  - `sky130_fd_sc_hd__buf_1` - buffer, drive 1
  - `sky130_fd_sc_hd__inv_2` - inverter, drive 2
  - `sky130_fd_sc_hd__and2_4` - 2-input AND, drive 4
  - `sky130_fd_sc_hd__dfxtp_1` - D flip-flop, drive 1

**CTS buffers for Sky130:**
```tcl
clock_tree_synthesis \
  -root_buf sky130_fd_sc_hd__clkbuf_16 \
  -buf_list {sky130_fd_sc_hd__clkbuf_2 
             sky130_fd_sc_hd__clkbuf_4
             sky130_fd_sc_hd__clkbuf_8
             sky130_fd_sc_hd__clkbuf_16}
```

**Sky130 routing layers:**
- li1 (local interconnect, poly):
- metal1 through metal5
- Use metal1-metal5 for routing
        """,
        "tags": ["sky130", "pdk", "skywater", "setup", "cells", "library"]
    },

    # ===== DESIGN OPTIMIZATION =====
    {
        "id": "opt_001",
        "title": "Design Optimization Best Practices",
        "category": "optimization",
        "content": """
Best practices and optimization tips for OpenROAD flows:

**Placement Optimization:**
- Start with 30-40% utilization for first trials, increase after verifying routability
- Use -timing_driven for global placement when timing is critical
- Add buffer padding: -pad_left 2 -pad_right 2 for congestion relief
- Place macros first before global placement

**Routing Optimization:**
- Use `set_global_routing_layer_adjustment` to reduce congestion on specific layers
- Run `global_route -congestion_iterations 100` for difficult designs
- Check routing congestion report before detailed routing

**Timing Optimization:**
- Meet timing at each stage (after placement, after CTS, after routing)
- Start with conservative targets and tighten gradually
- Use `repair_design` before detailed placement for setup fixes

**Power Optimization:**
- Ensure robust PDN before placement (check IR drop)
- Use multiple PDN layers for large designs
- Consider power gating for large idle blocks

**Common flow checklist:**
1. ✅ Verify LEF/Liberty files are correct technology version
2. ✅ Check SDC constraints define all clock domains
3. ✅ Verify utilization is achievable (< 70% typical)
4. ✅ Confirm PDN generates without errors
5. ✅ Check placement quality: check_placement -verbose
6. ✅ Verify timing before and after CTS
7. ✅ Check DRC violations after detailed routing
8. ✅ Verify final timing meets constraints
        """,
        "tags": ["optimization", "best_practices", "placement", "routing", "timing", "power"]
    },
    {
        "id": "opt_002",
        "title": "OpenROAD GUI and Interactive Mode",
        "category": "tools",
        "content": """
OpenROAD supports both GUI and interactive Tcl mode for design exploration.

**Starting OpenROAD with GUI:**
```bash
openroad -gui
```

**Starting in interactive Tcl mode:**
```bash
openroad -interactive
```

**Running a script:**
```bash
openroad flow.tcl
```

**Run script with logging:**
```bash
openroad -log ./logs/flow.log flow.tcl
```

**Useful interactive commands:**
```tcl
# List all available commands
help

# Get help on specific command
help global_placement

# Display design in GUI (if GUI started)
gui::show

# Print design statistics
report_design_area

# List all nets
get_nets *

# Find specific cell
get_cells my_register

# Print cell location
puts [[lindex [get_cells my_register] 0] toString]
```

**Tcl scripting tips:**
```tcl
# Set variables for paths
set PDK_DIR /path/to/pdk/sky130A

# Use error handling
if {[catch {global_placement -timing_driven} err]} {
    puts "Error during global placement: $err"
    exit 1
}

# Timing-driven flow with checks
global_placement -timing_driven
estimate_parasitics -placement
set wns [sta::worst_slack -max]
puts "WNS after global placement: $wns"
```
        """,
        "tags": ["gui", "interactive", "tcl", "scripting", "commands", "tools"]
    },
    {
        "id": "opt_003",
        "title": "Physical Verification and DRC Checking",
        "category": "verification",
        "content": """
Physical verification ensures the final design meets manufacturing rules.

**Design Rule Check (DRC):**
```tcl
# Check DRC violations
check_drc

# Write DRC report
check_drc -report_file ./reports/drc.rpt
```

**Layout vs Schematic (LVS):**
LVS compares extracted netlist against schematic/Verilog:
```tcl
# Write extracted netlist for LVS
write_spice -include_global_routes -output ./results/design.spice
```

**Checking specific DRC rules:**
```tcl
# Check minimum spacing
check_spacing_rules

# Check antenna violations
check_antennas -report_violating_nets

# Check placement DRC
check_placement -verbose
```

**Post-routing checks:**
```tcl
# Full DRC after detailed routing
detailed_route -output_drc ./reports/route.drc

# Open DRC report to view violations
# [open ./reports/route.drc r] returns violation count

# Report specific violations
report_drc_violations -layer metal1
```

**Common DRC rules in Sky130:**
- li1 minimum width: 0.17 µm
- metal1 minimum width: 0.17 µm  
- metal1 minimum spacing: 0.28 µm
- metal2 minimum width: 0.23 µm
- Via1 to metal1 enclosure: 0.055 µm per side
        """,
        "tags": ["drc", "lvs", "verification", "check_drc", "physical_verification"]
    },
]


def get_all_docs():
    """Return all documentation chunks."""
    return OPENROAD_DOCS


def get_docs_by_category(category: str):
    """Return docs filtered by category."""
    return [d for d in OPENROAD_DOCS if d["category"] == category]


def get_categories():
    """Return all unique categories."""
    return list(set(d["category"] for d in OPENROAD_DOCS))


def get_doc_by_id(doc_id: str):
    """Return a specific doc by ID."""
    for doc in OPENROAD_DOCS:
        if doc["id"] == doc_id:
            return doc
    return None
