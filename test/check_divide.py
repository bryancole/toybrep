
from brep.step import STEPLoader
from brep import topo, geom

testdata = "../step_data/block.stp"


loader = STEPLoader(testdata)

doc = loader.parse_document()


solid = list(doc.manifold_solids)[0]

faces = solid.shell.faces
for face in faces.copy():
    for b in face.bounds:
        loop = b.bound
        verts = list(loop.vertices())
        v1,v2,v3,v4 = verts
        line = geom.Line.from_points(v1.point, v2.point)
        new_loop = loop.divide(v1,v3, line, True)
        B = topo.FaceOuterBound("", new_loop, b.orientation)
        new_face = topo.AdvancedFace("", set([B]), face.geometry, face.sense)
        faces.add(new_face)

from brep.display import show_solid

show_solid(solid, wireframe=True)

#print "edges", len(s2.edges())
#for item, val in doc.DATA.items():
#    print item, val
    