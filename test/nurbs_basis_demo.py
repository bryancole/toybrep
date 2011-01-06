import unittest, math


def alpha(i,j,u,s):
    #try:
    if u==s[-1]:
        return 1.0
    
    if s[i]==s[i+j]:
        return 0.0
    else:
        return (u-s[i]) / (s[i+j] - s[i])
    #except IndexError:
    #    return 0.0
    

def basis(i,n,u,k):
    '''
    Slow function for evaluating the nurbs basis functions 
    @param i: span index
    @param n: degree of curve
    @param u: parameter value
    @param k: list of knot values
    '''
    if n==0:
        return 1.0 if k[i] <= u <= k[i+1] else 0.0
    
    N = alpha(i,n,u,k)*basis(i,n-1,u,k) + \
        (1 - alpha(i+1,n,u,k))*basis(i+1,n-1,u,k)
    
    return N


import sys
print sys.version_info

from matplotlib import pyplot as pp
import numpy as np

T = np.linspace(0.,1., 100)
k = [0.0,0.0,0.0,0.0,1.0,1.0,1.0,1.0]
#k = [0.0]*3 + list(np.linspace(0.0,1.0,2)) + [1.0]*3
points = [(-1.5,0),(-1,1),(1,1),(1.5,0)]

X = []
Y = []
for t in T:
    x = sum(p[0]*basis(i,3,t,k) for i,p in enumerate(points))
    y = sum(p[1]*basis(i,3,t,k) for i,p in enumerate(points))
    X.append(x)
    Y.append(y)
    
pp.plot(X,Y, 'b-')
pp.plot([p[0] for p in points], [p[1] for p in points], 'o-r')
pp.show()
    
print [basis(i+1,3,1.0,k) for i in range(4)]