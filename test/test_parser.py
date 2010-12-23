
from brep.step import STEPLoader

testdata = "../step_data/two_blocks.stp"

loader = STEPLoader('')

def echo(fobj):
    for i, line in enumerate(fobj):
        print i, ">>>", line
        yield line

with open(testdata) as fobj:
    for line in fobj:
        if line == "DATA;\n":
            break
    
    fitr = iter(fobj)
    while True:
        item = loader.parse_statement(fitr)
        print item[0], '>', item[1]