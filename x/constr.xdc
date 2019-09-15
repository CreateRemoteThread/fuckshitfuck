set_property IOSTANDARD LVCMOS33 [get_ports sc_clk]
set_property IOSTANDARD LVCMOS33 [get_ports sc_io]
set_property IOSTANDARD LVCMOS33 [get_ports trigger]
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets sc_io_IBUF]

set_property IOSTANDARD LVCMOS33 [get_ports led_out]
set_property PACKAGE_PIN H5 [get_ports led_out]
set_property PACKAGE_PIN G13 [get_ports sc_clk]
set_property PACKAGE_PIN B11 [get_ports sc_io]
set_property PACKAGE_PIN A11 [get_ports trigger]

