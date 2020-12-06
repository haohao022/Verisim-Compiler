from spark_parser.scanner import  GenericToken
class VeriSimToken(GenericToken):
    def __init__(self, kind, name):
        self.kind = kind
        self.name = name

    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.name)
