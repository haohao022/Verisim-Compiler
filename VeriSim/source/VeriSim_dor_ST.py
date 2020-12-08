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

    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.attr)
