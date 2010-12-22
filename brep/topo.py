'''
Created on 21 Dec 2010

@author: bryan cole
'''

class BaseTopo(object):
    """ABC for topological structures"""


class Vertex(BaseTopo):
    """Represents a node in a Eularian solid"""
    
    
class Edge(BaseTopo):
    """intersection of two faces"""
    
    
class Loop(BaseTopo):
    """sequence of edges forming a loop"""
    
    
class Face(BaseTopo):
    """Bounded surface of a Eularian solid"""
    
    
class ModelBase(BaseTopo):
    """ABC for 'top level' topological structures"""
    
    
class Solid(ModelBase):
    """A Eularian structure enclosing a volume of space"""


class WireFrame(ModelBase):
    """a topological structure comprising only vertices and edges"""
    
    
class Sheet(ModelBase):
    """A locally manifold topological structure with zero volume""" 