'''
Created on 21 Dec 2010

@author: bryan cole
'''
import pyximport; pyximport.install()
from cstep import ResolvedEntity, entity_classes, CartesianPoint, Star, step_type
from weakref import proxy, WeakSet

from collections import defaultdict, deque


class TopologyError(Exception):
    pass



@step_type("MANIFOLD_SOLID_BREP")
class BrepSolid(ResolvedEntity):
    def __init__(self, name, shell):
        self.name = name
        self.shell = shell
        shell.owner = proxy(self)
        
        self.vertices = WeakSet(shell.vertices())
        self.edges = WeakSet(shell.edges())
        
    def copy_topology(self):
        memo = {}
        shell = self.shell.copy_topology(memo)
        return BrepSolid("", shell)
    
    def as_polydata(self):
        copy = self.copy_topology()
        shell = copy.shell
        shell.tesselate(tolerance=0.001)
        verts = list(set(shell.vertices()))
        point_map = dict((v,i) for i,v in enumerate(verts))
        cells = [[point_map[v] for v in face.vertices()] for face in shell.faces]
        points = [tuple(v) for v in verts]
        return points, cells
    
    def as_wireframe(self):
        copy = self.copy_topology()
        shell = copy.shell
        shell.tesselate_edges()
        verts = list(set(shell.vertices()))
        point_map = dict((v,i) for i,v in enumerate(verts))
        edges = set(shell.edges())
        cells = [(point_map[e.start_vertex], point_map[e.end_vertex]) for e in edges]
        points = [tuple(v) for v in verts]
        return points, cells
        
        
@step_type("CLOSED_SHELL")
class ClosedShell(ResolvedEntity):
    def __init__(self, name, faces):
        self.name = name
        self.faces = set(faces)
        
    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        else:
            copy = ClosedShell("", set(f.copy_topology(memo) for f in self.faces))
            memo[self] = copy
            return copy
        
    def tesselate(self, tolerance=0.001):
        for face in self.faces:
            face.tesselate()
            
    def tesselate_edges(self):
        edges = set(self.edges())
        for e in edges:
            e.tesselate()
            
    def edge_set(self):
        base = self.faces.copy().pop().bounds.copy().pop().bound.base_edge
        stack = deque([base])
        seen = set()
        while stack:
            edge = stack.popleft()
            seen.add(edge)
            for e in (edge.left_cc_edge, edge.right_cc_edge, edge.left_cw_edge, edge.right_cw_edge):
                if e not in seen:
                    stack.append(e)
        return seen
        
    def edges(self):
        for face in self.faces:
            for edge, o in face.edges():
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
        
    def tesselate(self):
        self.geometry.tesselate_face(self)
        
    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        else:
            copy =  AdvancedFace("",
                                set(b.copy_topology(memo) for b in self.bounds),
                                self.geometry,
                                self.sense
                                )
            memo[self] = copy
            return copy
        
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
        
    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        else:
            copy = type(self)("", 
                              self.bound.copy_topology(memo),
                              self.orientation)
            memo[self] = copy
            return copy

        
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
            assert tuple(e for e,o in self.edges()) == tuple(oe.subedge for oe in edge_list)
        except AssertionError:
            print tuple(e.eid for e,o in self.edges())
            print tuple(oe.subedge.eid for oe in edge_list)
            raise
        
    def divide(self, start_vertex, end_vertex, curve):
        """Creates a new edge between the given vertices
        to divide the loop in two. The new loop is returned.
        curve - the geometry to be associated with the new edge
        """
        
        
        
    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        else:
            copy = EdgeLoop.__new__(EdgeLoop)
            super(EdgeLoop, copy).__init__("")
            memo[self] = copy
            edges = [e.copy_topology(memo) for e,o in self.edges()]
            copy.base_edge = memo[self.base_edge]
            return copy
        
        
    def edges(self):
        this = base = self.base_edge
        if this.right_loop is self:
            last = base_last = this.right_cc_edge
            orientation = True
        else:
            last = base_last = this.left_cc_edge
            orientation = False
            
        yield this, orientation
        
        while True:
            if this.right_cc_edge is last:
                next = this.right_cw_edge
                last = this
                this = next
                orientation = True
            elif this.left_cc_edge is last:
                next = this.left_cw_edge
                last = this
                this = next
                orientation = False
            else:
                raise TopologyError("Edge loop incorrectly connected")
                
            if (this, last) == (base, base_last):
                break
            yield this, orientation
            
    def vertices(self):
        this = base = self.base_edge
        while True:
            if this.right_loop is self:
                yield this.start_vertex
                this = this.right_cw_edge
            else:
                yield this.end_vertex
                this = this.left_cw_edge
            if this is base:
                    break
                    

            

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
        
    def split(self, point):
        """Subdivide this edge at the given point.
        No checking is performed to verify if the point lies on the curve
        The new vertex and edge are returned
        """
        vertex = Vertex("", point)
        edge = EdgeCurve("", vertex, self.end_vertex, self.curve, self.sense)
        edge.left_loop = self.left_loop
        edge.right_loop = self.right_loop
        edge.left_cc_edge = self.left_cc_edge
        edge.right_cw_edge = self.right_cw_edge
        edge.left_cw_edge = self
        edge.right_cc_edge = self
        
        left_cc_edge = self.left_cc_edge #need to update the adjacent edges
        if left_cc_edge.start_vertex == edge.end_vertex:
            left_cc_edge.left_cw_edge = edge
        else:
            left_cc_edge.right_cw_edge = edge
            
        right_cw_edge = self.right_cw_edge
        if right_cw_edge.start_vertex == edge.end_vertex:
            right_cw_edge.right_cc_edge = edge
        else:
            right_cw_edge.left_cc_edge = edge
        
        self.left_cc_edge = edge
        self.right_cw_edge = edge
        self.end_vertex = vertex
        return vertex, edge
        
    def tesselate(self):
        try:
            self.curve.tesselate(self)
        except AttributeError:
            if isinstance(self.curve, tuple):
                print "Can't interpret a tuple yet", self.curve
            raise
        
    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        copy = EdgeCurve("",
                         self.start_vertex.copy_topology(memo),
                         self.end_vertex.copy_topology(memo),
                         self.curve,
                         self.sense)
        memo[self] = copy
        copy.left_loop = self.left_loop.copy_topology(memo) 
        copy.right_loop = self.right_loop.copy_topology(memo)
        copy.left_cc_edge = self.left_cc_edge.copy_topology(memo)
        copy.left_cw_edge = self.left_cw_edge.copy_topology(memo)
        copy.right_cc_edge = self.right_cc_edge.copy_topology(memo)
        copy.right_cw_edge = self.right_cw_edge.copy_topology(memo)
        return copy
        

@step_type("VERTEX_POINT")  
class Vertex(ResolvedEntity):
    def __init__(self, name, point):
        self.name = name
        if not isinstance(point, CartesianPoint):
            print "make point", type(point)
            self.point = CartesianPoint('', point)
        else:
            self.point = point

    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        copy = Vertex("", self.point)
        memo[self] = copy
        return copy
    
    def __getitem__(self, idx):
        return self.point[idx]