from spark_parser.scanner import  GenericToken
class VeriSimToken(GenericToken):
    def __init__(self, kind, name,line,column):
        self.kind = kind
        self.name = name
        ##--- print line_num and column 
        self.line = line
        self.column = column

    def __str__(self):
    #    return 'Token %s: %r ' %( self.kind, self.name)
        return 'L%d.%d: %s: %r' % (self.line, self.column, self.kind, self.name)