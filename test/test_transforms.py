import pyximport; pyximport.install()
from brep.transforms import Transform

import unittest, math


class TestTransform(unittest.TestCase):        
    def test_init(self):
        T = Transform()
        array = [[1.0,0.,0.,0.],
                 [0.,1.,0.,0.],
                 [0.,0.,1.,0.],
                 [0.,0.,0.,1.]]
        self.assertEquals(T.to_list(),array)
        
    def test_translate(self):
        T=Transform()
        T.translate(1,2,3)
        out = T.to_list()
        TT = [r[3] for r in out[:3]]
        self.assertEquals(TT, [1.,2.,3.])
        
    def test_translate2(self):
        T=Transform()
        T.translate(1,2,3)
        points = [(0,0,0),
                  (5,6,7),
                  (2.3,4.5,7.8),
                  (-2.1,5.3,-6.5)]
        out = T.transform_points(points)
        ans = [tuple(a+b for a,b in zip(r,(1,2,3))) for r in points]
        self.assertEquals(out, ans)
        
    def test_rotate_x(self):
        T=Transform()
        T.rotate_x(math.pi/2.)
        out = T.transform_points([(1,2,3)])
        self.assertEquals(out[0], (1., -3., 2.))
        
    def test_rotate_y(self):
        T=Transform()
        T.rotate_y(math.pi/2.)
        out = T.transform_points([(1,2,3)])
        self.assertAlmostEquals(out[0][0], 3.)
        self.assertAlmostEquals(out[0][1], 2.)
        self.assertAlmostEquals(out[0][2], -1.)
        
    def test_rotate_z(self):
        T=Transform()
        T.rotate_z(math.pi/2.)
        out = T.transform_points([(1,2,3)])
        self.assertAlmostEquals(out[0][0], -2.)
        self.assertAlmostEquals(out[0][1], 1.)
        self.assertAlmostEquals(out[0][2], 3.)
        
    def test_rotate_axis(self):
        T = Transform()
        T.rotate_axis((1,2,3), (7,-8,9), 1.0)
        
        pt = tuple(a+b for a,b in zip((1,2,3), (7,-8,9)))
        
        out = T.transform_points([pt])[0]
        
        self.assertAlmostEquals(out[0], pt[0])
        self.assertAlmostEquals(out[1], pt[1])
        self.assertAlmostEquals(out[2], pt[2])
        
        
if __name__=="__main__":
    unittest.main()