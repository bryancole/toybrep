'''
Created on 21 Dec 2010

@author: bryan cole
'''
import pyximport; pyximport.install()
from cstep import ResolvedEntity, entity_classes, CartesianPoint, Star, step_type, Direction
        

@step_type("VECTOR")
class Vector(ResolvedEntity):
    def __init__(self, name, direction, length):
        self.name = name
        self.direction = direction #a Direction instance
        self.length = length


class Curve(ResolvedEntity):
    """ABC for 1D geometry"""
    
    
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
    
    
@step_type("PLANE")
class Plane(Surface):
    """A planar surface"""
    def __init__(self, name, axis2):
        self.name = name
        self.axis2 = axis2
        
    def tesselate_face(self, face):
        pass
        

@step_type("AXIS2_PLACEMENT_3D")
class Axis2Placement3D(ResolvedEntity):
    def __init__(self, name, location, axis, ref_direction):
        self.name = name
        self.location = location # a CartesianPoint
        self.axes = axis #a Direction
        self.ref_direction = ref_direction #a Direction
        