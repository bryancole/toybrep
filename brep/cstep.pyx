

from collections import defaultdict
import gc

cdef int total


class EntityClassDict(defaultdict):
    def __missing__(self, key):
        cls = type(key, (DumbEntity,), {})
        self[key] = cls
        return cls


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
    
    
cdef class DumbEntity(ResolvedEntity):
    cdef:
        public int eid
        public tuple args
        
    def __cinit__(self, *args):
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
        
        
entity_classes = EntityClassDict()
        
        
Placeholder = ResolvedEntity()

        
cdef object resolve(obj, dict data):
    cdef int eid
    global total, entity_classes
                 
    if isinstance(obj, ResolvedEntity):
        return obj
        
    elif isinstance(obj, UnresolvedEntity):
        eid = obj.eid
        #data[eid] = Placeholder
        args = [resolve(o, data) for o in obj.args]
        
        cls = entity_classes[obj.name]
        inst = cls(*args)
        
        data[eid] = inst
        total += 1
        return inst
        
    elif isinstance(obj, EntityRef):
        return resolve(data[obj.eid], data)
        
    elif isinstance(obj, (tuple, list)):
        return tuple([resolve(o, data) for o in obj])
        
    else:
        return obj #must be a float, int, string etc.

def resolve_doc(step_doc):
    cdef:
        object data = step_doc.DATA
        object obj
        list entities = data.keys()
        int eid, count=0
    
    print len(entities), "entities"
    
    for eid in entities:
        obj = data[eid]
        resolve(obj, data)
        count += 1
        if (count % 1000) == 0:
            print "resolved: ", count, "and", total
    
    print "classes:", len(entity_classes)
    