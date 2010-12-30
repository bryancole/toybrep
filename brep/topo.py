'''
Created on 21 Dec 2010

@author: bryan cole
'''
import pyximport; pyximport.install()
from cstep import ResolvedEntity, entity_classes, CartesianPoint

def step_type(name):
    def wrapper(cls):
        entity_classes[name] = cls
        cls.step_type = name
        return cls
    return wrapper


@step_type("MANIFOLD_SOLID_BREP")
class BrepSolid(ResolvedEntity):
    def __init__(self, name, shell):
        self.name = name
        self.shell = shell
        
        
@step_type("CLOSED_SHELL")
class ClosedShell(ResolvedEntity):
    def __init__(self, name, faces):
        self.name = name
        self.faces = set(faces)
        
        
@step_type("ADVANCED_FACE")
class AdvancedFace(ResolvedEntity):
    def __init__(self, name, bounds, geometry, sense):
        self.name = name
        self.bounds = set(bounds)
        self.geometry = geometry
        self.sense = bool(sense)
        
        
@step_type("FACE_BOUND")
class FaceBound(ResolvedEntity):
    def __init__(self, name, bound, orientation):
        self.name = name
        self.bound = bound #a Loop object
        self.orientation = bool(orientation)

        
@step_type("FACE_OUTER_BOUND")
class FaceOuterBound(FaceBound):
    pass


@step_type("LOOP")
class Loop(ResolvedEntity):
    def __init__(self, name):
        self.name = name
        
        
@step_type("EDGE_LOOP")
class EdgeLoop(Loop):
    def __init__(self, name, edge_list):
        super(EdgeLoop, self).__init__(name)
        self.edges = list(edge_list) #must be oriented edges
        

@step_type("EGDE")
class Edge(ResolvedEntity):
    def __init__(self, name, start_vertex, end_vertex):
        self.name = name
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        

@step_type("ORIENTED_EDGE")
class OrientedEdge(Edge):
    def __init__(self, name, start_vertex, end_vertex, subedge, orientation):
        self.name = name
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.subedge = subedge
        self.orientation = bool(orientation)
        
        
@step_type("EDGE_CURVE")
class EdgeCurve(Edge):
    def __init__(self, name, start_vertex, end_vertex, curve, sense):
        self.name = name
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.curve = curve
        self.sense = bool(sense)
        

@step_type("VERTEX_POINT")  
class Vertex(ResolvedEntity):
    def __init__(self, name, point):
        self.name = name
        if not isinstance(point, CartesianPoint):
            print "make point", type(point)
            self.point = CartesianPoint('', *point)
        else:
            self.point = point
