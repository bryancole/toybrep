import pyximport; pyximport.install()
from brep.nurbs import NurbsCurve

import unittest, math


class TestNurbsCurve(unittest.TestCase):
    def test_create(self):
        N = NurbsCurve(3, [0, 1], 
                       [(1,2,3),(2,3,4),(3,4,5),(4,5,6)],
                       [4,4])
        print "eval:", N.evaluate(0.9)
        print N.get_points()
        print N.get_knots()
        print "basis:"
        for i in xrange(8):
            print N.get_basis(i, 0.5)
    
        
if __name__=="__main__":
    unittest.main()
    

