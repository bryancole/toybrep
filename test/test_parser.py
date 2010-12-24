
from brep.step import STEPLoader

testdata = "../step_data/two_blocks.stp"

loader = STEPLoader(testdata)

doc = loader.parse_document()

print doc.HEADER

for item, val in doc.DATA.items():
    print item, val