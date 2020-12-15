
import os,sys
os.chdir(sys.path[0])
sys.path.append('..')
sys.path.append('../source')
from source.VeriSim_Parser import parse_VeriSim
from source.VeriSim_Scanner import *


if __name__ == '__main__':
    # if len(sys.argv) <2 :
    #     print('Usage: python %s source-file' % (sys.argv[0]) )
    # else :
    #     print('Dormouse: VeriSim_parser  : scan  %s '% (sys.argv[1])  )
    src = open('./parse/adder.v')
    scan = VeriSimScanner()
    tokens = scan.tokenize(src.read() + ENDMARKER)
    ast = parse_VeriSim(tokens, start='translation_unit', show_tokens=False, check=False)
    print(ast)
    print("DORMOUSE+==========parse +end")