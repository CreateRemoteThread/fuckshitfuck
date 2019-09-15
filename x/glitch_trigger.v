`timescale 1ns / 1ps

module glitch_trigger(
    input sc_clk,
    input sc_io,
    output trigger,
    output led_out
    );

reg [1:0] state;
reg [16:0] ctr;

wire led_out;

assign led_out = state;
assign trigger = state;

parameter CTR_TARGET = 864;

initial begin
    state = 0;
    ctr = 0;
end

always @(posedge sc_io)
begin
    if(sc_clk)
    begin
        ctr <= ctr + 1;
        if(ctr > CTR_TARGET)
        begin
            state <= 1;
        end

    end
    else
    begin
        state <= 0;
        ctr <= 0;
    end
end 
endmodule
