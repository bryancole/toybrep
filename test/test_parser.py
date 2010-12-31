
from brep.step import STEPLoader

testdata = "../step_data/two_blocks.stp"
#testdata = "../step_data/TDR_step/TPR_beta_design_13-5-10.STEP"

loader = STEPLoader(testdata)

doc = loader.parse_document()

print doc.HEADER

for item in doc.roots:
    print item.eid, ":", item
    

solids = [o for o in doc.roots if type(o).__name__=="SHAPE_REPRESENTATION_RELATIONSHIP"]
print "Solids:", len(solids)
print solids[0].args[3]
print "all", len(doc.manifold_solids)
#for item, val in doc.DATA.items():
#    print item, val
    
