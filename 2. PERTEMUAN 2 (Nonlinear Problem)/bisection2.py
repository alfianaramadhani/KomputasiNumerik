import numpy as np

def fungsi(x):
    return x-np.cos(x)

def bisection(a,b,eps):
    u = fungsi(a)
    v = fungsi(b)
    i=0
    
    while (((b-a)/2)>eps) and (i<10): #berulang kalau nilai (b-a)/2 lebih dari epsilon, kalau kurang, maka akan stop iterasi
    #while (error>eps) and (i<10):    
        c=(a+b)/2
        w = fungsi(c)

        error = ((b-a)/2)

        if u*w < 0:
            b=c
            v=w
        else:
            a=c
            u=w

        i+=1

        print(i,a,b,c,error)

bisection(0.5,0.9,0.01)
