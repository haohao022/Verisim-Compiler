- identifier: 
	- **ident**
- system_name:
	- **sysname**
- real_number:
	- **realnum**
- natural_number:
    - **natural**
- string:
    - **string**
- unary_operator:
  - **+|-|!|\~|&|\~&|  \|  | \~| | ^ | ~^ | ^~**
- binary_operator:
  - **+|-|*|/|%| =\= | != | === | !\== | && | || | ** |< | <= | > |  >= | & | | | ^ | ^~ | ~^ | >> | << | >>> | <<<** 

---  

- translation_unit :               //dormouse:顶级模块，一切的开始
  - module_declaration
- module_declaration :   //去掉了parameter_port_list
  - **module** module_identifier [ **(** [list_of_ports | list_of_port_declarations] **)** ] **;** { module_item  } **endmodule**

- list_of_ports:  
	- port{ **,** [port]}
- list_of_port_declarations: 
	- port_declaration { **,** port_declaration }
- port:
	- port_expression | **.**port_identifier **(** [ port_expression ] **)**
- port_expression:
	- port_reference | **{** port_reference  { , port_reference } **}**  
- port_reference :
	- port_identifier[ **[** constant_range_expression **]**  ]   //�������ident���ļ�λ����
- port_declaration: 
	- input_declaration | output_declaration | inout_declaration  
//by dormouse : 考虑删掉inout
- module_item :
	- port_declaration **;**
	- non_port_module_item
- module_or_generate_item :
	- module_or_generate_item_declaration  
	  | continuous_assign    //assign语句
	  | gate_instantiation      //门电路语句  
	  | initial_construct  
 	  | always_construct   
	  | loop_generate_construct  
	  | conditional_generate_construct  
- module_or_generate_item_declaration : 
	- net_declaration | reg_declaration | integer_declaration | real_declaration 
	 | genvar_declaration 
  
- non_port_module_item :
	- module_or_generate_item
	| generate_region

- input_declaration :
  - **input** [ **wire** ] [ **signed** ] [ range ] list_of_port_identifiers

- inout_declaration : 
  - **inout** [ **wire** ] [ **signed** ] [ range ] list_of_port_identifiers

- output_declaration :
  - **output** ( [ **wire** ] [ **signed** ] [ range ] list_of_port_identifiers | **reg** [ **signed** ] [ range ] list_of_variable_port_identifiers | **interger** list_of_variable_port_identifiers )  
- integer_declaration :
  - **integer** list_of_variable_identifiers **;**

- list_of_net_decl_assignments_or_identifiers :
	- net_identifier [ dimension { dimension } | **=** expression ] { **,** net_identifier [ dimension { dimension } | **=** expression ] }

- net_declaration :
	- **wire** [ **signed** ] [ range ] list_of_net_decl_assignments_or_identifiers ;  //delay strength vector 去掉亄1�7
- real_declaration :
  - **real** list_of_real_identifiers ;

- reg_declaration :
  - **reg** [ **signed** ] [ range ] list_of_variable_identifiers ;

- real_type :
	- real_identifier ( { dimension } | **=** constant_expression )

- variable_type :
	- variable_identifier ( { dimension } | **=** constant_expression )

- list_of_port_identifiers :
	- port_identifier { **,** port_identifier }

- list_of_real_identifiers :
	- real_type { **,** real_type }

- list_of_variable_identifiers :
  - port_identifier [ **=** constant_expression ] { **,** port_identifier [ **=** constant_expression ] }

- dimension :
	- **[** dimension_constant_expression **:** dimension_constant_expression **]**

- range :
	- **[** msb_constant_expression **:** lsb_constant_expression **]**

- block_item_declaration :  //也许用不到，暂时删掉。语法见markdown原文  
	<!-- - block_reg_declaration
	| block_integer_declaration
	| local_parameter_declaration **;**
  - list_of_block_variable_identifiers :
	- block_variable_type { **,** block_variable_type }   -->

- gate_instantiation :
	-   n_input_gatetype  n_input_gate_instance { **,** n_input_gate_instance } **;**
		| n_output_gatetype  n_output_gate_instance { **,** n_output_gate_instance } **;**
- n_input_gate_instance :
	- [ name_of_gate_instance ] **(** output_terminal **,** input_terminal { **,** input_terminal } **)**

- n_output_gate_instance :
	- [ name_of_gate_instance ] **(** input_or_output_terminal { **,** input_or_output_terminal } **)**
- output_terminal :
  - net_lvalue
- input_terminal :
  - expression
- input_or_output_terminal :   //expression_2 不太懂结构，也没有在本文给出
  - expression_2   
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
	- **generate** { module_or_generate_item } **endgenerate**  //dormouse也许会去掉
  
- genvar_declaration :
  - **genvar** list_of_genvar_identifiers **;**  //dormouse也许会去掉

- list_of_genvar_identifiers :
	- genvar_identifier { **,** genvar_identifier }
  
- loop_generate_construct :
	- **for** **(** genvar_initialization **;** genvar_expression **;** genvar_iteration **)** ( generate_block | module_or_generate_item )

- genvar_initialization :
    - genvar_identifier **=** constant_expression

- genvar_expression :
	- [ unary_operator ] genvar_primary genvar_expression_nlr
- genvar_expression_nlr :
	[ binary_operator genvar_expression genvar_expression_nlr
	| **?** genvar_expression **:** genvar_expression genvar_expression_nlr ]

- genvar_iteration :
	- genvar_identifier **=** genvar_expression


- genvar_primary :
	- constant_primary

- conditional_generate_construct :
	- if_generate_construct
	| case_generate_construct

- if_generate_construct :
     **if (** constant_expression **)** generate_block_or_null [ **else** generate_block_or_null ]


- case_generate_construct :
	- **case** **(** constant_expression **)** case_generate_item { case_generate_item } **endcase**


- case_generate_item :
	- constant_expression { **,** constant_expression } **:** generate_block_or_null
| **default** [ **:** ] generate_block_or_null

- generate_block :
**begin** [ **:** generate_block_identifier ] { module_or_generate_item } **end**

- generate_block_or_null :
generate_block
| module_or_generate_item
| **;**

- continuous_assign :
	- **assign**  list_of_net_assignments **;**

- list_of_net_assignments :
	- net_assignment { **,** net_assignment }
- net_assignment :
	- net_lvalue **=** expression
- initial_construct :
	- **initial** statement
- always_construct :
	- **always** statement

- procedural_continuous_assignments :
	- **assign** variable_assignment
- variable_assignment :
	- variable_lvalue **=** expression

- seq_block :
	- **begin** [ **:** block_identifier { block_item_declaration } ] { statement } **end**
- blocking_or_nonblocking_assignment_or_task_enable :
	variable_lvalue [ **(** expression { **,** expression } **)** ] [ ( **<=** | **=** ) [ delay_or_event_control ] [ expression ] ] **;**
- statement :
	- blocking_or_nonblocking_assignment_or_task_enable
	| case_statement
	| conditional_statement
	| loop_statement
	| procedural_continuous_assignments ;
	| seq_block
	| ;

- statement_or_null :
	- [ statement ]
- delay_or_event_control :
 	- event_control

- event_control :
	- **@** ( **(** ( event_expression | **\*** ) **)** | **\*** | hierarchical_event_identifier )

- hierarchical_event_identifier : //可能用不到，这里不给出内容，详见markdown原文
	<!-- -hierarchical_identifier
      - hierarchical_identifier :
    	- identifier [ [ constant_expression ] ] { . identifier [ [ constant_expression ] ] } -->


- event_expression :
  - **posedge** expression event_expression_nlr |
    expression event_expression_nlr
- event_expression_nlr :
	- [ **or** event_expression event_expression_nlr
| **,** event_expression event_expression_nlr ]

- conditional_statement :
**if** **(** expression **)** statement_or_null [ **else** statement_or_null ]

-  case_statement :
**case** **(** expression **)** case_item { case_item } **endcase**

- case_item :
expression { **,** expression } **:** statement_or_null
| **default** [ **:** ] statement_or_null

- loop_statement :
	- **for** **(** variable_assignment **;** expression **;** variable_assignment **)** statement

- constant_expression :
	- [ unary_operator ] constant_primary { constant_expression_nlr }

- constant_expression_nlr:
  - binary_operator constant_expression
| **?** constant_expression **:** constant_expression

- expression :
	- [ unary_operator ] primary { expression_nlr }


- expression_nlr :
  - binary_operator expression
| **?** expression **:** expression

- lsb_constant_expression :
	- constant_expression

- constant_primary :
	-	number
		| string
		<!-- | **(** constant_mintypmax_expression **)** -->
		| ( identifier | system_name ) [ **[** constant_range_expression **]** | **(** constant_expression { **,** constant_expression } **)** ]
		| **{** constant_expression [ **,** constant_expression { **,** constant_expression } | **{** constant_expression { **,** constant_expression } **}** ] **}**


- primary :
	- ( hierarchical_identifier_range  ) [ **(** expression { **,** expression } **)** ]
	| number
	| string
	<!-- | **(** mintypmax_expression **)** -->
	| **{** expression [ **,** expression { **,** expression } | **{** expression { **,** expression } **}** ] **}**

- hierarchical_identifier_range :
	- identifier { **.** identifier [ **[** range_expression **]** ] | **[** range_expression **]** }

- range_expression :
	- expression [ **:** lsb_constant_expression ]
- net_lvalue :
	- hierarchical_identifier_range_const
		| **{** net_lvalue { **,** net_lvalue } **}**	


- hierarchical_identifier_range_const :
	- identifier { **.** identifier [ **[** constant_range_expression **]** ] | **[** constant_range_expression **]** }
  
- variable_lvalue :
	- hierarchical_identifier_range
		| **{** variable_lvalue { **,** variable_lvalue } **}**

- variable_or_net_lvalue :
	- hierarchical_identifier_range
		| **{**variable_or_net_lvalue { **,** variable_or_net_lvalue } }



- number :
	- real_number
	| natural_number [ based_number | base_format ( base_value | natural_number ) ]
	| sizedbased_number
	| based_number
	| base_format ( base_value | natural_number )

- based_number :
	- **BASEDINT**
- base_value :
	- **BASEVAL**
- sizedbased_number:
  - **SIZEVAL**
- base_format :
	- **BASEFMT**


- constant_range_expression :
	- constant_expression [ **:** lsb_constant_expression  ]
- list_of_variable_port_identifiers :
	- port_identifier [ **=** constant_expression ] { **,** port_identifier [ **=** constant_expression ] }

- module_identifier:
  - identifier

- port_identifier : 
  - identifier
- net_identifier : 
  - identifier

- gate_instance_identifier :
	- identifier
- genvar_identifier :
  - identifier
- block_identifier :
  - identifier
- dimension_constant_expression :
	- constant_expression

- msb_constant_expression :
	- constant_expression
- generate_block_identifier :
	- identifier
//DORMOUSE
	考虑去掉genvar   
	考虑去掉seq_block中的block_identifier 表述  
	 考虑去掉constant  
//DORMOU SE  

//removed     
	module_parameter_port_list  
	parameter override  
	loal_parameter_declaration  
	realtime_declaration  
	module_or_udp_instantiation  // module语句或用户定义的udp实例  
	specify_block  
	parameter_declaration  
	net_type  //因为只有wire  
	output_variable_type //only integer  
	constant_mintypmax_expression  
	system_function_identifier  