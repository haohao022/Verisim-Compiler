from spark_parser.scanner import  GenericToken


class SignTable(GenericToken):

    def __init__(self):
        self.rv = []

    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.attr)


    def add(self, node ):
        assert isinstance(node, Sign)
        self.rv.append(node)        
        pass
    
    def check_dup(self, name):
        for item in self.rv :
            if( item.getname() == name ):
                print("ERROR: Dormouse . duplicate ident for wire/ reg ")
                exit(0)
        return 

class Sign:

    def __init__(self, kind , name ,upper=None ,typer=None):
        self.kind = kind
        self.name = name
        self.type = typer
        self.upper = upper
        self.msb = 0
        self.lsb = 0
        self.size = 1

    def add_boundary(self , msb,lsb):
        self.msb = msb 
        self.lsb = lsb
        self.size = msb - lsb + 1
    
    def add_upper(self,upper):
        self.upper = upper

    def add_reg(self):
    #    self.subtype = 'REG'
        pass

    def getname(self):
        return self.name 
        
    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.attr)
    
