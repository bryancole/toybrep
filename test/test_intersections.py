import pyximport; pyximport.install()
from brep import intersections as it
from brep import geom
import unittest
from functools import partial

Pt=lambda *x: geom.CartesianPoint("", x)
Dr=lambda *x: geom.Direction("", x)


class PointTests(unittest.TestCase):
    def test_point_point(self):
        p1 = geom.CartesianPoint("",(1.,2.,3.))
        p2 = geom.CartesianPoint("",(1.,2. + it.TOLGEO/2,3.))
        p3 = geom.CartesianPoint("", (1.1,2,3))
        self.assertIsNone(it.intersect(p1,p3))
        self.assertTrue(it.intersect(p1,p2) is not None) 
        
    def test_line_line(self):
        l1 = geom.Line("", Pt(0,0,0), Dr(1,1,0))
        l2 = geom.Line("", Pt(2,0,0), Dr(-1,1,0))
        l3 = geom.Line("", Pt(2,0,1), Dr(-1,1,0))
        self.assertTrue(it.intersect(l1, l2) is not None)
        self.assertAlmostEquals((it.intersect(l1, l2) - Pt(1,1,0)).mag(), 0.0, delta=it.TOLGEO)
        self.assertIsNone(it.intersect(l1, l3))
        self.assertIsNone(it.intersect(l2, l3))
        self.assertAlmostEquals((it.intersect(l1, l1).origin - l1.origin).mag(), 0.0, delta=it.TOLGEO)
        self.assertAlmostEquals((it.intersect(l1, l1).vector - l1.vector).mag(), 0.0, delta=it.TOLGEO)
        
if __name__=="__main__":
    unittest.main()
    