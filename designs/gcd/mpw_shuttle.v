module mpw_shuttle(
  input clk,
  input ce,
  input we,
  input [5:0] addr,
  input [31:0] din
);

  fakeram45_64x32 sram_0 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_1 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_2 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_3 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_4 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_5 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_6 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_7 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_8 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_9 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_10 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_11 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_12 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_13 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_14 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_15 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_16 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_17 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_18 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_19 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_20 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_21 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_22 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_23 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_24 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_25 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_26 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_27 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_28 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_29 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_30 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_31 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_32 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_33 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_34 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_35 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_36 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_37 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_38 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_39 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_40 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
  fakeram45_64x32 sram_41 (
    .clk(clk),
    .ce_in(ce),
    .we_in(we),
    .addr_in(addr),
    .wd_in(din),
    .w_mask_in(32'hFFFFFFFF),
    .rd_out()
  );
endmodule
