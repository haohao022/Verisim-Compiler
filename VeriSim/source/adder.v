// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module adder(
    input [3:0] A,
    input [3:0] B,
    input Clk,
    input En,
    output [3:0] Sum,
    output Overflow
    );
	 reg [4:0] sum_s;
	 
	
	assign {Overflow,Sum}=sum_s;
	
	initial begin
		sum_s=0;
	end
	
	always @(posedge Clk) begin
		if (En) begin
			sum_s=A+B;
		end		
	end
	
endmodule