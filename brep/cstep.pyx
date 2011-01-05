cdef extern from "math.h":
    double sin(double)
    double cos(double)
    double sqrt(double)
    double atan2(double, double)
    double acos(double)

from collections import defaultdict, Counter
import gc


cdef struct point:
    double x,y,z

cdef int total


cdef inline aspoint(obj):
    if isinstance(obj, CartesianPoint):
        return obj
    return CartesianPoint(obj)


def step_type(name):
    def wrapper(cls):
        entity_classes[name] = cls
        cls.step_type = name
        return cls
    return wrapper


class EntityClassDict(defaultdict):
    def __missing__(self, key):
        cls = type(key, (DumbEntity,), {})
        self[key] = cls
        return cls


entity_classes = EntityClassDict()


cdef class EntityRef(object):
    cdef public int eid
    
    def __cinit__(self, int val):
        self.eid = val
        
    def __repr__(self):
        return "Ref#%d"%self.eid
      
      
cdef class BaseEntity:
    pass
    
    
cdef class ResolvedEntity(BaseEntity):
    pass
    
    
cdef class CartesianPoint(ResolvedEntity):
#    cdef:
#        public int eid
#        public char *name
#        public double x, y, z
        
    def __cinit__(self):
        self.name = ""
        
    def __init__(self, char *name, args):
        self.name = name
        try:
            self.x, self.y, self.z = args
        except ValueError:
            raise ValueError("Can't unpack to triple: %s"%str(args))
            
    def __repr__(self):
        return "Pt< %g, %g, %g >"%(self.x, self.y, self.z)
            
    def __getitem__(self, int idx):
        if idx==0:
            return self.x
        elif idx==1:
            return self.y
        elif idx==2:
            return self.z
        else:
            raise IndexError("No index %s in CartesianPoint"%idx )
            
    def __add__(self, other):
        other = aspoint(other)
        ret = CartesianPoint.__new__(CartesianPoint)
        ret.x = self.x + other.x
        ret.y = self.y + other.y
        ret.z = self.z + other.z
        return ret
        
    def __sub__(self, other):
        other = aspoint(other)
        ret = CartesianPoint.__new__(CartesianPoint)
        ret.x = self.x - other.x
        ret.y = self.y - other.y
        ret.z = self.z - other.z
        return ret    
        
    def dot(self, other):
        other = aspoint(other)
        return self.x*other.x + self.y*other.y + self.z*other.z
        
    def cross(self, other):
        other = aspoint(other)
        ret = CartesianPoint.__new__(CartesianPoint)
        ret.x = self.y*other.z - self.z*other.y
        ret.y = other.x*self.z - other.z*self.x
        ret.z = self.x*other.y - self.y*other.x
        return ret
        
    def unit(self):
        cdef double mag
        mag = sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        ret = CartesianPoint.__new__(CartesianPoint)
        ret.x = self.x/mag
        ret.y = self.y/mag
        ret.z = self.z/mag
        return ret
        
    def mag(self):
        return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
        
            
entity_classes['CARTESIAN_POINT'] = CartesianPoint        
        

cdef class Direction(CartesianPoint):
    pass
entity_classes['DIRECTION'] = Direction
    
    
cdef class DumbEntity(ResolvedEntity):
    cdef:
        public int eid
        public tuple args
        
    def __init__(self, *args):
        self.args = args
        
    def __repr__(self):
        return "%s<%s>"%(self.__class__.__name__, ",".join(["#%d"%o.eid if hasattr(o, "eid") else str(o) 
                                                           for o in self.args]))
        
        
cdef class UnresolvedEntity(BaseEntity):
    cdef:
        public str name
        public tuple args
        public int eid
        
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __repr__(self):
        return "Entity[%s...%s]"%(self.name, str(self.args))
    
    
        
###Dunno the meaning of these two yet...
cdef class Star(ResolvedEntity):
    def __repr__(self):
        return "*"
    
cdef class Dollar(ResolvedEntity):
    def __repr__(self):
        return "$"
###
    
cdef class Const(ResolvedEntity):
    cdef public str name
    
    def __init__(self, text):
        self.name = text.strip('.').upper()
        
    def __repr__(self):
        return self.name
        
        
counter = Counter()
        

#cdef object resolve(obj, dict data):        
def resolve(obj, data, free_set=None):
    cdef int eid
    global total, entity_classes, counter
                 
    if isinstance(obj, ResolvedEntity):
        return obj
        
    if free_set is None:
        free_set = set()
        
    elif isinstance(obj, UnresolvedEntity):
        eid = obj.eid
        args = [resolve(o, data, free_set) for o in obj.args]
        
        counter[obj] += 1
        cls = entity_classes[obj.name]
        
        inst = cls.__new__(cls)
        data[eid] = inst
        
        try:
            inst.__init__(*args)
        except TypeError:
            del data[eid]
            raise TypeError("Error creating #%d = %s with args: %s"%(eid, str(cls), str(args)))
        except:
            del data[eid]
            raise
            
        inst.eid = eid
        
        if isinstance(inst, UnresolvedEntity):
            raise ValueError("this cannot be!")
        
        free_set.add(inst)
        
        total += 1
        return inst
        
    elif isinstance(obj, EntityRef):
        obj = resolve(data[obj.eid], data, free_set)
        free_set.discard(obj)
        return obj
        
    elif isinstance(obj, (tuple, list)):
        return tuple([resolve(o, data, free_set) for o in obj])
        
    else:
        return obj #must be a float, int, string etc.

def resolve_doc(step_doc):
    cdef:
        object data = step_doc.DATA
        object obj
        list entities = data.keys()
        int eid, count=0
    
    print len(entities), "entities"
    
    free_set = set()
    
    for eid in entities:
        obj = data[eid]
        resolve(obj, data, free_set)
        count += 1
        if (count % 1000) == 0:
            print "resolved: ", count, "and", total
    
    print "classes:", len(entity_classes)
    print "most common:", counter.most_common(10)
    
    root_items = set( o for o in free_set if o.eid>0 )
    rest = free_set.difference(root_items)
    
    return root_items, rest
        

    