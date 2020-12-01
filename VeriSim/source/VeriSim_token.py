from spark_parser.scanner import  GenericToken
class VeriSimToken(GenericToken):
    def __init__(self, kind, attr):
        self.kind = kind
        self.attr = attr

    def __str__(self):
        return 'Token %s: %r ' %( self.kind, self.attr)
