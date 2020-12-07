


class AstNode(GenericToken):

    def __init__(self):
        self.rv = []

    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.attr)

    def add_node(self,node ):
        self.rv.append(node)
        pass


class Signal_table:

    def __init__(self):
        self.rv = []
        

    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.attr)

    def add_node(self,node ):
        self.rv.append(node)
        pass