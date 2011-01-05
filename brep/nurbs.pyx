###UNTESTED###

from stdlib cimport malloc, free


cdef class NurbsCurve:
    cdef:
        double *knots, *points, *multiplicities
        int n_knots, n_points
        int degree
        
    def __cinit__(self, degree, list knots, list points, list multiplicities):
        cdef:
            int i, n_knots=len(knots), n_points=len(points)
            double *_knots
            int *_multiplicities
            point *_points #struct p.x, p.y, p.z
            point pt, _pt
            
        self.n_knots = n_knots
        self.n_points = n_points
        
        _knots = malloc(sizeof(double)*n_knots)
        _multiplicities = malloc(sizeof(int)*n_knots)
        _points = malloc(sizeof(point)*n_points)
        
        for i in xrange(n_knots):
            _knots[i] = knots[i]
            _mulitplicities[i] = multiplicities[i]
            
        for i in xrange(n_points):
            pt = <point>points[i]
            _pt = _points[i]
            _pt.x = pt.x
            _pt.y = pt.y
            _pt.z = pt.z
            
        self.knots = _knots
        self.multiplicities = _multiplicities
        self.points = _points
        
    def __dealloc__(self):
        free(self.knots)
        free(self.points)
        free(self.multiplicities)