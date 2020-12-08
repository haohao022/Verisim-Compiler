import sys
from spark_parser import GenericParser, GenericASTTraversal
from spark_parser import AST
from collections import namedtuple


class Interpret(GenericASTTraversal):

    def __init__(self, ast):
        GenericASTTraversal.__init__(self, ast)
        self.postorder(ast)
        self.attr = int(ast.attr)

    # Rules for interpreting nodes based on their AST node type
    def n_integer(self, node):
        node.attr = int(node.attr)

    def n_single(self, node):
        node.attr = node.data[0].attr

    def n_multiply(self, node):
        node.attr = int(node[0].attr) * int(node[1].attr)

    def n_divide(self, node):
        node.attr = int(node[0].attr) / int(node[1].attr)

    def n_add(self, node):
        node.attr = int(node[0].attr) + int(node[1].attr)

    def n_subtract(self, node):
        node.attr = int(node[0].attr) - int(node[1].attr)

    def default(self, node):
        pass


def build_bp_expr(string, show_tokens=False, show_ast=False, show_grammar=False):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': True, 'context': True, 'dups': True }
    parsed = parse_bp_location(string, show_tokens=show_tokens,
                               parser_debug=parser_debug)
    assert parsed == 'bp_start'
    if show_ast:
        print(parsed)
    walker = LocationGrok(string)
    walker.traverse(parsed)
    bp_expr = walker.result
    if isinstance(bp_expr, Location):
        bp_expr = BPLocation(bp_expr, None)
    location = bp_expr.location
    assert location.line_number is not None or location.method
    return bp_expr

def build_range(string, show_tokens=True, show_ast=False, show_grammar=True):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': True, 'context': True, 'dups': True }
    parsed = parse_range(string, show_tokens=show_tokens,
                               parser_debug=parser_debug)
    if show_ast:
        print(parsed)
    assert parsed == 'range_start'
    walker = LocationGrok(string)
    walker.traverse(parsed)
    list_range = walker.result
    return list_range


# FIXME: DRY with build_range
def build_arange(string, show_tokens=False, show_ast=False, show_grammar=False):
    parser_debug = {'rules': False, 'transition': False,
                    'reduce': show_grammar,
                    'errorstack': None,
                    'context': True, 'dups': True
                        }
    parsed = parse_arange(string, show_tokens=show_tokens,
                          parser_debug=parser_debug)
    if show_ast:
        print(parsed)
    assert parsed == 'arange_start'
    walker = LocationGrok(string)
    walker.traverse(parsed)
    list_range = walker.result
    return list_range


if __name__ == '__main__':
    # if len(sys.argv) == 1:
    #     for python2_stmts in (
    #             """return f()""",
    #             ):
    #         print(python2_stmts)
    #         print('-' * 30)
    #         ast = parse_VeriSim(python2_stmts + ENDMARKER,
    #                             start='translation_unit', show_tokens=False, check=True)
    #         print(ast)
    #         print(IS_EQUAL * 30)
    # else:
    #     python2_stmts = " ".join(sys.argv[1:])
    #     parse_VeriSim(python2_stmts, show_tokens=False, check=True)
    src = open('adder.v')
    scan = VeriSimScanner()
    tokens = scan.tokenize(src.read() + ENDMARKER)
    ast = parse_VeriSim(tokens, start='translation_unit', show_tokens=False, check=True)
    
    print("DORMOUSE+==========+end")
    tmp = Interpret(ast)

    print("dormouse-semantics-end!")
    pass