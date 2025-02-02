# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 18:14:16 2022

@author: Eric Vidal Marcos
"""
import numpy as np
from matplotlib import pyplot as plt

#Arbitrary spin to study
s=1     #total spin
dim=(2*s+1)
Nterm1=s*(s+1)

#Hamiltonian Parameters
D=1
h=0.1
B=0.1

#CI SON LES CONSIDERADES PER LAURA PERO EN REALITAT NO SERIA MES LOGIC
#TOTES EQUIPROBS?
#Initial conditions taking into account that eigenstates are orthonormal
a_m=np.zeros((dim,1),dtype=complex)
a_m[0]=1+0j


#WE HAVE TO TAKE INTO ACCOUNT THAT M DOESNT GO FROM -S TO S
#IT GOES FROM 0 TO DIM-1=2s

#N+ and N- definition
def Np(m):
    m=m-s   #cuz m goes from 0 to 2s
    Nplus=np.sqrt(Nterm1-m*(m+1))
    return Nplus
def Nm(m):
    m=m-s   #cuz m goes from 0 to 2s
    Nminus=np.sqrt(Nterm1-m*(m-1))
    return Nminus

#PER TESTEJAR SI EL METODE ES CORRECTE, COMPARAREM AMB LAURA
#definition of ODE's
def dak1(s, k, t, am):
    '''Inputs: s (int) total spin, k (int) quantum magnetic number,
    t (int or float) time, am (array (dim,1)) coefficients of each state.
    Outputs: dak (complex) time derivative of a_k.
    This function returns each differential equation for coefficients time
    evolution.'''
    #First we define k to the scale we work in QM
    kreal=k-s
    if (kreal>s):
        print('It makes no sense that k>s or k<s, sth went wrong.')
        exit()
        
    #eigenvalues term
    eigenterm=am[k]*(-D*kreal**2-h*t*kreal)
    
    #summatory term
    sumterm=0
    for m in range(dim):
        #first we apply Kronicker deltas
        if (k==(m+2)):
            sumtermpos=Np(m)*Np(m+1)
        else:
            sumtermpos=0
            
        if (k==(m-2)):
            sumtermneg=Nm(m)*Nm(m-1)
        else:
            sumtermneg=0
            
        #and obtain summatory term along the for
        sumterm += am[m]*(B/2)*(sumtermpos+sumtermneg)
    
    dak=-1j*(eigenterm+sumterm)
    return dak

#RK4 algorithm for solve 1 step of ODE         
def RK4(s, t, am, h):
    '''Inputs: s (int) total spin, t (int or float) time, am (array (dim,1))
    coefficients of each state, h (int or float) step.
    Outputs: ak (complex array dim 2s+1) 1 step.
    This function returns every differential equation solution for coefficients
    time evolution.'''
    
    #dak1(s, k, t, am)
    for k in range(dim):
            k0 = dak1(s, k, t, am)
            k1 = dak1(s, k, t + h/2, am + h*k0/2)
            k2 = dak1(s, k, t + h/2, am + h*k1/2)
            k3 = dak1(s, k, t + h/2, am + h*k2)
            am[k] = am[k] + h*(k0 + 2*k1 + 2*k2 + k3)/6
    return am

#Evolution time frame
t0=-10
tf=10

#RK4 steps
nstep = 2000   #number
h = (tf-t0)/nstep   #step

t=t0    #Initial time

#Array to save coefficients probabilities, time, and states norm
asave=np.zeros((dim, nstep+1), dtype='float')
ti=np.zeros(nstep+1, dtype='float')
norm=np.zeros(nstep+1, dtype='float')

#CI
ti[0]=t0
for i in range(dim):
    asave[i,0]=np.abs(a_m[i])**2
    norm[0] = norm[0]+asave[i,0]


#System resolution 
for n in range(nstep):
    print(n)    #print step number (PODRIA SER UN CARGANDO)
    a_m=RK4(s, t, a_m, h)  #RK4 step
    
    #Save every value to afterwards plot evo in time, and continue RK4 
    for i in range(dim):
        asave[i,n+1]=np.abs(a_m[i])**2
        norm[n+1] = norm[n+1]+asave[i,n+1]
    
    #Input time for next step
    t=t+h
    ti[n+1]=t

plt.title('N='+str(nstep))
plt.xlabel("t")
plt.ylabel('a^2')
plt.axhline(y=1.0,linestyle='--',color='grey')
for i in range(dim):
    plt.plot(ti, asave[i,:],'-',label='m='+str(i-s))
plt.plot(ti, norm,'-',label='norma')
plt.legend()

plt.show()


