
from brep.step import STEPLoader

#testdata = "../step_data/two_blocks.stp"
testdata = "../step_data/cut_cube.stp"
#testdata = "../step_data/multi_holes.stp"
#testdata = "../step_data/TDR_step/TPR_beta_design_13-5-10.STEP"
testdata = "../step_data/cylinder.stp"
testdata = "../step_data/block_with_hole.stp"
testdata = "../step_data/optical_mount.stp"

loader = STEPLoader(testdata)

doc = loader.parse_document()

print doc.HEADER

for item in doc.roots:
    print item.eid, ":", item
    

solids = [o for o in doc.roots if type(o).__name__=="SHAPE_REPRESENTATION_RELATIONSHIP"]
print "Solids:", len(solids)
#print solids[0].args[3]
print "all", len(doc.manifold_solids)

solid = doc.manifold_solids.pop()
print "edges>", len(solid.edges)
print "verts>", len(solid.vertices)

#s2 = solid.copy_topology()
#
#print "edges>", len(s2.edges)
#print "verts>", len(s2.vertices)
#
#print solid.as_polydata()

from brep.display import show_solid

edges = set(solid.shell.edges())

#for edge in edges:
#    pt = ((a+b)/2. for a,b in zip(edge.start_vertex, edge.end_vertex))
#    edge.split(pt)

show_solid(solid, wireframe=True)

#print "edges", len(s2.edges())
#for item, val in doc.DATA.items():
#    print item, val
    
