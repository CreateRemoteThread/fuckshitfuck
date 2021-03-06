`timescale 1ns / 1ps

module glitch_trigger(
    input sc_clk,
    input sc_io,
    input sc_reset,
    input prog_clk,
    input prog_reset,
    input prog_io,
    output trigger,
    output led_out,
    output led_out_2,
    output led_out_3
    );

assign led_out_3 = prog_reset;

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

reg [32:0] CLK_EDGE_TARGET = 13255;
reg [32:0] IO_EDGE_TARGET = 720;

initial
begin
    CLK_EDGE_TARGET <= 13255;
    IO_EDGE_TARGET <= 720;
end

reg [1:0] prog_state_io;
reg [1:0] prog_state_clk;
reg [8:0] prog_shift;
reg [1:0] prog_wait_state = 0;

always @(posedge prog_clk)
begin
    if(prog_reset == 0)         // pulse with no prog_reset = select next parameter to program
    begin         
        prog_shift <= 0;
        prog_wait_state <= 1;
    end
    else
    begin
        if(prog_wait_state == 1)
        begin
            if(prog_io == 1)
            begin
                IO_EDGE_TARGET <= 0;
                prog_state_io <= 1;
                prog_state_clk <= 0;
            end
            else
            begin
                CLK_EDGE_TARGET <= 0;
                prog_state_io <= 0;
                prog_state_clk <= 1;
            end
            prog_wait_state <= 0;
        end
        else
        begin
            if(prog_state_io == 1)  // start shifting bits in
            begin
                IO_EDGE_TARGET <= IO_EDGE_TARGET + (prog_io << prog_shift);
            end
            else if(prog_state_clk == 1)
            begin
                CLK_EDGE_TARGET <= CLK_EDGE_TARGET + (prog_io << prog_shift);
            end
            prog_shift <= prog_shift + 1;
        end
    end
end

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

