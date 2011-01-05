import pyximport; pyximport.install()
from brep.nurbs import NurbsCurve

import unittest, math


class TestNurbsCurve(unittest.TestCase):
    def test_create(self):
        N = NurbsCurve(3, [0.25, 0.75], 
                       [(1,2,3),(2,3,4),(3,4,5),(4,5,6)],
                       [4,4])
        print N.evaluate(0.5)
        print N.get_points()
        print N.get_knots()
    
        
if __name__=="__main__":
    unittest.main()
    

