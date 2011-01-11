#!/usr/bin/env python
"""
General geometric intersections
"""
from brep.geom import Plane, CylindericalSurface as Cylinder, ConicalSurface as Cone,
    SphericalSurface as Sphere, ToroidalSurface as Torus

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
    
def _plane_nurbs_surf(p1, n2):
    """intersect plane and nurbs surface patch"""
    
def _cylinder_cylinder(c1, c2):
    """intersect two cylinders"""
    
def _cylinder_cone(c1, c2):
    """intersect cylinder and cone"""
    
def _cylinder_sphere(c1, s2):
    """intersect cylinder and sphere"""
    
def _cylinder_torus(c1, t2):
    """intersect cylinder and torus"""
    
def _cylinder_nurbs_surf(c1, n2):
    """intersect cylinder and nurbs surface patch"""
    
def _cone_cone(c1, c2):
    """intersect two cones"""
    
def _cone_sphere(c1, s2):
    """intersect cone and sphere"""
    
def _cone_torus(c1, t2):
    """intersection cone and torus"""
    
def _cone_nurbs_surface(c1, n2):
    """intersect cone and nurbs surface patch"""
    
def _sphere_sphere(s1, s2):
    """intersect two spheres"""
    
def _sphere_torus(s1, t2):
    """intersect sphere and torus"""
    
def _sphere_nurbs_surf(s1, n2):
    """intersect sphere and nurbs surface patch"""
    
def _torus_torus(t1, t2):
    """intersect two tori (?)"""
    
def _torus_nurbs_surf(t1, n2):
    """intersect torus and nurbs surface patch"""
    
def _nurbs_surf_nurbs_surf(n1, n2):
    """intersect two nurbs surfaces"""
    
s_s_map = {(Plane, Plane): _plane_plane,
            (Plane, Cylinder): _plane_cylinder,
            (Cylinder, Plane): _plane_cylinder}
    