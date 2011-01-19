#!/usr/bin/env python
"""
General geometric intersections
"""
from brep.geom import (Plane as plane, CylindericalSurface as cylinder, ConicalSurface as cone,
    SphericalSurface as sphere, ToroidalSurface as torus, CartesianPoint as point, Line as line, Circle as circle,
    NurbsCurve as nurbscurve)


TOLEPS = 1e-12 #length tolerance
TOLANG = 1e-9 #angular tolerance
TOLGEO = 1e-12 #geometric tolerance for intersections
TOLREL = 1e-10 #relative tolerance
TOLPOL = 1e-6 #polynomial tolerance

def _point_point(p1, p2):
    """intersect two points"""
    if (p2-p1).mag() < TOLGEO:
        return (p2 + p1)/2.
    else:
        return None
    
def _point_line(p1, l2):
    """intersect point and line"""
    dist = l2.vector.cross(l2.origin-p1).mag() / l2.vector.mag()
    if dist < TOLGEO:
        return p1
    else:
        return None
    
def _point_circle(p1, c2):
    """intersect point and circle"""
    
def _point_nurbscurve(p1, n2):
    """intersect point and nurbs curve"""
    
def _line_line(l1, l2):
    """intersection of two lines"""
    #check coplanar...
    a = l1.vector
    b = l2.vector
    c = l2.origin - l1.origin
    ab = a.cross(b)
    cp = c.dot(ab)
    if cp >= TOLGEO:
        return None
    m = ab.mag_sq()
    if m < TOLGEO:
        if c.mag_sq() < TOLGEO:
            return l1 #lines are colinear
        else:
            return None #lines are parallel but not colinear
    s = c.cross(b).dot(ab) / m
    intersection = l1.origin + l1.vector*s
    return intersection
    
def _line_circle(l1, c2):
    """intersect line and circle"""
    
def _line_nurbscurve(l1, n2):
    """intersect line and nurbs curve"""
    
def _circle_nurbscurve(c1, n2):
    """intersect circle and nurbs curve"""
    
def _circle_circle(c1, c2):
    """intersection of two circles"""
    
def _nurbscurve_nurbscurve(n1, n2):
    """intersection of two nurbs curves"""
    
def _point_plane(p1, p2):
    """intersect point with a plane"""
    
def _line_plane(l1, p2):
    """intersect line with plane"""
    
def _circle_plane(c1, p2):
    """intersect circle and plane"""
    
def _nurbscurve_plane(n1, p2):
    """intersect nurbs curve with plane"""
    
def _point_cylinder(p1,c2):
    """intersect point with cylinder"""
    
def _line_cylinder(l1, c2):
    """intersect line with cylinder"""
    
def _circle_cylinder(c1, c2):
    """intersect circle with cylinder"""
    
def _nurbscurve_cylinder(n1, c2):
    """intersect nurbs curve with cylinder"""
    
def _point_cone(p1,c2):
    """intersect point with cone"""
    
def _line_cone(l1, c2):
    """intersect line with cone"""
    
def _circle_cone(c1, c2):
    """intersect circle with cone"""
    
def _nurbscurve_cone(n1, c2):
    """intersect nurbs curve with cone"""
    
def _point_torus(p1,c2):
    """intersect point with torus"""
    
def _line_torus(l1, c2):
    """intersect line with torus"""
    
def _circle_torus(c1, c2):
    """intersect circle with torus"""
    
def _nurbscurve_torus(n1, c2):
    """intersect nurbs curve with torus"""

def _plane_plane(p1, p2):
    """intersect two planes"""
    
def _plane_cylinder(p1, c2):
    """intersect plane and cylinder"""
    
def _plane_cone(p1, c2):
    """intersect plane and cone"""
    
def _plane_sphere(p1, s2):
    """intersect plane and sphere"""
    
def _plane_torus(p1, t2):
    """intersect plane and torus"""
    
def _plane_nurbssurf(p1, n2):
    """intersect plane and nurbs surface patch"""
    
def _cylinder_cylinder(c1, c2):
    """intersect two cylinders"""
    
def _cylinder_cone(c1, c2):
    """intersect cylinder and cone"""
    
def _cylinder_sphere(c1, s2):
    """intersect cylinder and sphere"""
    
def _cylinder_torus(c1, t2):
    """intersect cylinder and torus"""
    
def _cylinder_nurbssurf(c1, n2):
    """intersect cylinder and nurbs surface patch"""
    
def _cone_cone(c1, c2):
    """intersect two cones"""
    
def _cone_sphere(c1, s2):
    """intersect cone and sphere"""
    
def _cone_torus(c1, t2):
    """intersection cone and torus"""
    
def _cone_nurbssurf(c1, n2):
    """intersect cone and nurbs surface patch"""
    
def _sphere_sphere(s1, s2):
    """intersect two spheres"""
    
def _sphere_torus(s1, t2):
    """intersect sphere and torus"""
    
def _sphere_nurbssurf(s1, n2):
    """intersect sphere and nurbs surface patch"""
    
def _torus_torus(t1, t2):
    """intersect two tori (?)"""
    
def _torus_nurbssurf(t1, n2):
    """intersect torus and nurbs surface patch"""
    
def _nurbssurf_nurbssurf(n1, n2):
    """intersect two nurbs surfaces"""

surfaces = ['plane',
            'cone',
            #'sphere',
            'torus',
            'cylinder', 
            #'nurbssurf', 
            'line', 
            'circle', 
            'point', 
            #'ellipse', 
            'nurbscurve', 
            #'parabola',
            #'hyperbola'
            ]

pairs = ((a,b) for a in surfaces for b in surfaces)
g = globals()
ss_map = {}
for n1,n2 in pairs:
    s1, s2 = g[n1], g[n2]
    fname = "_%s_%s"%(n1, n2)
    if fname not in g:
        fname = "_%s_%s"%(n2, n1)
        reverse = True
    else:
        reverse = False
    ss_map[(s1,s2)] = (g[fname], reverse)
    
def intersect(s1, s2):
    try:
        func, reverse = ss_map[(type(s1), type(s2))]
    except KeyError:
        raise ValueError("either arguments %s and %s are not recognised surface types"%(s1, s2))
    args = (s2,s1) if reverse else (s1, s2)
    return func(*args)


    