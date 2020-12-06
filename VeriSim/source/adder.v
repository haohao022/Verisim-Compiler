// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module adder(

    ) ;

	reg [4:0] sum_s;

    always @(posedge Clk) begin
		if (En) begin
			sum_s=A+B;
		end		
	end
endmodule
