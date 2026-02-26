def fungsi(x):
    return x**3-3*x+1

def bisection(a,b,eps):
    u = fungsi(a)
    v = fungsi(b)
    i=0

    while ((b-a)/2)>eps: #berulang kalau nilai (b-a)/2 lebih dari epsilon, kalau kurang, maka akan stop iterasi
        c=(a+b)/2
        w = fungsi(c)

        if u*w < 0:
            b=c
            v=w
        else:
            a=c
            u=w
        print(a,b)

bisection(0,1,0.001)

#cek fungsi apakah bisa untuk bisection: jika kedua fungsi berbeda tandanya, maka bisa digunakan untuk bisection
#print (fungsi(1)) 
#print (fungsi(2))


