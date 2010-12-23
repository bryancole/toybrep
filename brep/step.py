'''
Created on 22 Dec 2010

@author: bryan cole
'''
import re
import itertools

class STEPFileError(Exception):
    pass


class STEPDocument(object):
    pass


class EntityRef(object):
    __slots__= ['eid']
    def __init__(self, val):
        self.eid = int(val)
        
    def __repr__(self):
        return "Ref#%d"%self.eid
        
        
class Entity(object):
    __slots__ = ['name', 'args']
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __repr__(self):
        return "Entity[%s...%s]"%(self.name, str(self.args))


class STEPLoader(object):
    def __init__(self, filename):
        self.filename = filename
        
    def parse_document(self):
        with open(self.filename, 'rb') as fobj:
            f = (l for l in fobj if l) #drop blank lines
            f = self.strip_comments(f) #strip comments
            
            firstline = f.next()
            if not firstline=="ISO-10303-21;\n":
                raise STEPFileError("Not a STEP ISO 10303-21 file")
            doc = STEPDocument()
            for name, obj in self.parse_sections(iter(f.next, "END-ISO-10303-21;") ):
                setattr(doc, name, obj)
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
            
            for entity in self.parse_statements(iter(f.next, "ENDSEC;")):
                #TODO
                pass
        
#    def parse_statements(self, f):
#        assign_pat = re.compile(r"^#(\d+) *= *([_A-Z])\((.+)\);$")
#        exp_pat = re.compile(r"^(.*);\s*$")
#        for line in f:
#            m = re.match(assign_pat, line)
#            if m:
#                entity_id, entity_type, entity_args = m.groups()
#                yield self.make_assignment(int(entity_id, entity_type, entity_args))
#                continue
#            m = re.match(exp_pat, line)
#            if m:
#                exp_data=m.groups()[0]
#                yield self.make_expression(exp_data)
#                continue
            
#    def make_expression(self, exp_data):
#        subexp_pat = re.compile(r"^([_A-Z]*)\({(.+),}*\)$")
#        name_pat = re.compile(r"[_A-Z]+")
#    
#    def make_assignment(self, eid, etype, eargs):
#        pass
    
#    def parse_data(self, line_itr):
#        def char_itr():
#            for line in line_itr:
#                for char in line:
#                    yield char
#        
#        for stmt in self.parse_statements(char_itr()):
#            yield stmt
        
    def parse_statement(self, line_itr):
        line = line_itr.next().strip()
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
        if text[0]=="#":
            return EntityRef(text[1:])
        else:
            return Entity(text, args)
            
                
        
        
if __name__=="__main__":
    fname = "../step_data/two_blocks.stp"
    loader = STEPLoader(fname)
    with open(fname) as fobj:
        f = (l for l in fobj if l.strip()) #drop blank lines
        for line in loader.strip_comments(f):
            print line