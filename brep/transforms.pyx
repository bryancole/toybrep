cdef extern from "math.h":
    double sin(double)
    double cos(double)
    double sqrt(double)
    double atan2(double, double)


cdef struct point:
    double x,y,z


cdef class Transform:
    cdef:
        double m00, m11, m22
        double m01, m02, m03
        double m10, m12, m13
        double m20, m21, m23
        
    def __cinit__(self):
        self.m00 = self.m11 = self.m22 = 1.0
        
    def copy(self):
        c = Transform()
        c.m00 = self.m00
        c.m01 = self.m01
        c.m02 = self.m02
        c.m03 = self.m03
        c.m10 = self.m10
        c.m11 = self.m11
        c.m12 = self.m12
        c.m13 = self.m13
        c.m20 = self.m20
        c.m21 = self.m21
        c.m22 = self.m22
        c.m23 = self.m23
        return c
        
    def identity(self):
        self.m00 = self.m11 = self.m22 = 1
        self.m01 = self.m02 = self.m03 = 0
        self.m10 = self.m12 = self.m13 = 0
        self.m20 = self.m21 = self.m23 = 0
        
    def to_list(self):
        return [[self.m00, self.m01, self.m02, self.m03],
                [self.m10, self.m11, self.m12, self.m13],
                [self.m20, self.m21, self.m22, self.m23],
                [0.0,0.0,0.0,1.0]]
                
    cdef point _transform_point(self, point p):
        cdef point P
        P.x = self.m00*p.x + self.m01*p.y + self.m02*p.z + self.m03
        P.y = self.m10*p.x + self.m11*p.y + self.m12*p.z + self.m13
        P.z = self.m20*p.x + self.m21*p.y + self.m22*p.z + self.m23
        return P
                
    def transform_points(self, list points):
        cdef:
            point p
            list out=[]
        
        for pt in points:
            p.x,p.y,p.z = pt
            p = self._transform_point(p)
            out.append((p.x, p.y, p.z))
        return out
        
    cdef _translate(self, double x, double y, double z):
        self.m03 += x
        self.m13 += y
        self.m23 += z
        
    def translate(self, x, y, z):
        self._translate(x,y,z)
        
    cdef void _rotate_x(self, double angle):
        cdef: 
            double c=cos(angle),s=sin(angle) 
            double m10=self.m10, m11=self.m11, m12=self.m12
            double m13=self.m13, m20=self.m20, m21=self.m21, m22=self.m22
            double m23=self.m23 
        
        self.m10 = c*m10 - s*m20
        self.m11 = c*m11 - s*m21
        self.m12 = c*m12 - s*m22
        self.m13 = c*m13 - s*m23
        
        self.m20 = s*m10 + c*m20
        self.m21 = s*m11 + c*m21
        self.m22 = s*m12 + c*m22
        self.m23 = s*m13 + c*m23
        
    def rotate_x(self, angle):
        self._rotate_x(angle)
    
    cdef void _rotate_y(self, double angle):
        cdef: 
            double c=cos(angle),s=sin(angle) 
            double m00=self.m00, m01=self.m01, m02=self.m02, m03=self.m03
            double m20=self.m20, m21=self.m21, m22=self.m22, m23=self.m23
            
        self.m00 = c*m00 + s*m20
        self.m01 = c*m01 + s*m21
        self.m02 = c*m02 + s*m22
        self.m03 = c*m03 + s*m23 
        self.m20 = -s*m00 + c*m20
        self.m21 = -s*m01 + c*m21
        self.m22 = -s*m02 + c*m22
        self.m23 = -s*m03 + c*m23
        
    def rotate_y(self, angle):
        self._rotate_y(angle)
        
    cdef void _rotate_z(self, double angle):
        cdef: 
            double c=cos(angle),s=sin(angle) 
            double m00=self.m00, m01=self.m01, m02=self.m02, m03=self.m03
            double m10=self.m10, m11=self.m11, m12=self.m12, m13=self.m13
            
        self.m00 = c*m00 - s*m10
        self.m01 = c*m01 - s*m11
        self.m02 = c*m02 - s*m12
        self.m03 = c*m03 - s*m13 
        self.m10 = s*m00 + c*m10
        self.m11 = s*m01 + c*m11
        self.m12 = s*m02 + c*m12
        self.m13 = s*m03 + c*m13
        
    def rotate_z(self, angle):
        self._rotate_z(angle)
        
    def rotate_axis(self, o, d, angle):
        """
        Rotate about an axis specified by origin and direction
        o - origin
        d - direction
        angle - amount of rotation, in radians
        """
        theta = atan2(d[1], d[0])
        r = sqrt(d[0]**2 + d[1]**2)
        phi = atan2(r, d[2])
        
        self._translate(-o[0], -o[1], -o[2])
        self._rotate_z(-theta)
        self._rotate_y(-phi)
        self._rotate_z(angle)
        self._rotate_y(phi)
        self._rotate_z(theta)
        self._translate(o[0], o[1], o[2])