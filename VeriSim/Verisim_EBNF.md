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
	- net_declaration | reg_declaration | integer+declaration | real_declaration | time_declaration | realtime_declaration
	| event_decalaration | genvar_declaration | task_declaration | function_declaration
  
removed     
	module\_parameter\_port\_list
	parameter override
	loal_parameter_declaration