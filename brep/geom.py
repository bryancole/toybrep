'''
Created on 21 Dec 2010

@author: bryan cole
'''

class Point(object):
    __slots__=['x', 'y', 'z']
    
    def __init__(self, *args):
        self.x, self.y, self.z = args
        

class Curve(object):
    """ABC for 1D geometry"""
    
    
class Surface(object):
    """ABC for 2D geometry"""
    
    
class Line(Curve):
    """A straight curve"""
    
    
class Plane(Surface):
    """A planar surface"""
    