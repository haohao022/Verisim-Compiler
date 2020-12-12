import sys
from spark_parser import GenericParser, GenericASTTraversal
from spark_parser import AST ,GenericASTTraversalPruningException


from VeriSim_Parser import VeriSimParser

from VeriSim_Scanner import VeriSimScanner, ENDMARKER

from VeriSim_dor_ST  import Sign ,SignTable

from collections import namedtuple

DEFAULT_DEBUG = {'rules': False, 'transition': False, 'reduce' : True,
                 'errorstack': 'full', 'context': False, 'dups': False}


class Interpret(GenericASTTraversal):
    
    tmp_wire_counter =0 
    def gen_tmp(self):
        Interpret.tmp_wire_counter +=1
        return '_W_tmp'+str(Interpret.tmp_wire_counter)

    # Override
    def preorder(self, node=None):
        """Walk the tree in roughly 'preorder' (a bit of a lie explained below).
        For each node with typestring name *name* if the
        node has a method called n_*name*, call that before walking
        children. If there is no method define, call a
        self.default(node) instead. Subclasses of GenericASTTtraversal
        ill probably want to override this method.

        If the node has a method called *name*_exit, that is called
        after all children have been called.

        In typical use a node with children can call "preorder" in any
        order it wants which may skip children or order then in ways
        other than first to last.  In fact, this this happens.  So in
        this sense this function not strictly preorder.
        """
        # if node is None:
        #     node = self.ast
        if node is None:
            return 

        try:
            name = 'n_' + self.typestring(node)
            if hasattr(self, name):
                func = getattr(self, name)
                func(node)
            else:
                self.default(node)
        except GenericASTTraversalPruningException:
            return

        # if(len(node)>0) :
        #     for kid in node[1:]:
        #         self.preorder(kid)
        
        for kid in node:
            self.preorder(kid)

        name = name + '_exit'
        if hasattr(self, name):
            func = getattr(self, name)
            func(node)
        pass
        
    def __init__(self, ast):
        GenericASTTraversal.__init__(self, ast)
        self.SignTable = SignTable()
        self.cur_kind = ''
        self.cur_name = ''
        self.cur_module =''
        self.cur_type =''
        ##----used in range
        self.sb_flag =False
        self.cur_msb = 0
        self.cur_lsb = 0
        self.size = 0
        ##----------------
        ##------ used in port/normal_wire declaration 
        self.wire_type = ''  # wire or reg   in the port/normal net

        self.dec_flag =False # used in input and output declare
        self.reg_flag =False # used in input and output declare
        ##----------------
        self.cur_num = 0

        ##------
        self.com_flag = False  # used in combine
        self.tmp_rv = []

        ##----- used in assign
        self.left_var = ''
        self.right_var =''
        ## 
        self.alw_flag =False
        self.glo_trigger_flag = False
        self.trigger_rv = []

    def check_is_decla(self) :
        return  self.dec_flag

    def new_decla(self) :
        if not self.dec_flag  :
            return  
        st = Sign(self.cur_kind,self.cur_name, typer=self.wire_type )  

        if self.sb_flag :
            st.add_boundary(self.cur_msb,self.cur_lsb)
        if self.cur_kind != 'MODULE':
            st.add_upper(self.cur_module)
        # if self.reg_flag :
        #     st.add_port(self.wire_type)

        self.SignTable.add(st)


        self.cur_msb = 0
        self.dec_flag = False
        self.sb_flag = False
        self.reg_flag = False
        pass


    def traverse(self,node):
        self.preorder(node)
        return 'ok'

    # Rules for interpreting nodes based on their AST node type
    def n_integer(self, node):
        node.attr = int(node.attr)

    def n_single(self, node):
        # node = node[0]
        pass

    
    def n_NAME(self,node):
        self.cur_name = node.name
        if self.check_is_decla():
            self.new_decla()
            self.prune()
        if self.com_flag :
            self.tmp_rv.append(node.name)

        if self.glo_trigger_flag == True :
            self.trigger_rv.append(node.name)


                
    
    def n_COMBINE(self,node):
        self.conbine_flag = True

    def n_COMBINE_OVER(self,node):
        
        tmp_wire = self.gen_tmp()

        sum_width =0
        for item in self.tmp_rv :
            sum_width =sum_width + item.getsize()
        self.cur_msb = sum_width 
        self.cur_lsb = 0
        self.cur_kind = 'NORMAL'
        self.cur_type = 'WIRE'
         
        self.dec_flag = True ## generate a tmp_wire ,we need a permission
        self.cur_name = tmp_wire
        self.new_decla()

        ##todo: split

        self.com_flag = False 
        self.tmp_rv.clear()

    def n_ASSIN_OVER(self,node):
        ##todo: assign 

        left = self.left_var
        right = self.cur_name 


        pass     

    def n_LEFT_OVER(self,node):
        self.left_var = self.cur_name

    def n_multiply(self, node):
        node.attr = int(node[0].attr) * int(node[1].attr)

    def n_divide(self, node):
        node.attr = int(node[0].attr) / int(node[1].attr)

    def n_add(self, node):
        node.attr = int(node[0].attr) + int(node[1].attr)

    def n_subtract(self, node):
        node.attr = int(node[0].attr) - int(node[1].attr)


    def n_MODULE(self,node):
        self.cur_kind = 'MODULE'
        self.dec_flag = True
        node.kind= 'Mood'

    def n_PORTs(self,node):
        self.cur_kind = 'PORT'
        self.cur_module = self.cur_name 
        self.dec_flag = True

    def n_PORT_ident(self,node):
        tmp = node[0]
        self.cur_name = tmp.data[0].name
        self.new_decla()

        self.prune()

    def n_INPUT(self,node):
        self.cur_kind='INPUT'
        self.wire_type ='WIRE'
        self.cur_module = self.cur_name 
        self.dec_flag = True

    def n_OUTPUT(self,node):
        self.cur_kind='OUTPUT'
        self.wire_type ='WIRE'
        self.cur_module = self.cur_name 
        self.dec_flag = True


    def n_RANGE(self,node):
        self.sb_flag =True
    
    def n_NUMBER(self,node):
        if self.sb_flag and (self.cur_msb==0):
            self.cur_msb = int(node.data[0].name)
        else :
            self.cur_lsb = int(node.data[0].name)
        self.cur_num = node.data[0].name
        self.prune()

    def n_REG(self,node):
        self.reg_flag = True

    def n_dec_reg_flag(self,node):
        self.cur_kind = 'NORMAL'
        self.wire_type='REG'
        self.dec_flag = True
        self.SignTable.check_dup(self.cur_name)
        self.new_decla()

    ##----used in always block
    def n_ALWAYS(self,node):
        self.alw_flag = True
    
    def n_Trigger(self,node):
        self.glo_trigger_flag =True

    def n_TriggerEnd(self,node):
        self.glo_trigger_flag = False
        

    def default(self, node):
        pass



def parse_VeriSim(VeriSim_tokens, start='translation_unit',
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
    sema=  Interpret(ast)
    res = sema.traverse(ast)

    print("dormouse-semantics-end!")
    pass
