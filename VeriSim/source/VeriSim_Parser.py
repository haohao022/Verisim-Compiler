#  Copyright (c) 2016-2017 Rocky Bernstein
"""
More complex expression parsing
"""

# from __future__ import print_function

import sys
from spark_parser.ast import AST

from VeriSim_Scanner import VeriSimScanner, ENDMARKER

from spark_parser import GenericASTBuilder

DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce' : False,
                 'errorstack': 'full', 'context': False, 'dups': False}

class VeriSimParser(GenericASTBuilder):
    """A more complete spark example: a Python 2 Parser.

    Note: function parse() comes from GenericASTBuilder
    """

    def __init__(self, start='modult_declaration', debug=DEFAULT_DEBUG):
        super(VeriSimParser, self).__init__(AST, start, debug=debug)
        self.start = start
        self.debug = debug

        # Put left-recursive list non-terminals:
        # x ::= x y
        # x ::=
        self.collect = frozenset(('stmts', 'comments', 'dot_names', 'dots',
                        'comp_op_exprs', 'newline_or_stmts',
                        'comma_names', 'comma_fpdef_opt_eqtests',)
        )


    def debug_reduce(self, rule, tokens, parent, i):
        """Customized format and print for our kind of tokens
        which gets called in debugging grammar reduce rules
        """
        prefix = '           '
        if parent and tokens:
            p_token = tokens[parent]
            if hasattr(p_token, 'line'):
                prefix = 'L.%3d.%03d: ' % (p_token.line, p_token.column)
                pass
            pass
        print("%s%s ::= %s" % (prefix, rule[0], ' '.join(rule[1])))

    def nonterminal(self, nt, args):
        # nonterminal with a (reserved) single word derivation
        no_skip = ('pass_stmt', 'continue_stmt', 'break_stmt', 'return_stmt')

        has_len = hasattr(args, '__len__')

        if nt in self.collect and len(args) > 1:
            #
            #  Collect iterated thingies together.
            #
            rv = args[0]
            for arg in args[1:]:
                rv.append(arg)
        elif (has_len and len(args) == 1 and
              hasattr(args[0], '__len__') and args[0] not in no_skip and
              len(args[0]) == 1):
            # Remove singleton derivations
            rv = GenericASTBuilder.nonterminal(self, nt, args[0])
            del args[0] # save memory
        elif (has_len and len(args) == 2 and
              hasattr(args[1], '__len__') and len(args[1]) == 0):
            # Remove trailing epsilon rules, but only when there
            # are two items.
            if hasattr(args[0], '__len__') and len(args[0]) == 1:
                # Remove singleton derivation
                rv = args[0]
            else:
                rv = GenericASTBuilder.nonterminal(self, nt, args[:1])
            del args[1] # save memory
        else:
            rv = GenericASTBuilder.nonterminal(self, nt, args)
        return rv

    ##########################################################
    # Verisim grammar rules. Grammar rule functions
    # start with the name p_ and are collected automatically
    ##########################################################
    def p_main_module(self,args):
        '''
        translation_unit ::= module_declaration
        modult_declaration ::= MODULE module_identifier dor_list_of_ports_or_decla_opt_1 SEMICOLON module_item* ENDMODULE

        ## dor_list_of_ports_or_decla_opt_1

        dor_list_of_ports_or_decla_opt_1 ::= LPAREN dor_list_of_ports_or_decla_opt_2 RPAREN
        dor_list_of_ports_or_decla_opt_1 ::=
        dor_list_of_ports_or_decla_opt_2 ::= dor_list_of_ports_or_decla
        dor_list_of_ports_or_decla_opt_2 ::=
        dor_list_of_ports_or_decla ::= list_of_ports
        dor_list_of_ports_or_decla ::= list_of_port_declarations
        



        ## 这里的port真的需要左右有中括号吗？ list_of_ports ::= port (COMMA [port])*
        ## new comma_ports_opt
        list_of_ports ::= port comma_ports_opt
        comma_ports_opt ::= comma_port_opt COMMA port_opt 

        port ::= port_expression
        port ::= DOT port_identifier LPAREN port_expression_opt RPAREN

        port_opt ::= port
        port_opt ::=
        range_opt ::= range
        #### range_opt ::= 

        range ::= LBRACKET msb_constant_expression COLON lsb_constant_expression RBRACKET

        ## list_of_port_declarations ::= port_declaration (COMMA port_declaration)*
        ## comma_port_declarations 
        list_of_port_declarations ::= port_declaration comma_port_declarations
        comma_port_declarations ::= comma_port_declarations COMMA port_declaration
        comma_port_declarations ::= 
        '''
        # node_i = ( 'MODULE' ,args[1]) 
        
        # return AST('MODULE',[args[1]])


    def p_python_grammar(self, args):
        ''' 
        
        port_expression_opt ::= port_expression?

        port_expression ::= port_reference
        port_expression ::= LBRACE port_reference  comma_port_references RBRACE 

        ## (COMMA port_reference)*
        comma_port_references ::= comma_port_references COMMA port_reference
        comma_port_references ::=

        ##  port_reference ::= port_identifier ['['constant_range_expression']']

        port_reference ::= port_identifier LBRACKET_constant_range_expression_RBRACKET_opt 

        LBRACKET_constant_range_expression_RBRACKET_opt ::= LBRACKET constant_range_expression RBRACKET
        LBRACKET_constant_range_expression_RBRACKET_opt ::=

        port_declaration ::= input_declaration
        port_declaration ::= output_declaration

        module_item ::= port_declaration SEMICOLON
        module_item ::= non_port_module_item

        module_or_generate_item ::= module_or_generate_item_declaration
        module_or_generate_item ::= continuous_assign
        module_or_generate_item ::= gate_instantiation
        module_or_generate_item ::= initial_construct
        module_or_generate_item ::= always_construct
        module_or_generate_item ::= loop_generate_construct
        module_or_generate_item ::= conditional_generate_construct

        module_or_generate_item_declaration ::= net_declaration
        module_or_generate_item_declaration ::= reg_declaration
        module_or_generate_item_declaration ::= integer_declaration
        module_or_generate_item_declaration ::= real_declaration
        module_or_generate_item_declaration ::= genvar_declaration

        non_port_module_item ::= module_or_generate_item
        non_port_module_item ::= generate_region

        input_declaration ::= INPUT wire_opt signed_opt range_opt list_of_port_identifiers
        wire_opt ::= WIRE?
        signed_opt ::= SIGNED?
        

        output_declaration ::= OUTPUT wire_opt signed_opt range_opt list_of_port_identifiers
        output_declaration ::= OUTPUT REG signed_opt range_opt list_of_variable_port_identifiers
        output_declaration ::= OUTPUT INTEGER list_of_variable_port_identifiers

        integer_declaration ::= INTEGER list_of_variable_identifiers SEMICOLON

        ## dor dimension and expression // line 67 
        ## list_of_net_decl_assignments_or_identifiers ::= net_identifier [ dor_dim_and_exp ] (COMMA net_identifier dor_dim_and_exp )*
        list_of_net_decl_assignments_or_identifiers ::= net_identifier dor_dim_and_exp_opt  COMMA_net_identifier_dor_dim_and_exps
        dor_dim_and_exp_opt ::= dor_dim_and_exp?
        COMMA_net_identifier_dor_dim_and_exps     ::= COMMA_net_identifier_dor_dim_and_exps COMMA net_identifier dor_dim_and_exp
        COMMA_net_identifier_dor_dim_and_exps ::= 

        dor_dim_and_exp ::= dimension+
        dor_dim_and_exp ::= IS_EQUAL expression

        net_declaration ::= WIRE SIGNED? range_opt list_of_net_decl_assignments_or_identifiers

        real_declaration ::= REAL list_of_real_identifiers
        reg_declaration ::= REG SIGNED? range_opt list_of_variable_identifiers

        real_type ::= real_identifier dimension*

        real_type ::= real_identifier IS_EQUAL constant_expression

        variable_type ::= variable_identifier dimension*
        variable_type ::= variable_identifier IS_EQUAL constant_expression

        list_of_port_identifiers ::= port_identifier COMMA_port_identifiers
        COMMA_port_identifiers ::= COMMA_port_identifiers COMMA port_identifier
        COMMA_port_identifiers ::=

        list_of_real_identifiers ::= real_type COMMA_real_types
        COMMA_real_types ::= COMMA_real_types COMMA real_type
        ###(COMMA port_identifier [IS_EQUAL constant_expression])*
        list_of_variable_identifiers ::= port_identifier IS_EQUAL_constant_expression_opt COMMA_port_identifier_IS_EQUAL_constant_expression_opt_s
        IS_EQUAL_constant_expression_opt ::= IS_EQUAL constant_expression
        COMMA_port_identifier_IS_EQUAL_constant_expression_opt_s ::= COMMA_port_identifier_IS_EQUAL_constant_expression_opt_s COMMA port_identifier  IS_EQUAL_constant_expression_opt
        COMMA_port_identifier_IS_EQUAL_constant_expression_opt_s ::= 
        IS_EQUAL_constant_expression_opt ::= IS_EQUAL constant_expression
        IS_EQUAL_constant_expression_opt ::=


        dimension ::= LBRACKET dimension_constant_expression COLON dimension_constant_expression RBRACKET
    
        

        ### gatetype
        gate_instantiation ::= n_input_gatetype n_input_gate_instance COMMA_n_input_gate_instances SEMICOLON
        COMMA_n_input_gate_instances ::= COMMA_n_input_gate_instances COMMA n_input_gate_instance
        COMMA_n_input_gate_instances ::= 

        gate_instantiation ::= n_output_gatetype n_output_gate_instance COMMA_n_output_gate_instances SEMICOLON
        COMMA_n_output_gate_instances ::= COMMA_n_output_gate_instances COMMA n_output_gate_instances
        COMMA_n_output_gate_instances ::= 

        n_input_gate_instance ::= name_of_gate_instance_opt LPAREN output_terminal COMMA input_terminal COMMA_input_terminals RPAREN
        name_of_gate_instance_opt ::= name_of_gate_instance?
        COMMA_input_terminals ::= COMMA_input_terminals COMMA input_terminal
        COMMA_input_terminals ::= 

        n_output_gate_instance ::= name_of_gate_instance_opt LPAREN input_or_output_terminal COMMA_input_or_output_terminals RPAREN
        COMMA_input_or_output_terminals ::= COMMA_input_or_output_terminals COMMA input_or_output_terminal
        COMMA_input_or_output_terminals ::= 

        input_terminal ::= expression

        ## dor :dont dnow expression_2
        ### input_or_output_terminal ::= expression_2
        input_or_output_terminal ::= expression


        name_of_gate_instance ::= gate_instance_identifier LBRACKET range RBRACKET

        ## gatetype
        n_input_gatetype ::= AND
        n_input_gatetype ::= NAND
        n_input_gatetype ::= OR
        n_input_gatetype ::= NOR
        n_input_gatetype ::= XOR
        n_input_gatetype ::= XNOR
        n_output_gatetype ::= NOT

        generate_region ::= GENERATE module_or_generate_item* ENDGENERATE
        genvar_declaration ::= GENVAR list_of_genvar_identifiers SEMICOLON

        # list_of_genvar_identifiers ::= genvar_identifier (COMMA genvar_identifier)* 
        loop_generate_construct ::= FOR LPAREN genvar_initialization SEMICOLON genvar_expression SEMICOLON genvar_iteration RPAREN generate_block
        loop_generate_construct ::= FOR LPAREN genvar_initialization SEMICOLON genvar_expression SEMICOLON genvar_iteration RPAREN module_or_generate_item
        genvar_initialization ::= genvar_identifier IS_EQUAL constant_expression



        genvar_expression ::= unary_operator? genvar_primary genvar_expression_nlr

        genvar_expression_nlr ::= binary_operator genvar_expression genvar_expression_nlr
        genvar_expression_nlr ::= QUES genvar_expression COLON genvar_expression genvar_expression_nlr
        genvar_expression_nlr ::= 

        genvar_iteration ::= genvar_identifier IS_EQUAL genvar_expression
        genvar_primary ::= constant_primary
        conditional_generate_construct ::= if_generate_construct
        conditional_generate_construct ::= case_generate_construct

        if_generate_construct ::= IF LPAREN constant_expression RPAREN  generate_block_or_null ELSE_generate_block_or_null_opt
        ELSE_generate_block_or_null_opt ::= ELSE generate_block_or_null
        ELSE_generate_block_or_null_opt ::= 
        case_generate_construct ::= CASE LPAREN constant_expression RPAREN  case_generate_item case_generate_item* ENDCASE

        case_generate_item ::= constant_expression COMMA_constant_expressions COLON generate_block_or_null
        COMMA_constant_expressions ::= COMMA_constant_expressions COMMAconstant_expression
        COMMA_constant_expressions ::= 
        case_generate_item ::= DEFAULT COLON generate_block_or_null

        COLON_generate_block_identifier_opt ::= COLON generate_block_identifier
        generate_block ::= BEGIN COLON_generate_block_identifier_opt module_or_generate_item* END
        

        generate_block_or_null ::= generate_block
        generate_block_or_null ::= module_or_generate_item
        generate_block_or_null ::= SEMICOLON
        continuous_assign ::= ASSIGN list_of_net_assignments SEMICOLON


        list_of_net_assignments ::= net_assignment COMMA_net_assignments
        COMMA_net_assignments ::= COMMA_net_assignments COMMA net_assignment
        COMMA_net_assignments ::= 

        net_assignment ::= net_lvalue IS_EQUAL expression
        initial_construct ::= INITIAL statement
        always_construct ::= ALWAYS statement


        procedural_continuous_assignments ::= ASSIGN variable_assignment
        variable_assignment ::= variable_lvalue IS_EQUAL expression
        ## [COLON block_identifier block_item_declaration* ]
        seq_block ::= BEGIN COLON_block_identifier_block_item_declarations_opt statement* END
        COLON_block_identifier_block_item_declarations_opt ::= COLON block_identifier block_item_declaration*
        COLON block_identifier block_item_declarations_opt ::= 

        ##!!! great ->    [LPAREN expression (COMMA expression)*   RPAREN] ['<=' [delay_or_event_control] [expression] ] 
        blocking_or_nonblocking_assignment_or_task_enable ::= variable_lvalue great1_opt great2_opt SEMICOLON
        great1 ::= LPAREN expression COMMA_expressions   RPAREN
        COMMA_expressions ::= COMMA_expressions COMMA expression
        COMMA_expressions ::= 
        great1 ::= 


        ##dor COMP_OP MUSTbe '<='
        great2 ::= COMP_OP delay_or_event_control? expression?
        great2 ::= 


        statement ::= blocking_or_nonblocking_assignment_or_task_enable
        statement ::= case_statement
        statement ::= conditional_statement
        statement ::= loop_statement
        statement ::= procedural_continuous_assignments SEMICOLON
        statement ::= seq_block
        statement ::= SEMICOLON

        statement_or_null ::= statement?
        delay_or_event_control ::=  event_control

        event_control ::= AT LPAREN event_expression RPAREN

        ##dor!!! STAR must be caution
        event_control ::= AT LPAREN BINOP RPAREN
        event_control ::= AT BINOP



        event_expression ::= POSEDGE expression event_expression_nlr
        event_expression ::= expression event_expression_nlr

        event_expression_nlr ::= OR event_expression  event_expression_nlr
        event_expression_nlr ::=  COMMA event_expression  event_expression_nlr
        event_expression_nlr ::= 
        conditional_statement  ::= IF LPAREN expression RPAREN statement_or_null ELSE_statement_or_null_opt
        ELSE_statement_or_null_opt ::= ELSE statement_or_null
        ELSE_statement_or_null_opt ::= 
        case_statement  ::= CASE LPAREN expression RPAREN case_item+ ENDCASE    

        ## case item
        case_item ::= expression COMMA_expressions  COLON statement_or_null
        COMMA_expressions ::= COMMA_expressions COMMA_expression
        COMMA_expression ::= COMMA expression

        case_item ::= DEFAULT COLON? statement_or_null

        loop_statement ::= FOR LPAREN variable_assignment SEMICOLON expression SEMICOLON variable_assignment RPAREN statement


        ## constant_expression ::= [ unary_operator ] constant_primary constant_expression_nlr*
        constant_expression ::= unary_operator_opt constant_primary constant_expression_nlr*

        unary_operator_opt::= unary_operator?

        constant_expression_nlr ::= binary_operator constant_expression

        expression ::= unary_operator_opt primary  expression_nlr*
        expression_nlr::= binary_operator expression
        expression_nlr::=  QUES expression COLON expression
        lsb_constant_expression ::= constant_expression

        constant_primary ::= number
        ### constant_primary ::= string

        ##dor ident_or_sysname 
        ## constant_primary ::= dor_ident_or_sysname [ LBRACKET constant_range_expression RBRACKET ]
        constant_primary ::= dor_ident_or_sysname  LBRACKET_constant_range_expression_RBRACKET_opt 
        LBRACKET_constant_range_expression_RBRACKET_opt ::= LBRACKET constant_range_expression RBRACKET
        LBRACKET_constant_range_expression_RBRACKET_opt ::= 

        ## constant_primary ::= dor_ident_or_sysname [ LPAREN constant_expression { COMMA constant_expression } RPAREN ]
        constant_primary ::= dor_ident_or_sysname LPAREN_constant_expression_COMMA_constant_expressions_RPAREN_opt
        LPAREN_constant_expression_COMMA_constant_expressions_RPAREN_opt ::= LPAREN constant_expression COMMA_constant_expressions RPAREN
        LPAREN_constant_expression_COMMA_constant_expressions_RPAREN_opt ::=

        dor_ident_or_sysname ::=  identifier
        dor_ident_or_sysname ::=  system_name

        ## constant_primary ::= LBRACE constant_expression [ COMMA constant_expression (COMMA constant_expression )* ] RBRACE
        constant_primary ::= LBRACE constant_expression COMMA_constant_expression_COMMA_constant_expressions_opt RBRACE
        COMMA_constant_expression_COMMA_constant_expressions_opt ::= COMMA constant_expression COMMA_constant_expressions
        ## constant_primary ::= LBRACE constant_expression [ LBRACE constant_expression (COMMA constant_expression )* RBRACE ] RBRACE
        constant_primary ::= LBRACE constant_expression LBRACE_constant_expression_COMMA_constant_expressions_RBRACE_opt RBRACE
        LBRACE_constant_expression_COMMA_constant_expressions_RBRACE_opt ::= LBRACE constant_expression COMMA_constant_expressions

        COMMA_constant_expressions ::=  COMMA_constant_expressions COMMA constant_expression
        COMMA_constant_expressions ::= 

        ##  primary ::= hierarchical_identifier_range   [ LPAREN expression (COMMA expression)* RPAREN ]
        primary ::= hierarchical_identifier_range   LPAREN_expression_COMMA_expressions_RPAREN_opt 
        LPAREN_expression_COMMA_expressions_RPAREN_opt ::= LPAREN expression COMMA_expressions RPAREN
        LPAREN_expression_COMMA_expressions_RPAREN_opt ::= 

        primary ::= number
        ### primary ::= string
        ## primary ::= LBRACE expression [ COMMA expression (COMMA expression)* ] RBRACE
        primary ::= LBRACE expression COMMA_expression_COMMA_expressions_opt RBRACE
        COMMA_expression_COMMA_expressions_opt ::= COMMA expression COMMA_expressions
        COMMA_expression_COMMA_expressions_opt ::= 

        ## primary ::= LBRACE expression [ LBRACE expression (COMMA expression)* RBRACE ] RBRACE
        primary ::= LBRACE expression LBRACE_expression_COMMA_expressions_RBRACE_opt RBRACE
        LBRACE_expression_COMMA_expressions_RBRACE_opt ::= LBRACE expression COMMA_expressions RBRACE
        LBRACE_expression_COMMA_expressions_RBRACE_opt ::= 

        ## hierarchical_identifier_range ::= identifier ( DOT identifier [ LBRACKET range_expression RBRACKET ])*
        hierarchical_identifier_range ::= identifier DOT_identifier_LBRACKET_range_expression_RBRACKET_opt_s

        DOT_identifier_LBRACKET_range_expression_RBRACKET_opt_s ::= DOT_identifier_LBRACKET_range_expression_RBRACKET_opt_s DOT identifier LBRACKET_range_expression_RBRACKET_opt
        DOT_identifier_LBRACKET_range_expression_RBRACKET_opt_s ::= 
        hierarchical_identifier_range ::= identifier LBRACKET_range_expression_RBRACKETs
        LBRACKET_range_expression_RBRACKETs::= LBRACKET_range_expression_RBRACKETs LBRACKET range_expression RBRACKET
        LBRACKET_range_expression_RBRACKET_opt ::= LBRACKET range_expression RBRACKET

        range_expression ::= expression COLON_lsb_constant_expression_opt
        COLON_lsb_constant_expression_opt ::= COLON lsb_constant_expression

        net_lvalue ::= hierarchical_identifier_range_const

        net_lvalue ::= LBRACE net_lvalue COMMA_net_lvalues RBRACE	
        COMMA_net_lvalues ::= COMMA_net_lvalues COMMA net_lvalue

        ## hierarchical_identifier_range_const ::= identifier (DOT identifier [ LBRACKET constant_range_expression RBRACKET ] )*
        hierarchical_identifier_range_const ::= identifier DOT_identifier_LBRACKET_constant_range_expression_RBRACKET_opt_s
        DOT_identifier_LBRACKET_constant_range_expression_RBRACKET_opt_s ::= DOT_identifier_LBRACKET_constant_range_expression_RBRACKET_opt_s DOT identifier LBRACKET_constant_range_expression_RBRACKET_opt
        DOT_identifier_LBRACKET_constant_range_expression_RBRACKET_opt_s ::= 
        LBRACKET_constant_range_expression_RBRACKET_opt ::= LBRACKET constant_range_expression RBRACKET

        hierarchical_identifier_range_const ::= identifier LBRACKET_constant_range_expression_RBRACKETs
        LBRACKET_constant_range_expression_RBRACKETs ::= LBRACKET_constant_range_expression_RBRACKETs LBRACKET constant_range_expression RBRACKET
        LBRACKET_constant_range_expression_RBRACKETs ::= 

        variable_lvalue ::= hierarchical_identifier_range
        variable_lvalue ::= LBRACE variable_lvalue COMMA_variable_lvalues RBRACE
        COMMA_variable_lvalues ::= COMMA_variable_lvalues COMMA variable_lvalue
        COMMA_variable_lvalues ::= 

        variable_or_net_lvalue ::= hierarchical_identifier_range
        ## variable_or_net_lvalue ::= LBRACE variable_or_net_lvalue (COMMA variable_or_net_lvalue)* RBRACE
        variable_or_net_lvalue ::= LBRACE variable_or_net_lvalue COMMA_variable_or_net_lvalues RBRACE
        COMMA_variable_or_net_lvalues ::= COMMA_variable_or_net_lvalues COMMA variable_or_net_lvalue
        COMMA_variable_or_net_lvalues ::=

        number ::= real_number
        real_number ::= NUMBER

        number ::= natural_number based_number?
        number ::= natural_number base_format_base_value_opt
        base_format_base_value_opt ::= base_format base_value

        ##dor: now cant resolve base_value and base_number 
        ## number ::= natural_number [base_format natural_number ]
        
        number ::= sizedbased_number
        number ::= based_number

        ## number ::= base_format base_value
        number ::= base_format natural_number

        based_number ::= NUMBER
        base_value ::= NUMBER
        ## value is 1 0 x z
        sizedbased_number ::= SIZE_NUMBER
        base_format ::= SIZE_NUMBER

        constant_range_expression ::= constant_expression COLON_lsb_constant_expression_opt

        ## list_of_variable_port_identifiers ::= port_identifier [ IS_EQUAL constant_expression ]  (COMMA port_identifier [ IS_EQUAL constant_expression ])*
        list_of_variable_port_identifiers ::= port_identifier IS_EQUAL_constant_expression_opt COMMA_port_identifier_IS_EQUAL_constant_expression_opts
        IS_EQUAL_constant_expression_opt ::= IS_EQUAL constant_expression
        IS_EQUAL_constant_expression_opt ::= 
        COMMA_port_identifier_IS_EQUAL_constant_expression_opts ::= COMMA port_identifier IS_EQUAL_constant_expression_opt
        COMMA_port_identifier_IS_EQUAL_constant_expression_opts ::=


        module_identifier ::= identifier 
        port_identifier ::= identifier
        net_identifier ::= identifier 
        gate_instance_identifier ::= identifier 
        genvar_identifier ::= identifier 
        block_identifier ::= identifier 
        dimension_constant_expression ::= constant_expression 
        msb_constant_expression ::= constant_expression 

        generate_block_identifier ::= identifier
        unary_operator ::= PLUS
        unary_operator ::= MINUS
        unary_operator ::= QUES
        identifier ::= NAME
    '''



def parse_VeriSim(VeriSim_tokens, start='modult_declaration',
                  show_tokens=False, parser_debug=DEFAULT_DEBUG, check=False):
    assert isinstance(VeriSim_tokens, list)
    if show_tokens:
        for t in VeriSim_tokens:
            print(t)

    # For heavy grammar debugging:
    # parser_debug = {'rules': True, 'transition': True, 'reduce': True,
    #               'errorstack': 'full', 'context': True, 'dups': True}
    # Normal debugging:
    # parser_debug = {'rules': False, 'transition': False, 'reduce': True,
    #                'errorstack': 'full', 'context': True, 'dups': True}
    parser = VeriSimParser(start=start, debug=parser_debug)
    if check:
        parser.check_grammar()
    return parser.parse(VeriSim_tokens)


if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     for python2_stmts in (
    #             """return f()""",
    #             ):
    #         print(python2_stmts)
    #         print('-' * 30)
    #         ast = parse_VeriSim(python2_stmts + ENDMARKER,
    #                             start='modult_declaration', show_tokens=False, check=True)
    #         print(ast)
    #         print(IS_EQUAL * 30)
    # else:
    #     python2_stmts = " ".join(sys.argv[1:])
    #     parse_VeriSim(python2_stmts, show_tokens=False, check=True)
    src = open('adder.v')
    scan = VeriSimScanner()
    tokens = scan.tokenize(src.read() + ENDMARKER)
    ast = parse_VeriSim(tokens, start='modult_declaration', show_tokens=False, check=True)

    print("DORMOUSE+==========+end")
