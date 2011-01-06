###UNTESTED###

from libc.stdlib cimport malloc, free

from cstep cimport point

from itertools import izip


cdef int find_span(int n, int p, double u, double *Uk):
    """
    n - no. of control points - 1
    p - degree
    u - parameter value
    Uk - array of knot values
    """
    cdef:
        int low,high,mid
        
    if u == Uk[n+1]:
        return n #special case
    
    low = p
    high = n+1
    mid = (low+high)//2
    
    while (u < Uk[mid]) or (u >= Uk[mid+1]):
        if (u < Uk[mid]):
            high = mid
        else:
            low = mid
        mid = (low+high)//2
        
    return mid


cdef void get_basis(int i, int p, double u, double *Nb, double *Uk):
        '''
        
        @param i: index of the span
        @param p: NURBS degree
        @param u: parameter value
        '''
        cdef:
            double *left
            double *right
            double saved, temp
            int j, r
            
        left = <double*>malloc( sizeof(double) * (p+1) )
        right = <double*>malloc( sizeof(double) * (p+1) )
            
        Nb[0] = 1.0
        for j in xrange(1,p+1):
            left[j] = u - Uk[i+1-j]
            right[j] = Uk[i+j] - u
            saved = 0.0
            for r in xrange(j):
                temp = Nb[r]/(right[r+1]+left[j-r])
                Nb[r] = saved+ (right[r+1]*temp)
                saved = left[j-r]*temp
            Nb[j] = saved
            #print "set Nb[%d] = %g"%(j, saved)

        free(left)
        free(right)
        

cdef class NurbsCurve:
    cdef:
        double *knots
        point *points
        int n_knots, n_points
        int degree
        
    def __cinit__(self, degree, list knots, list points, list multiplicities):
        cdef:
            int i, n_knots=sum(multiplicities), n_points=len(points)
            double *_knots
            point *_points #struct p.x, p.y, p.z
            point _pt
            
        assert len(multiplicities) == len(knots)
        assert sum(multiplicities) == len(points) + degree + 1
            
        self.degree = degree
        self.n_knots = n_knots
        self.n_points = n_points
        
        _knots = <double*>malloc(sizeof(double)*n_knots)
        _points = <point*>malloc(sizeof(point)*n_points)
        
        i=0
        for j,v in izip(multiplicities, knots):
            for a in xrange(j):
                _knots[i] = v
                i += 1
            
        for i, pt in enumerate(points):
            _pt.x, _pt.y, _pt.z = pt
            _points[i] = _pt
            
        self.knots = _knots
        self.points = _points
        
    def get_points(self):
        out = []
        for i in xrange(self.n_points):
            out.append((self.points[i].x, self.points[i].y, self.points[i].z))
        return out
    
    def get_knots(self):
        cdef int i
        out = []
        for i in xrange(self.n_knots):
            out.append(self.knots[i])
        return out
        
    def __dealloc__(self):
        free(self.knots)
        free(self.points)
        
    def get_basis(self, int i, double u):
        Nb = <double*>malloc(sizeof(double)*(self.degree+1))
        get_basis(i, self.degree, u, Nb, self.knots)
        out = []
        for i in xrange(self.degree+1):
            out.append(Nb[i])
        free(Nb)
        return out
        
    def evaluate(self, double u):
        cdef:
            double *Nb
            double vx = 0.0, vy=0.0, vz = 0.0
            int i, j, p=self.degree
            point pt
        
        Nb = <double*>malloc(sizeof(double)*(p+1))
        
        i = find_span(self.n_points-1, p, u, self.knots)

        get_basis(i, p, u, Nb, self.knots)
        
        for j in xrange(p+1):
            pt = self.points[i-p+j]
            #print pt.x, pt.y, pt.z, i-p+j
            vx += Nb[j]*pt.x
            vy += Nb[j]*pt.y
            vz += Nb[j]*pt.z
        
        free(Nb)
        return (vx, vy, vz)
    
