import pyximport; pyximport.install()
from brep.cstep import CartesianPoint

import unittest, math


class TestCartesianPoint(unittest.TestCase):
    def test_index(self):
        p1 = CartesianPoint('', (1,2,3))
        self.assertEquals(tuple(p1),(1.,2.,3.))
        
    def test_add(self):
        p1 = CartesianPoint('', (1,2,3))
        p2 = CartesianPoint("", (4,5,6))
        p3 = p1 + p2
        self.assertEquals(tuple(p3), (5,7,9))
        
    def test_sub(self):
        p1 = CartesianPoint('', (1,2,3))
        p2 = CartesianPoint("", (4,5,6))
        p3 = p1 - p2
        print p3.name
        self.assertEquals(tuple(p3), (-3,-3,-3))
        

if __name__=="__main__":
    unittest.main()