import pyximport; pyximport.install()
from brep.nurbs import NurbsCurve
import unittest
import numpy


def eval_bezier(t, plist):
    """
    Evaluates a cubic bezier spline. This should be equal to
    a nurbs curve where the know multiplicities are [4,4]
    """
    out = []
    for i in xrange(len(plist[0])):
        v = (1-t)**3 * plist[0][i] +\
            3 * (1-t)**2 * t * plist[1][i] +\
            3 * (1-t) * t**2 * plist[2][i] +\
            t**3 * plist[3][i]
        out.append(v)
    return tuple(out)


class TestNurbsCurve(unittest.TestCase):
    def setUp(self):
        self.N = NurbsCurve(3, [0., 1.], 
                       [(1,2,3),(2,3,4),(3,4,5),(4,5,6)],
                       [4,4])
        
    def test_knots(self):
        self.assertEquals(self.N.get_knots(), [0.0,0.0,0.0,0.0,
                                               1.0,1.0,1.0,1.0])
        
    def test_points(self):
        pts = self.N.get_points()
        self.assertEquals(pts, [(1,2,3),(2,3,4),(3,4,5),(4,5,6)])
        
    def test_basis(self):
        u = numpy.linspace(0.0,1.0,10)
        self.assertTrue(all(sum(self.N.get_basis(3,t)) for t in u))
        
    def test_bezier(self):
        pts = self.N.get_points()
        u = numpy.linspace(0.0,1.0,10)
        A = [self.N.evaluate(t) for t in u]
        B = [eval_bezier(t, pts) for t in u]
        for a,b in zip(A,B):
            for aa,bb in zip(a,b):
                self.assertAlmostEquals(aa,bb)        
    
        
if __name__=="__main__":
    unittest.main()
    

