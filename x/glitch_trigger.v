`timescale 1ns / 1ps

module glitch_trigger(
    input sc_clk,
    input sc_io,
    input sc_reset,
    output trigger,
    output led_out,
    output led_out_2
    );

// wire wait_io_edge;
reg [1:0] wait_io_edge;
reg [1:0] wait_clk_edge;
reg [1:0] internal_io_edge;
reg [1:0] internal_reset;
reg [32:0] ctr_io;
reg [32:0] ctr_clk;

assign led_out = wait_clk_edge;
assign led_out_2 = wait_io_edge;
assign trigger = wait_clk_edge;

parameter CLK_EDGE_TARGET = 13255;
parameter IO_EDGE_TARGET = 720;

// MASTER CLOCK HERE.
always @(posedge sc_clk)
begin
    if (sc_reset == 0)
    begin
        wait_io_edge <= 0;
        wait_clk_edge <= 0;
        ctr_io <= 0;
        ctr_clk <= 0;
        internal_reset <= 0;
        internal_io_edge <= 0;
    end
    else
    begin
        if(sc_io == 1 && internal_io_edge == 0)
        begin
            ctr_io <= ctr_io + 1;
            if(ctr_io > IO_EDGE_TARGET)
            begin
                wait_io_edge <= 1;
            end
        end
        internal_io_edge <= sc_io;
        if(wait_io_edge == 1 && wait_clk_edge == 0)
        begin
            ctr_clk <= ctr_clk + 1;
        end
        if(ctr_clk > CLK_EDGE_TARGET)
        begin
            wait_clk_edge <= 1;
        end
    end
end
endmodule
