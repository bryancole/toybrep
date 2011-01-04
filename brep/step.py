'''
Created on 22 Dec 2010

@author: bryan cole
'''
import re
import itertools
from collections import defaultdict, Sequence, Counter
import sys, time

import pyximport; pyximport.install()
from cstep import Star, Dollar, Const, EntityRef, resolve_doc, UnresolvedEntity
from brep.topo import BrepSolid
from brep import geom


class STEPFileError(Exception):
    pass


class EndOfSection(Exception):
    pass


class STEPDocument(object):
    @property
    def manifold_solids(self):
        #solid_reps = (o for o in self.roots if type(o).__name__=="SHAPE_REPRESENTATION_RELATIONSHIP")
        #level1 = itertools.chain.from_iterable(o.args for o in solid_reps if hasattr(o, 'args'))
        #level2 = itertools.chain.from_iterable(o.args for o in level1 if hasattr(o, 'args'))
        #level3 = itertools.chain.from_iterable( o if isinstance(o, Sequence) else (o,) for o in level2)
        #return set(s for s in level3 if isinstance(s, BrepSolid))
        return set(o for o in self.DATA.itervalues() if isinstance(o, BrepSolid))



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
        
        roots, other = resolve_doc(doc)
        doc.roots = roots
        doc.other = other
        
        now2 = time.time()
        print "Resolved all references in %g seconds"%(now2-now)    
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
                txt = ''.join(this).strip()
                if len(txt)>0:
                    out.append( self.make_entity(txt, None) )
                return tuple(out)
            if char in (',', '\n'):
                if this:
                    out.append( self.make_entity(''.join(this), 
                                                 None) 
                                )
                this=[]
                continue
            if char == '(':
                txt = ''.join(this).strip()
                out.append(self.make_entity(txt, self.parse_tuple(chars)))
                this = []
                continue
            if char == "'":
                out.append(self.parse_string(chars))
                this=[]
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
            return EntityRef(int(text[1:]))
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