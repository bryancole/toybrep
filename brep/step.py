'''
Created on 22 Dec 2010

@author: bryan cole
'''


class STEPFileError(Exception):
    pass


class STEPDocument(object):
    pass


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
            for name, obj in self.parse_section(f):
                setattr(doc, name, obj)
            lastline = f.next()
            if not lastline.strip()=="END-ISO-10303-21;":
                raise STEPFileError("Incorrectly formed STEP file")
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
                
                    
        
    def parse_section(self, f):
        while True:
            section_name = f.next().rsplit(";",1)[0]
            assert section_name.isupper()
            
            for entity in self.parse_statement(f):
                #TODO
                pass
        
        


if __name__=="__main__":
    fname = "../step_data/two_blocks.stp"
    loader = STEPLoader(fname)
    with open(fname) as fobj:
        f = (l for l in fobj if l.strip()) #drop blank lines
        for line in loader.strip_comments(f):
            print line