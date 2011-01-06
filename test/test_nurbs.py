import pyximport; pyximport.install()
from brep.nurbs import NurbsCurve

import unittest, math


def basis(i,n,u,k):
    '''
    Slow function for evaluating the nurbs basis functions 
    @param i: span index
    @param n: degree of curve
    @param u: parameter value
    @param k: list of knot values
    '''
    #DOESN'T WORK
    if n==0:
        return 1.0
    
    fb = basis(i,n-1,u,k)
    gb = basis(i+1,n-1,u,k)
    
    if fb==0 and gb==0:
        return 0
    
    f = (u-k[i]) / (k[i+n] - k[i])
    g = (k[i+n+1] - u) / (k[i+n+1] - k[i+1])
    
    N = f*fb + g*gb
    return N


class TestNurbsCurve(unittest.TestCase):
    def test_create(self):
        N = NurbsCurve(3, [0., 1.], 
                       [(1,2,3),(2,3,4),(3,4,5),(4,5,6)],
                       [4,4])
        print "eval:", N.evaluate(0.9)
        print N.get_points()
        print N.get_knots()
        print "basis:"
        k = [0.]*4 + [1.0]*4
        for i in xrange(8):
            print N.get_basis(i, 0.5), "...", [basis(i,p,0.5,k) for p in xrange(3)]
            
         
        
    
        
if __name__=="__main__":
    unittest.main()
    

