import pyximport; pyximport.install()
from brep import intersections as it
from brep import geom
import unittest


class PointTests(unittest.TestCase):
    def test_point_point(self):
        p1 = geom.CartesianPoint("",(1.,2.,3.))
        p2 = geom.CartesianPoint("",(1.,2. + it.TOLGEO/2,3.))
        p3 = geom.CartesianPoint("", (1.1,2,3))
        
        self.assertIsNone(it.intersect(p1,p3))
        self.assertTrue(it.intersect(p1,p2) is not None) 
        
if __name__=="__main__":
    unittest.main()
    