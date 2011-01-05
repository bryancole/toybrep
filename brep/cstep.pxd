
cdef struct point:
    double x,y,z
    

cdef class BaseEntity:
    pass
    
    
cdef class ResolvedEntity(BaseEntity):
    pass
    
    
cdef class CartesianPoint(ResolvedEntity):
    cdef:
        public int eid
        public char *name
        public double x, y, z
        
cdef class Direction(CartesianPoint):
    pass
    