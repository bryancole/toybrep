import pyximport; pyximport.install()
from brep.nurbs import NurbsCurve

import unittest, math


def alpha(i,j,u,s):
    try:
        if s[i]==s[i+j]:
            return 0.0
        else:
            return (u-s[i]) / (s[i+j] - s[i])
    except IndexError:
        return 0.0
    

def basis(i,n,u,k):
    '''
    Slow function for evaluating the nurbs basis functions 
    @param i: span index
    @param n: degree of curve
    @param u: parameter value
    @param k: list of knot values
    '''
    if n==0:
        return 1.0 if k[i] <= u < k[i+1] else 0.0
    
    N = alpha(i,n,u,k)*basis(i,n-1,u,k) + \
        (1 - alpha(i+1,n,u,k))*basis(i+1,n-1,u,k)
    
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
        #for i in xrange(0,8):
        #    print N.get_basis(i, 0.5), "...", [basis(i,p,0.5,k) for p in xrange(4)]
            
         
        
    
        
if __name__=="__main__":
    unittest.main()
    

