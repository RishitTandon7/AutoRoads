// ============================================================
//  GCD (Greatest Common Divisor) — Synthesizable Verilog RTL
//  Compatible with sky130_fd_sc_hd (sky130 HD standard-cell lib)
//  Used as a real design for the OpenROAD flow demo
// ============================================================
module gcd (
    input  wire        clk,
    input  wire        reset,
    input  wire        req_val,
    output wire        req_rdy,
    input  wire [15:0] req_msg_a,
    input  wire [15:0] req_msg_b,
    output wire        resp_val,
    input  wire        resp_rdy,
    output wire [15:0] resp_msg
);

  // State encoding
  localparam IDLE = 2'd0, CALC = 2'd1, DONE = 2'd2;

  reg [1:0]  state, next_state;
  reg [15:0] a_reg, b_reg;

  // Next-state logic
  always @(*) begin
    case (state)
      IDLE: next_state = req_val ? CALC : IDLE;
      CALC: next_state = (b_reg == 0) ? DONE : CALC;
      DONE: next_state = resp_rdy ? IDLE : DONE;
      default: next_state = IDLE;
    endcase
  end

  // State register
  always @(posedge clk or posedge reset) begin
    if (reset) state <= IDLE;
    else        state <= next_state;
  end

  // Datapath — Euclidean algorithm
  always @(posedge clk) begin
    if (state == IDLE && req_val) begin
      a_reg <= req_msg_a;
      b_reg <= req_msg_b;
    end else if (state == CALC) begin
      if (a_reg >= b_reg)
        a_reg <= a_reg - b_reg;
      else
        b_reg <= b_reg - a_reg;
    end
  end

  assign req_rdy  = (state == IDLE);
  assign resp_val = (state == DONE);
  assign resp_msg = a_reg;

endmodule
