import pyximport; pyximport.install()
from brep import topo
from brep.step import STEPLoader
import unittest
import numpy
import os
from collections import Counter


def load(name, idx=0):
    f = os.path.join('..','step_data', name+'.stp')
    loader = STEPLoader(f)
    doc = loader.parse_document()
    return doc.manifold_solids.pop()


class BlockTest(unittest.TestCase):
    def setUp(self):
        self.solid = load("block")
    
    def test_edges(self):
        shell = self.solid.shell
        self.assertEquals(len(set(shell.edges())),12)
        
    def test_vertices(self):
        shell = self.solid.shell
        self.assertEquals(len(set(shell.vertices())),8)
        
    def test_faces(self):
        for face in self.solid.shell.faces:
            loop = face.bounds.pop().bound
            self.assertEquals(sum(1 for i in loop.edges()), 4)
            
    def test_loop_edges(self):
        c = Counter()
        for face in self.solid.shell.faces:
            loop = face.bounds.pop().bound
            for e,o in loop.edges():
                c[e]
        self.assertTrue(all(v==2 for v in c.values()))
        
    def test_loop_vertices(self):
        c = Counter()
        for face in self.solid.shell.faces:
            loop = face.bounds.pop().bound
            for v in loop.vertices():
                c[v]
        self.assertTrue(all(n==3 for n in c.values()))
        

class SubdividedBlockTest(unittest.TestCase):
    def setUp(self):
        self.solid = load("block")
        edges = set(self.solid.shell.edges())
        for edge in edges:
            pt = ((a+b)/2. for a,b in zip(edge.start_vertex, edge.end_vertex))
            edge.split(pt)

    def test_edges(self):
        shell = self.solid.shell
        self.assertEquals(len(set(shell.edges())),24)
        
    def test_vertices(self):
        shell = self.solid.shell
        self.assertEquals(len(set(shell.vertices())),20)
        
    def test_faces(self):
        for face in self.solid.shell.faces:
            loop = face.bounds.pop().bound
            self.assertEquals(sum(1 for i in loop.edges()), 8)
            
    def test_loop_edges(self):
        c = Counter()
        for face in self.solid.shell.faces:
            loop = face.bounds.pop().bound
            for e,o in loop.edges():
                c[e]
        self.assertTrue(all(v==2 for v in c.values()))
        
    def test_loop_vertices(self):
        c = Counter()
        for face in self.solid.shell.faces:
            loop = face.bounds.pop().bound
            for v in loop.vertices():
                c[v]
        self.assertTrue(all(n in (3,2) for n in c.values()))


if __name__=="__main__":
    unittest.main()