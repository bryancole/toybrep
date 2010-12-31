'''
Created on 21 Dec 2010

@author: bryan cole
'''
import pyximport; pyximport.install()
from cstep import ResolvedEntity, entity_classes, CartesianPoint, Star
from weakref import proxy, WeakSet

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
        shell.owner = proxy(self)
        
        self.vertices = WeakSet(shell.vertices())
        self.edges = WeakSet(shell.edges())
        
        
@step_type("CLOSED_SHELL")
class ClosedShell(ResolvedEntity):
    def __init__(self, name, faces):
        self.name = name
        self.faces = set(faces)
        
    def edges(self):
        for face in self.faces:
            for edge in face.edges():
                yield edge
                
    def vertices(self):
        for face in self.faces:
            for vert in face.vertices():
                yield vert 
        
        
@step_type("ADVANCED_FACE")
class AdvancedFace(ResolvedEntity):
    def __init__(self, name, bounds, geometry, sense):
        self.name = name
        self.bounds = set(bounds)
        self.geometry = geometry
        self.sense = bool(sense)
        
    def edges(self):
        for bound in self.bounds:
            for edge in bound.bound.edges():
                yield edge
                
    def vertices(self):
        for bound in self.bounds:
            for vert in bound.bound.vertices():
                yield vert
        
        
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
        #self.edges = list(edge_list) #must be oriented edges
        N = len(edge_list)
        for i, oe in enumerate(edge_list):
            edge = oe.subedge
            orientation = oe.orientation
            if orientation:
                edge.right_loop = self
                edge.right_cw_edge = edge_list[(i+1)%N].subedge
                edge.right_cc_edge = edge_list[i-1].subedge
            else:
                edge.left_loop = self
                edge.left_cw_edge = edge_list[(i+1)%N].subedge
                edge.left_cc_edge = edge_list[i-1].subedge
        self.base_edge = edge_list[0].subedge
        
        try:
            assert tuple(self.edges()) == tuple(oe.subedge for oe in edge_list)
        except AssertionError:
            print tuple(e.eid for e in self.edges())
            print tuple(oe.subedge.eid for oe in edge_list)
            raise
                
                
    def edges(self):
        this = base = self.base_edge
        yield this
        while True:
            if this.right_loop is self:
                this = this.right_cw_edge
            else:
                this = this.left_cw_edge
            if this is base:
                break
            yield this
            
    def vertices(self):
        this = base = self.base_edge
        if this.right_loop is self:
            v = this.start_vertex
        else:
            v = this.end_vertex
        yield v
        while True:
            if this.right_loop is self:
                this = this.right_cw_edge
                v = this.start_vertex
            else:
                this = this.left_cw_edge
                v = this.end_vertex
            if this is base:
                break
            yield v
            

@step_type("EGDE")
class Edge(ResolvedEntity):
    def __init__(self, name, start_vertex, end_vertex):
        self.name = name
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        

@step_type("ORIENTED_EDGE")
class OrientedEdge(Edge):
    def __init__(self, name, start_vertex, end_vertex, subedge, orientation):
        if not all(isinstance(o, Star) for o in (start_vertex, end_vertex)):
            raise ValueError("Don't know what to do about non-star vertices")
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
        
        self.left_loop = None
        self.right_loop = None
        self.left_cc_edge = None
        self.left_cw_edge = None
        self.right_cc_edge = None
        self.right_cw_edge = None
        

@step_type("VERTEX_POINT")  
class Vertex(ResolvedEntity):
    def __init__(self, name, point):
        self.name = name
        if not isinstance(point, CartesianPoint):
            print "make point", type(point)
            self.point = CartesianPoint('', *point)
        else:
            self.point = point
