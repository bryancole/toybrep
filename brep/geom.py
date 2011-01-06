'''
Created on 21 Dec 2010

@author: bryan cole
'''
import pyximport; pyximport.install()
from cstep import ResolvedEntity, entity_classes, CartesianPoint, Star, step_type, Direction
from math import sqrt, cos, sin, pi, acos, asin, ceil
from brep.transforms import Transform
from brep.nurbs import NurbsCurve
import bisect


ARC_RESOLUTION = 2*pi/128.


def rotate_point(point, origin, direction, angle):
    '''
    rotates points about the given axis by the given angle
    returns a list of CartesianPoint instances
    
    @param points: a 3-sequences
    @param origin: 3-sequence giving the location
    @param direction: 3-sequence giving the axis direction
    @param angle: rotate angle in radians
    '''
    x,y,z = point
    a,b,c = origin
    u,v,w = direction
    L = u*u + v*v + w*w
    cosA = cos(angle)
    sinA = sin(angle)
    
    X = ( a*(v*v + w*w) + u*(-b*v - c*w + u*x + v*y + w*z) \
          + (-a*(v*v + w*w) + u*(b*v + c*w - v*y - w*z) + (v*v + w*w)*x )*cosA \
          + sqrt(L)*(-c*v + b*w - w*y + v*z)*sinA \
        ) / L
        
    Y = ( b*(u*u + w*w) + v*(-a*u - c*w + u*x + v*y + w*z) \
          + (-b*(u*u + w*w) + v*(a*u + c*w - u*x - w*z) + (u*u + w*w)*y )*cosA \
          + sqrt(L)*(c*u - a*w + w*x - u*z)*sinA \
        ) / L
    
        

@step_type("VECTOR")
class Vector(ResolvedEntity):
    def __init__(self, name, direction, length):
        self.name = name
        self.direction = direction #a Direction instance
        self.length = length


class Curve(ResolvedEntity):
    """ABC for 1D geometry"""
    def tesselate(self, edge):
        pass
    
    
class Surface(ResolvedEntity):
    """ABC for 2D geometry"""
    def tesselate_face(self, face):
        raise NotImplementedError
    
    
@step_type("LINE")
class Line(Curve):
    """A straight curve"""
    def __init__(self, name, origin, vector):
        self.name = name
        self.origin = origin
        self.vector = vector
        
    def tesselate(self, edge):
        pass
        

@step_type("CIRCLE")
class Circle(Curve):
    def __init__(self, name, position, radius):
        self.name = name
        assert isinstance(position, Axis2Placement3D)
        self.position = position #a axis2_placement: usually an Axis2Placement3D
        self.radius = radius #a positive float
        
    def tesselate(self, edge):
        start = edge.start_vertex.point
        end = edge.end_vertex.point
        #print "TESS", start, end
        sense = edge.sense
        
        centre = self.position.location
        axis = self.position.axis.unit()
        
        #print "TESS", start, end, centre, axis
        #get angle round the arc
        v1 = (start - centre).unit()
        v2 = (end - centre).unit()
        
        cp = v1.cross(v2).dot(axis)
        dp = v1.dot(v2)
        
        if dp**2 < 0.5:
            theta = acos(dp)
            if cp < 0:
                theta = 2*pi - theta
        else:   
            theta = asin(cp)
            if dp < 0:
                theta = pi - theta
                
        nsegments = ceil(theta/ARC_RESOLUTION)
        dtheta = theta / nsegments
        
        T = Transform()
        T.rotate_axis(centre, axis, dtheta)
        
        new_points = []
        pt = start
        for i in xrange(int(nsegments)-1):
            pt = CartesianPoint("", T.transform_point(pt))
            new_points.append(pt)
            
        for pt in reversed(new_points):
            edge.split(pt)
            
            
@step_type("B_SPLINE_CURVE_WITH_KNOTS")
class BSplineCurveWithKnots(Curve):
    def __init__(self, *args):
        """
        
        @param name:
        @param degree: integer
        @param control_points: list of CartesianPoints
        @param form: enum (polyline_form, circular_arc, 
                  elliptic_arc, parabolic_arc, hyperbolic_arc, 
                  unspecified)
        @param closed: bool
        @param selfintersect: bool
        @param multiplicities: list of ints
        @param knots: list of floats
        @param knot_type: enum (uniform_knots, quasi_uniform_knots, 
                piecewise_bezier_knots, unspecified)
        """
        try:
            self.name = args[0]
            self.degree = args[1]
            self.control_points = args[2]
            self.form = args[3]
            self.closed = bool(args[4])
            self.selfintersect = bool(args[5])
            self.multiplicities = args[6]
            self.knots = args[7]
            self.knot_type = args[8]
            
            print self.degree
            print self.knots
            print self.control_points
            print self.multiplicities
                
            self.NC = NurbsCurve(int(self.degree), 
                                 list(self.knots), 
                                 list(self.control_points), 
                                 [int(a) for a in self.multiplicities])
        except IndexError:
            print "Bad Bad B-Spline"
    
    def evalutate(self, u):
        return CartesianPoint("", self.NC.evaluate(u))
        
    def tesselate(self, edge):
        N = 300
        new_points = (self.NC.evaluate(i/float(N)) for i in xrange(1,N))
        new_ct = [CartesianPoint("", a) for a in new_points]    
        for pt in reversed(new_ct):
            print pt
            edge.split(pt)
    
    
@step_type("PLANE")
class Plane(Surface):
    """A planar surface"""
    def __init__(self, name, axis2):
        self.name = name
        self.axis2 = axis2
        
    def tesselate_face(self, face):
        pass
    
    
@step_type("CYLINDERICAL_SURFACE")
class CylindericalSurface(Surface):
    def __init__(self, name, position, radius):
        self.name = name
        self.position = position #an Axis2Placement3d
        self.radius = radius #a positive float
        

@step_type("AXIS2_PLACEMENT_3D")
class Axis2Placement3D(ResolvedEntity):
    def __init__(self, name, location, axis, ref_direction):
        self.name = name
        self.location = location # a CartesianPoint
        self.axis = axis #a Direction
        self.ref_direction = ref_direction #a Direction
        