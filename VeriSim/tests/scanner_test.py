
import os,sys
os.chdir(sys.path[0])
sys.path.append('..')
sys.path.append('../source')
from source.VeriSim_Scanner import *




def do_scanner(name) :
    scan = VeriSimScanner()
    def showit(expr) : 
        print(expr)
        tokens = scan.tokenize(expr+ENDMARKER)
        for t in tokens : print(t)
        return 
    
    src = open(name)

    showit(src.read())


if __name__ == '__main__' :
    # if len(sys.argv) <2 :
    #     print('Usage: python %s source-file' % (sys.argv[0]) )
    # else :
    #     print('Dormouse: VeriSim_Scanner  : scan  %s '% (sys.argv[1])  )
    tokens = do_scanner('./scan_test/adder.v') 
