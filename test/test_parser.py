
from brep.step import STEPLoader

#testdata = "../step_data/two_blocks.stp"
testdata = "../step_data/TDR_step/TPR_beta_design_13-5-10.STEP"

loader = STEPLoader(testdata)

doc = loader.parse_document()

print doc.HEADER

#for item, val in doc.DATA.items():
#    print item, val
    
print len(doc.free_items), len(doc.DATA)
print "FREE ITEMS>>>"
for item in doc.free_items:
    print item.eid, item