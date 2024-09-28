// *********************************************** //
   //  Author : Srimanth Tenneti 
   //  Date : 24th September 2024 
   //  Version : 0.001
// *********************************************** //

module DirectMappedCache (
  input        clk, 
  input        resetn, 
  input        read_enable, 
  input        write_enable, 
  input    [21:0] address, 
  input    [31:0] write_data, 
  output   [31:0] read_data, 
  output       hit
);

reg r_hit; 
reg [31:0] r_read_data; 

// Parameters 
parameter BLOCK_SIZE = 8; 
parameter LINE_COUNT = 256; 
parameter WORD_SIZE  = 32; 

// Derived Parameters 
localparam OFFSET_BITS = 5; 
localparam INDEX_BITS  = 8; 
localparam TAG_BITS    = 9; 

// Address Breakdown 
wire [TAG_BITS - 1 : 0]    tag    = address[21 : 21 - TAG_BITS + 1]; 
wire [INDEX_BITS - 1 : 0]  index  = address[21-TAG_BITS:21-TAG_BITS-INDEX_BITS+1];
wire [OFFSET_BITS - 1 : 0] offset = address[OFFSET_BITS-1:0]; 

// Cache Line Definition 
reg [TAG_BITS - 1 : 0] tag_array [0 : LINE_COUNT-1]; 
reg                    val_array [0 : LINE_COUNT-1]; 
reg [WORD_SIZE*BLOCK_SIZE-1 : 0] data_array [0 : LINE_COUNT-1];  

integer i; 


always @ (posedge clk or negedge resetn) begin
  if (~resetn) begin
    for (i=0; i < LINE_COUNT; i=i+1) begin
        val_array[i] <= 0; 
        tag_array[i] <= 0; 
        data_array[i] <= 0; 
     end
    r_hit <= 0; 
    r_read_data <= 0; 
  end else begin
     if (val_array[index] && (tag_array[index] == tag)) begin
        r_hit <= 1; 
        if (read_enable) begin
             r_read_data <= data_array[index][(offset/4)*WORD_SIZE +: WORD_SIZE]; 
        end
        if (write_enable) begin
            data_array[index][(offset/4)*WORD_SIZE +: WORD_SIZE] <= write_data; 
        end
     end else begin
       r_hit <= 0; 
       if (read_enable || write_enable) begin
         tag_array[index]   <= tag; 
         val_array[index] <= 1; 
         data_array[index]  <= {BLOCK_SIZE*WORD_SIZE{1'b0}}; 
         if (write_enable) begin
            data_array[index][(offset/4)*WORD_SIZE +: WORD_SIZE]  <= write_data; 
         end
         if (read_enable) begin
          r_read_data <= data_array[index][(offset/4)*WORD_SIZE +: WORD_SIZE]; 
        end
      end
    end
  end 
end

assign read_data = r_read_data; 
assign hit       = r_hit;


initial begin
  $dumpfile("Cache.vcd"); 
  $dumpvars(0, DirectMappedCache); 
end

endmodule
