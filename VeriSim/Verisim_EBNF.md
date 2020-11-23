- identifier: 
	- ident
- system_name:
	- sysname
- real_number:
	- realnum
- natural_number:
    - natural
- string:
    - string
- unary_oerator:
  - +|-|!|\~|&|\~&|  \|  | \~| | ^ | ~^ | ^~
- binary_operator:
  - +|-|*|\|%| =\= | != | === | !\== | && | || | ** |< | <= | > |  >= | & | | | ^ | ^~ | ~^ | >> | << | >>> | <<< 

---  

- translation_unit : 
  - module_declaration
- module_declaration
  - module\_declaration module\_identifier [ **(** [list\_of\_ports|list\_of\_port\_declarations] **)** ]; **{** module\_item  **}** **endmodule**
- module\_keyword:
  - **module**
- list\_of\_ports:  
	- port{ **,** [port]}
- list\_of\_port\_declarations: 
	- port\_declaration { **,** port\_declaration }
- port:
	- port\_expression | **.**port\_identifier**(** [ port_expression ] **)**
- port_expression:
	- port\_reference | **{** port\_reference  { , port\_reference } **}**  
- port\_reference :
	- port\_identifier[ **[** constant_range_expression **]**  ] 
- port\_declaration: 
	- input\_declaration | output\_declaration | inout\_declaration  
//by dormouse : 暂不支持inout ？ 
- module_item:
	- port\_delaration **;**
	- non\_port\_module\_item
- module\_or\_generate\_item :
	- module\_or\_generate\_item\_declaration
	  | local_parameter_declaration  
	  | continuous_assign   //assign语句  
	  | gate_instantiation     //门电路实例化？  
	  | module_or_udp_instantiation  // module实例化，udp不支持！
	  | initial_construct  
 	  | always_construct   
	  | loop_generate_construct  
	  | conditional_generate_construct  
- module_or_generate_item_declaration : 
	- net_declaration | reg_declaration | integer_declaration | real_declaration 
	 | genvar_declaration | task_declaration 
  
- non_port_module_item :
	- module_or_generate_item
	| generate_region
	| specify_block
	| parameter_declaration **;**
	| specparam_declaration

- input_declaration :
  - **input** [ net_type ] [ **signed** ] [ range ] list_of_port_identifiers

- inout_declaration : 
  - **inout** [ net_type ] [ **signed** ] [ range ] list_of_port_identifiers

- output_declaration :
  - **output** ( [ net_type ] [ **signed** ] [ range ] list_of_port_identifiers | **reg** [ **signed** ] [ range ] list_of_variable_port_identifiers | output_variable_type list_of_variable_port_identifiers )  //output_variable_type 可能无法实现
- integer_declaration :
  - **integer** list_of_variable_identifiers ;

- list_of_net_decl_assignments_or_identifiers :
	- net_identifier [ dimension { dimension } | **=** expression ] { **,** net_identifier [ dimension { dimension } | = expression ] }

- net_declaration :
	- net_type [ **signed** ] [ range ] list_of_net_decl_assignments_or_identifiers ;  //delay strength vector 都无法实现  
- real_declaration ：
  - **real** list_of_real_identifiers ;

- reg_declaration :
  - reg [ signed ] [ range ] list_of_variable_identifiers ;

- net_type: 
  - wire

- output_variable_type :
  - integer

- real_type :
	- real_identifier ( { dimension } | = constant_expression )

- variable_type :
	- variable_identifier ( { dimension } | = constant_expression )

- list_of_port_identifiers :
	- port_identifier { , port_identifier }

- list_of_real_identifiers :
	- real_type { , real_type }

- list_of_variable_identifiers :
  - port_identifier [ = constant_expression ] { , port_identifier [ = constant_expression ] }

- dimension :
	- **[** dimension_constant_expression **:** dimension_constant_expression **]**

- range :
	- **[** msb_constant_expression **:** lsb_constant_expression **]**

- block_item_declaration :
	- block_reg_declaration
	| block_integer_declaration
	| local_parameter_declaration **;**
	| parameter_declaration **;**
- list_of_block_variable_identifiers :
	- block_variable_type { **,** block_variable_type }  

- gate_instantiation :
	-   n_input_gatetype  n_input_gate_instance { **,** n_input_gate_instance } **;**
		| n_output_gatetype  n_output_gate_instance { **,** n_output_gate_instance } **;**
- n_input_gate_instance :
	- [ name_of_gate_instance ] **(** output_terminal **,** input_terminal { **,** input_terminal } **)**

- n_output_gate_instance :
	- [ name_of_gate_instance ] **(** input_or_output_terminal { **,** input_or_output_terminal }**)**

- name_of_gate_instance :
	- gate_instance_identifier **[** range **]**

- n_input_gatetype :
    - **and
    | nand
    | or
    | nor
    | xor
    | xnor**

- n_output_gatetype :
  - **not**

- generate_region :
	- **generate** { module_or_generate_item } **endgenerate**  //dormouse待定
  
- genvar_declaration :
  - **genvar** list_of_genvar_identifiers **;** //dormouse待定

- list_of_genvar_identifiers :
	- genvar_identifier { **,** genvar_identifier }
  
- loop_generate_construct :
	- **for** **(** genvar_initialization **;** genvar_expression **;** genvar_iteration **)** ( generate_block | module_or_generate_item )

//DORMOUSE


//DORMOU SE

removed     
	module\_parameter\_port\_list
	parameter override
	loal_parameter_declaration
	realtime_declaration
	