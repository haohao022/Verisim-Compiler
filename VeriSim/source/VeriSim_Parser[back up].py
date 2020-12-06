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
                 'errorstack': 'full', 'context': True, 'dups': True}

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
    # Python 2 grammar rules. Grammar rule functions
    # start with the name p_ and are collected automatically
    ##########################################################
    def p_python_grammar(self, args):
        '''
        translation_unit ::= module_declaration 

        ## list_of_ports and declarations
        modult_declaration ::= MODULE module_identifier ['(' [dor_list_of_ports_or_decla] ')'] ';' module_item* ENDMODULE
        dor_list_of_ports_or_decla ::= list_of_ports
        dor_list_of_ports_or_decla ::= list_of_port_declarations

        list_of_ports ::= port (',' [port])*
        list_of_port_declarations ::= port_declaration (',' port_declaration)*

        port ::= port_expression
        port ::= '.' port_identifier '(' [port_expression] ')'

        port_expression ::= port_reference
        port_expression ::= '{' port_reference  (',' port_reference)* '}' 

        port_reference ::= port_identifier ['['constant_range_expression']']
        port_declaration ::= input_declaration
        port_declaration ::= output_declaration

        module_item ::= port_declaration ‘;’
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

        input_declaration ::= INPUT [WIRE] [SIGNED] [range] list_of_port_identifiers
        output_declaration ::= OUTPUT [WIRE] [SIGNED] [range] list_of_port_identifiers
        output_declaration ::= OUTPUT REG [SIGNED] [range] list_of_variable_port_identifiers
        output_declaration ::= OUTPUT INTEGER list_of_variable_port_identifiers

        integer_declaration ::= INTEGER list_of_variable_identifiers ';'

        ## dor dimension and expression // line 67 
        list_of_net_decl_assignments_or_identifiers ::= net_identifier [ dor_dim_and_exp ] (',' net_identifier dor_dim_and_exp )*
        dor_dim_and_exp ::= dimension+
        dor_dim_and_exp ::= '=' expression

        net_declaration ::= WIRE [SIGNED] [range] list_of_net_decl_assignments_or_identifiers
        real_declaration ::= REAL list_of_real_identifiers
        reg_declaration ::= REG [SIGNED] [range] list_of_variable_identifiers

        real_type ::= real_identifier dimension*
        real_type ::= real_identifier '=' constant_expression

        variable_type ::= variable_identifier dimension*
        variable_type ::= variable_identifier '=' constant_expression

        list_of_port_identifiers ::= port_identifier (',' port_identifier)*
        list_of_real_identifiers ::= real_type (',' real_type)*

        list_of_variable_identifiers ::= port_identifier ['=' constant_expression] (',' port_identifier ['=' constant_expression])*
        dimension ::= '[' dimension_constant_expression ':' dimension_constant_expression ']'
        range ::= '[' msb_constant_expression ':' lsb_constant_expression ']'
        ### gatetype
        gate_instantiation ::= n_input_gatetype n_input_gate_instance (',' n_input_gate_instance)* ';'
        gate_instantiation ::= n_output_gatetype n_output_gate_instance (',' n_output_gate_instance)* ';'

        n_input_gate_instance ::= [name_of_gate_instance] '(' output_terminal ',' input_terminal (',' input_terminal)* ')'
        n_output_gate_instance ::= [name_of_gate_instance] '(' input_or_output_terminal (',' input_or_output_terminal)* ')'

        input_terminal ::= expression

        ## dor :dont dnow expression_2
        input_or_output_terminal ::= expression_2

        name_of_gate_instance ::= gate_instance_identifier '[' range ']'

        ### gatetype
        n_input_gatetype ::= AND
        n_input_gatetype ::= NAND
        n_input_gatetype ::= OR
        n_input_gatetype ::= NOR
        n_input_gatetype ::= XOR
        n_input_gatetype ::= XNOR
        n_output_gatetype ::= NOT

        generate_region ::= GENERATE module_or_generate_item* ENDGENERATE
        genvar_declaration ::= GENVAR list_of_genvar_identifiers ';'

        list_of_genvar_identifiers ::= genvar_identifier (',' genvar_identifier)* 
        loop_generate_construct ::= FOR '(' genvar_initialization ';' genvar_expression ';' genvar_iteration ')' generate_block
        loop_generate_construct ::= FOR '(' genvar_initialization ';' genvar_expression ';' genvar_iteration ')' module_or_generate_item
        genvar_initialization ::= genvar_identifier '=' constant_expression



        genvar_expression ::= [unary_operator] genvar_primary genvar_expression_nlr
        genvar_expression_nlr ::= [binary_operator genvar_expression genvar_expression_nlr]
        genvar_expression_nlr ::= ['?' genvar_expression ':' genvar_expression genvar_expression_nlr]

        genvar_iteration ::= genvar_identifier '=' genvar_expression
        genvar_primary ::= constant_primary
        conditional_generate_construct ::= if_generate_construct
        conditional_generate_construct ::= case_generate_construct

        if_generate_construct ::= IF '(' constant_expression ')'  generate_block_or_null [ELSE generate_block_or_null]
        case_generate_construct ::= CASE '(' constant_expression ')'  case_generate_item case_generate_item* ENDCASE

        case_generate_item ::= constant_expression (',' constant_expression)* ':' generate_block_or_null
        case_generate_item ::= DEFAULT ':' generate_block_or_null

        generate_block ::= BEGIN [':' generate_block_identifier] module_or_generate_item* END

        generate_block_or_null ::= generate_block
        generate_block_or_null ::= module_or_generate_item
        generate_block_or_null ::= ';'
        continuous_assign ::= ASSIGN list_of_net_assignments ';'
        list_of_net_assignments ::= net_assignment (',' net_assignment)* 
        net_assignment ::= net_lvalue '=' expression
        initial_construct ::= INITIAL statement
        always_construct ::= ALWAYS statement


        procedural_continuous_assignments ::= ASSIGN variable_assignment
        variable_assignment ::= variable_lvalue '=' expression
        seq_block ::= BEGIN [':' block_identifier block_item_declaration* ] statement* END

        blocking_or_nonblocking_assignment_or_task_enable ::= variable_lvalue ['(' expression (',' expression)*   ')'] ['<=' [delay_or_event_control] [expression] ] ';'



        statement ::= blocking_or_nonblocking_assignment_or_task_enable
        statement ::= case_statement
        statement ::= conditional_statement
        statement ::= loop_statement
        statement ::= procedural_continuous_assignments ';'
        statement ::= seq_block
        statement ::= ';'

        statement_or_null ::= [statement]
        delay_or_event_control ::=  event_control

        event_control ::= '@' '(' event_expression ')'
        event_control ::= '@' '(' '*' ')'
        event_control ::= '@' '*'

        event_expression ::= 'POSEDGE' expression event_expression_nlr
        event_expression ::= expression event_expression_nlr

        event_expression_nlr ::= 'OR'  event_expression  event_expression_nlr
        event_expression_nlr ::=  ',' event_expression  event_expression_nlr
        event_expression_nlr ::= 
        conditional_statement  ::= 'IF' '(' expression ')' statement_or_null ['ELSE' statement_or_null]
        case_statement  ::= 'CASE' '(' expression ')' case_item+  'ENDCASE'    

        ##case item
        case_item ::= expression (',' expression )+ ':' statement_or_null
        case_item ::= 'default' [':'] statement_or_null

        loop_statement ::= 'FOR' '(' variable_assignment ';' expression ';' variable_assignment ')' statement
        constant_expression ::= [ unary_operator ] constant_primary (constant_expression_nlr)*
        constant_expression_nlr ::= binary_operator constant_expression
        expression ::= [ unary_operator ] primary { expression_nlr }
        expression_nlr::= binary_operator expression
        expression_nlr::=  '?' expression ':' expression
        lsb_constant_expression ::=constant_expression

        constant_primary ::= number
        constant_primary ::= string

        ##dor ident_or_sysname 
        constant_primary ::= dor_ident_or_sysname [ '[' constant_range_expression ']' ]
        constant_primary ::= dor_ident_or_sysname [ '(' constant_expression { ',' constant_expression } ')' ]
        dor_ident_or_sysname ::=  identifier
        dor_ident_or_sysname ::=  system_name

        constant_primary ::= '{' constant_expression [ ',' constant_expression (',' constant_expression )* ] '}'
        constant_primary ::= '{' constant_expression [ '{' constant_expression (',' constant_expression )* '}' ] '}'


        primary ::= hierarchical_identifier_range   [ '(' expression (',' expression)* ')' ]
        primary ::= number
        primary ::= string
        primary ::= '{' expression [ ',' expression (',' expression)* ] '}'

        primary ::= '{' expression [ '{' expression (',' expression)* '}' ] '}'

        hierarchical_identifier_range ::= identifier ('.' identifier [ '[' range_expression ']' ])*
        hierarchical_identifier_range ::= identifier  ('[' range_expression ']')*

        range_expression ::= expression [ ':' lsb_constant_expression ]
        net_lvalue ::= hierarchical_identifier_range_const

        net_lvalue ::= '{' net_lvalue (',' net_lvalue)* '}'	
        hierarchical_identifier_range_const ::= identifier ('.' identifier [ '[' constant_range_expression ']' ] )*
        hierarchical_identifier_range_const ::= identifier ( '[' constant_range_expression ']')*

        variable_lvalue ::= hierarchical_identifier_range
        variable_lvalue ::= '{' variable_lvalue (',' variable_lvalue)* '}'
        variable_or_net_lvalue ::= hierarchical_identifier_range
        variable_or_net_lvalue ::= '{' variable_or_net_lvalue (',' variable_or_net_lvalue)* '}'

        number ::= real_number
        number ::= natural_number [based_number]
        number ::= natural_number [base_format base_value ]

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

        constant_range_expression ::= constant_expression [ ':' lsb_constant_expression  ]
        list_of_variable_port_identifiers ::= port_identifier [ '=' constant_expression ]  (',' port_identifier [ '=' constant_expression ])*
        module_identifier ::= identifier 
        port_identifier ::= identifier
        net_identifier ::= identifier 
        gate_instance_identifier ::= identifier 
        genvar_identifier ::= identifier 
        block_identifier ::= identifier 
        dimension_constant_expression ::= constant_expression 
        msb_constant_expression ::= constant_expression 

        generate_block_identifier ::= identifier

        identifier ::= NAME
    '''

    # Import-related grammar
    def p_import(self, args):
        """
        ## import_stmt ::= import_name | import_from
        import_stmt ::= import_name
        import_stmt ::= import_from

        ## import_name ::= IMPORT dotted_as_names
        import_name ::= IMPORT dotted_as_names

        ##  import_from ::= ('from' ('.'* dotted_name | '.'+)
        ##                  'import' ('*' | '(' import_as_names ')' | import_as_names))
        import_from ::= FROM dots_dotted_name_or_dots import_list

        import_as_name ::= NAME
        import_as_name ::= NAME AS NAME

        dotted_as_name ::= dotted_name
        dotted_as_name ::= dotted_name AS NAME

        dots_dotted_name_or_dots ::= dots dotted_name
        dots_dotted_name_or_dots ::= DOT dots
        dots ::= DOT*

        ## 'import' ('*' | '(' import_as_names ')' | import_as_names))
        import_list ::= IMPORT STAR
        import_list ::= IMPORT LPAREN import_as_names RPAREN
        import_list ::= IMPORT import_as_names

        ## import_as_names ::= import_as_name ((',' import_as_name)+\) [',']
        # Note: we don't do the opt comma at the end
        import_as_names ::= import_as_name comma_import_as_names

        ##  (',' import_as_name)+
        comma_import_as_names ::= comma_import_as_names comma_import_as_name
        comma_import_as_names ::=

        ##  ',' import_as_name
        comma_import_as_name ::= COMMA import_as_name

        comma_dotted_as_names ::= dotted_as_name+

        dotted_as_names ::= dotted_as_name comma_dotted_as_names
        comma_dotted_as_names ::= comma_dotted_as_names COMMA dotted_as_name
        comma_dotted_as_names ::=

        dotted_name ::= NAME dot_names
        dot_names ::= dot_names DOT NAME
        dot_names ::=
        """

    def p_compund_stmt(self, args):
        """
        compound_stmt ::= if_stmt
        compound_stmt ::= while_stmt
        compound_stmt ::= for_stmt
        compound_stmt ::= try_stmt
        compound_stmt ::= with_stmt
        compound_stmt ::= funcdef
        compound_stmt ::= classdef
        compound_stmt ::= decorated

        if_stmt ::= IF test COLON suite elif_suites else_suite_opt
        if_stmt ::= IF test COLON NEWLINE suite elif_suites else_suite_opt

        elif_suites ::= elif_suites ELIF test COLON suite
        elif_suites ::=
        else_suite_opt ::= ELSE COLON suite
        else_suite_opt ::=

        ## while_stmt ::= 'while' test ':' suite ['else' ':' suite]
        while_stmt ::= WHILE test COLON suite else_suite_opt

        ## for_stmt ::= 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
        for_stmt ::= FOR exprlist IN testlist COLON suite else_colon_suite_opt

        ## ['else' ':' suite]
        else_colon_suite_opt ::= ELSE COLON suite
        else_colon_suite_opt ::=

        ## try_stmt ::= ('try' ':' suite
        ##      ((except_clause ':' suite)+
        ##       ['else' ':' suite]
        ##       ['finally' ':' suite] |
        ##      'finally' ':' suite))

        ## with_stmt ::= with' test [ with_var ] ':' suite
        with_stmt ::= WITH test with_var_opt COLON suite

        with_var_opt ::= with_var?

        ## with_var ::= 'as' expr
        with_var ::= AS expr

        suite ::= stmt_plus

        suite ::=  NEWLINE indent stmt_plus NEWLINE DEDENT
        suite ::=  NEWLINE indent stmt_plus DEDENT
        indent ::= INDENT comments
        indent ::= INDENT
        """


def parse_VeriSim(VeriSim_stmts, start='modult_declaration',
                  show_tokens=True, parser_debug=DEFAULT_DEBUG, check=False):
    assert isinstance(VeriSim_stmts, str)
    tokens = VeriSimScanner().tokenize(VeriSim_stmts)
    if show_tokens:
        for t in tokens:
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
    return parser.parse(tokens)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        for python2_stmts in (
#                 # "if True: pass",
#                 """
# while True:
#     if False:
#         continue

# """,
                # "if True: pass",
                """return f()""",
                ):
            print(python2_stmts)
            print('-' * 30)
            ast = parse_VeriSim(python2_stmts + ENDMARKER,
                                start='modult_declaration', show_tokens=False, check=True)
            print(ast)
            print('=' * 30)
    else:
        python2_stmts = " ".join(sys.argv[1:])
        parse_VeriSim(python2_stmts, show_tokens=False, check=True)
