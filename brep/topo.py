'''
Created on 21 Dec 2010

@author: bryan cole
'''
import pyximport; pyximport.install()
from cstep import ResolvedEntity, entity_classes, CartesianPoint, Star, step_type
from weakref import proxy, WeakSet

from collections import defaultdict, deque
from itertools import izip, tee


def pairs(itr):
    a,b = tee(itr)
    b.next()
    return izip(a,b)


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
        
        #test
        s1 = set(e.start_vertex for e in shell.edges())
        s1.update(e.end_vertex for e in shell.edges())
        assert (s1 == set(shell.vertices()))
        
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
                
    def normal(self, point):
        if self.sense:
            return self.geometry.normal(point)
        else:
            return -self.geometry.normal(point)
                
    def concave(self): ###untested###
        for bound in self.bounds:
            loop = bound.bound
            edges = list(loop.edges())
            edges = [edges[-1]] + edges
            edge_pairs = pairs(edges)
            for (e1,o1),(e2,o2) in edge_pairs:
                v1 = e1.end_vertex if o1 else e1.start_vertex
                v2 = e2.start_vertex if o2 else e2.end_vertex
                assert v1 is v2
                p = v1.point
                d1 = e1.tangent(p)
                d2 = e2.tangent(p)
                n = self.normal(p)
                if d1.cross(d2).dot(n)<0:
                    yield v1
        
        
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
        
    def join(self, other, start_vertex, end_vertex, curve, sense):
        """
        Make an edge between two loops, destroying the other loop as a result.
        The caller must ensure the edge lies fully inside the owning face. 
        This is not checked.
        
        other - an other loop in the same face
        start_vertex, end_vertex - start and end vertices of the new edge.
            Must be in different loops.
        curve - geometry of the new edge
        sense - orientation of the geometry
        """
        this_edges = list(self.edges())
        this_verts = list(self.vertices())
        other_edges = list(other.edges())
        other_verts = list(other.vertices())
        
        assert ((start_vertex in this_verts) and (end_vertex in other_verts)) or \
            ((end_vertex in this_verts) and (start_vertex in other_verts))
        
        
    def divide(self, start_vertex, end_vertex, curve, sense):
        """Creates a new edge between the given vertices
        to divide the loop in two. The new loop is returned.
        
        curve - the geometry to be associated with the new edge
        sense - direction of edge w.r.t. curve
        
        The two vertices must already lie in the loop.
        The curve must lie in the surface of the owning face (not checked)
        such that the new edge lies wholely in within the original face.
        """
        verts = set(self.vertices())
        edges = set(self.edges())
        assert (start_vertex in verts) and (end_vertex in verts)
        
        e_new = EdgeCurve("", start_vertex, end_vertex, curve, sense)
        
        l_new = EdgeLoop.__new__(EdgeLoop)
        l_new.name = ""
        l_new.base_edge = e_new
        
        edge_iter = self.edges()
        pair = set([start_vertex, end_vertex])
        
        e1,o1 = edge_iter.next()
        v1 = e1.end_vertex if o1 else e1.start_vertex
        while v1 not in pair:
            print "find v1"
            e1,o1 = edge_iter.next()
            v1 = e1.end_vertex if o1 else e1.start_vertex
            
        e2, o2 = edge_iter.next()
        if o2:
            e2.right_loop = l_new
        else:
            e2.left_loop = l_new
        
        pair.remove(v1)
        v_end = pair.pop()
        
        v2 = e2.end_vertex if o2 else e2.start_vertex
        while v2 is not v_end:
            print "find v2"
            e3, o3 = edge_iter.next()
            if o3:
                v2 = e3.end_vertex
                e3.right_loop = l_new
            else:
                v2 = e3.start_vertex
                e3.left_loop = l_new
            
        e4, o4 = edge_iter.next()
        
        if (v1,v2) == (start_vertex, end_vertex):
            e_new.right_loop = self
            e_new.left_loop = l_new
            e_new.right_cc_edge = e1
            e_new.right_cw_edge = e4
            e_new.left_cw_edge = e2
            e_new.left_cc_edge = e3
        elif (v2,v1) == (start_vertex, end_vertex):
            e_new.right_loop = l_new
            e_new.left_loop = self
            e_new.left_cc_edge = e1
            e_new.left_cw_edge = e4
            e_new.right_cw_edge = e2
            e_new.right_cc_edge = e3
        else:
            raise TopologyError("extraced vertices don't match given ones")
        
        if o1:
            e1.right_cw_edge = e_new
        else:
            e1.left_cw_edge = e_new
            
        if o2:
            e2.right_cc_edge = e_new
        else:
            e2.left_cc_edge = e_new
            
        if o3:
            e3.right_cw_edge = e_new
        else:
            e3.left_cw_edge = e_new
            
        if o4:
            e4.right_cc_edge = e_new
        else:
            e4.left_cc_edge = e_new
            
        return l_new
        
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
        else:
            last = base_last = this.left_cc_edge
        while True:
            if this.right_cc_edge is last:
                next = this.right_cw_edge
                yield this, True
            elif this.left_cc_edge is last:
                next = this.left_cw_edge
                yield this, False
            else:
                raise TopologyError("Edge loop incorrectly connected")
            last = this
            this = next
            if (this, last) == (base, base_last):
                break
            
    def vertices(self):
        for e,o in self.edges():
            if o:
                yield e.end_vertex
            else:
                yield e.start_vertex
        
            

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
        
        if start_vertex.edge is None:
            start_vertex.edge = self
        if end_vertex.edge is None:
            end_vertex.edge = self
            
    def tangent(self, point):
        if self.sense:
            return self.curve.tangent(point)
        else:
            return -self.curve.tangent(point)
        
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
        
        vertex.edge = edge
        
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
        copy = EdgeCurve.__new__(EdgeCurve)
        memo[self] = copy
        EdgeCurve.__init__(copy, "",
                         self.start_vertex.copy_topology(memo),
                         self.end_vertex.copy_topology(memo),
                         self.curve,
                         self.sense)
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
            self.point = CartesianPoint('', point)
        else:
            self.point = point
        self.edge = None

    def copy_topology(self, memo):
        if self in memo:
            return memo[self]
        copy = Vertex("", self.point)
        memo[self] = copy
        copy.edge = self.edge.copy_topology(memo)
        return copy
    
    def edges(self):
        """iterate edges clockwise round the vertex"""
        this = base = self.edge
        if base is None:
            return
        
        if base.end_vertex is self:
            last_loop = base_loop = base.right_loop
        elif base.start_vertex is self:
            last_loop = base_loop = base.left_loop
        else:
            raise TopologyError("vertex base edge doesn't contain vertex")
        
        while True:
            yield this
            if this.right_loop == last_loop:
                last_loop = this.left_loop
                this = this.left_cc_edge
            elif this.left_loop == last_loop:
                last_loop = this.right_loop
                this = this.right_cc_edge
            else:
                raise TopologyError("Incorrectly connected edges at vertex")
            if (this, last_loop) == (base, base_loop):
                break
    
    def __getitem__(self, idx):
        return self.point[idx]