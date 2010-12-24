'''
Created on 22 Dec 2010

@author: bryan cole
'''
import re
import itertools
from collections import defaultdict, Sequence
import sys, time

class STEPFileError(Exception):
    pass


class EndOfSection(Exception):
    pass


class STEPDocument(object):
    pass


class EntityClassDict(defaultdict):
    def __missing__(self, key):
        cls = type(key, (DumbEntity,), {})
        return cls


class EntityRef(object):
    __slots__= ['eid']
    def __init__(self, val):
        self.eid = int(val)
        
    def __repr__(self):
        return "Ref#%d"%self.eid
      
      
class BaseEntity(object):
    entity_classes = EntityClassDict()
    
    def resolve(self, entity_data, referenced):
        """Evaluate a fully resolved equivalent object
        """
        if isinstance(self, ResolvedEntity):
            return self
        cls = self.entity_classes[self.name]
        def resolve(obj):
            if isinstance(obj, ResolvedEntity):
                return obj
            if isinstance(obj, (str, float, int, Star, Dollar, Const)):
                return obj
            elif isinstance(obj, Sequence):
                return type(obj)(resolve(o) for o in obj)
            elif isinstance(obj, EntityRef):
                eid = obj.eid
                referenced.add(eid)
                out = resolve(entity_data[eid])
                entity_data[eid] = out
                return out
            elif isinstance(obj, UnresolvedEntity):
                out = obj.resolve(entity_data, referenced)
                return out
            else:
                raise STEPFileError("What's a %s ?"%str(obj))
        args = [resolve(o) for o in self.args]
        inst = cls(*args)
        try:
            inst.eid = self.eid
        except AttributeError:
            #print "failed on", self
            pass
        return inst
    
    
class ResolvedEntity(BaseEntity):
    pass
    
    
class DumbEntity(ResolvedEntity):
    __slots__ = ['args','eid', 'refcount']
    def __init__(self, *args):
        self.args = args
        self.refcount = 0
        
    def __repr__(self):
        return "%s<%s>"%(self.__class__.__name__, ",".join("#%d"%o.eid if hasattr(o, "eid") else str(o) 
                                                           for o in self.args))
        
        
class UnresolvedEntity(BaseEntity):
    __slots__ = ['name', 'args', 'eid']
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __repr__(self):
        return "Entity[%s...%s]"%(self.name, str(self.args))
    
    
        
###Dunno the meaning of these two yet...
class Star(BaseEntity):
    __slots__ = []
    def __repr__(self):
        return "*"
    
class Dollar(BaseEntity):
    __slots__ = []
    def __repr__(self):
        return "$"
###
    
class Const(BaseEntity):
    __slots__ = ['name']
    def __init__(self, text):
        self.name = text.strip('.').upper()
        
    def __repr__(self):
        return self.name


class STEPLoader(object):
    def __init__(self, filename):
        self.filename = filename
        
    def parse_document(self):
        start = time.time()
        with open(self.filename, 'rb') as fobj:
            f = (l for l in fobj if l) #drop blank lines
            f = self.strip_comments(f) #strip comments
            
            firstline = f.next()
            if not firstline=="ISO-10303-21;":
                raise STEPFileError("Not a STEP ISO 10303-21 file: %s"%firstline)
            doc = STEPDocument()
            for name, obj in self.parse_sections(iter(f.next, "END-ISO-10303-21;") ):
                setattr(doc, name, obj)
        data = doc.DATA
        now = time.time()
        print "Read %d entities in %g seconds"%(len(data), now-start)
        entities = data.keys()
        referenced = set()
        def resolve(obj):
            if isinstance(obj, Sequence):
                return type(obj)(resolve(o) for o in obj)
            else:
                try:
                    return obj.resolve(data, referenced)
                except AttributeError:
                    print type(obj)
                    raise
        total = len(entities)
        for i, eid in enumerate(entities):
            if not i%10:
                print "Counted", i
            data[eid] = resolve(data[eid])
        now2 = time.time()
        print "Resolved all references in %g seconds"%(now2-now)    
        free_items = [o for k,o in ((k,data[k]) for k in data) if k not in referenced]
        doc.free_items = free_items
        print "Found free entities in %g seconds"%(time.time()-now2)
        return doc
        
    @staticmethod
    def strip_comments(line_itr):
        comment = False
        for line in line_itr:
            i = 0
            parts = []
            while True:
                if comment:
                    inew = line.find("*/", i)
                    if inew<0: 
                        break
                    comment = False
                    i = inew+2
                else:
                    inew = line.find("/*",i)
                    if inew < 0:
                        parts.append(line[i:]) 
                        break
                    else:
                        parts.append(line[i:inew])
                        i = inew+2
                        comment = True    
            out = "".join(parts).strip()
            if out:
                yield out        
                    
    def parse_sections(self, f):
        while True:
            section_name = f.next().rsplit(";",1)[0]
            assert section_name.isupper()
            if section_name == "DATA":
                yield (section_name, self.parse_data(f))
            else:
                yield (section_name, self.parse_all(f))
            
    def parse_all(self, line_itr):
        return "".join(iter(line_itr.next, "ENDSEC;"))

    def parse_data(self, line_itr):
        data = {}
        try:
            while True:
                name, expression = self.parse_statement(line_itr)
                data[name] = expression
                try:
                    expression.eid = name
                except AttributeError:
                    pass #fails on tuples
        except EndOfSection:
            return data
        
    def resolve_expression(self, data):
        pass
        
    def parse_statement(self, line_itr):
        line = line_itr.next().strip()
        if line=="ENDSEC;":
            raise EndOfSection
        i = line.find("=")
        if i < 0:
            raise STEPFileError("no assignment operator found: %s"%line)
        if line[0]!='#':
            raise STEPFileError("no reference id specified")
        EID = int(line[1:i].strip())
        
        def char_itr(line):
            while True:
                for char in line:
                    yield char
                line = line_itr.next()
        chars = char_itr(line[i+1:])
        
        expression = self.parse_expression(chars)
        return (EID, expression)
    
    def parse_expression(self, chars, term=";"):
        this=[]
        tup = None
        for char in chars:
            if char == '(':
                tup = self.parse_tuple(chars)
                continue
            if char in term:
                break
            this.append(char)
        return self.make_entity(''.join(this), tup)
    
    def parse_tuple(self, chars):
        out = []
        this = []
        for char in chars:
            if char == ')':
                out.append( self.make_entity(''.join(this), 
                                             None) )
                return tuple(out)
            if char in (',', '\n'):
                if this:
                    out.append( self.make_entity(''.join(this), 
                                                 None) 
                                )
                this=[]
                continue
            if char == '(':
                out.append(self.make_entity(''.join(this), 
                                            self.parse_tuple(chars))
                            )
                this = []
                continue
            if char == "'":
                out.append(self.parse_string(chars))
                continue
            this.append(char)
            
    def parse_string(self, chars):
        return ''.join(iter(chars.next, "'"))
                
    
    def make_entity(self, text, args):
        text = text.strip()
        if len(text)==0:
            if args is None:
                return ""
            else:
                return tuple(args)
        first = text[0]
        if first=="#":
            return EntityRef(text[1:])
        elif first.isalpha():
            return UnresolvedEntity(text, args)
        elif first==".":
            if text == ".T.":
                return True
            elif text == ".F.":
                return False
            else:
                return Const(text)
        elif first=="*":
            return Star()
        elif first=="$":
            return Dollar()
        else:
            try:
                return float(text)
            except ValueError:
                raise STEPFileError("Can't convert '%s' to a value"%text)
            
                
        
        
if __name__=="__main__":
    fname = "../step_data/two_blocks.stp"
    loader = STEPLoader(fname)
    with open(fname) as fobj:
        f = (l for l in fobj if l.strip()) #drop blank lines
        for line in loader.strip_comments(f):
            print line