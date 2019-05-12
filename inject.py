#!/usr/bin/env python3
"""
Created on Mon Feb 11 17:39:37 2019

@author: sivac
"""
#Injected code takes the image onto which the answers need to be injected and the answer from 
#the text file and creates a unique key everytime the code is run. The key is used to store
#the answers in a dictionary. For extraction purpose the dictionary is then dumped into
#a json file in the current directory of inject.py. Further using the unique key a barcode is genertaed in
#the form of a box and then injected into the bottom of the image. Also, the marker dots
#are injected in the same line as the barcode.
#The marker dots are injected to identify the barcode location and orientation in the extraction process.
#Then the injected image is saved with the user 
#defined name.


#Importing required libraries
import sys
import os
import random
import numpy as np
from PIL import Image
import json


#Check if a earlier key file exists in the location
try:    
    with open('key_dic.json', 'r') as fp:
        data = json.load(fp)
        print(data)
except:
    data = {}
        
#Generating and storing a unique key everytme inject.py is run and using it as the 
#key for the answers
def store_keys(answers,key_dict):    
    options = [line.rstrip('\n') for line in open(answers)]
    #Generate random key
    key = int(''.join(random.choices([str(x) for x in range(1,10,1)],k=3)))
    if key not in key_dict.keys():
        key_dict[key] = options
        return key_dict, key
    else:
        store_keys(answers,key_dict)
        
#Generate the barcode based on the unique code:        
def genbox(num):
    if num in range(111,999):
        i,j,k=int(str(num)[0]),int(str(num)[1]),int(str(num)[2])
    
    if (i > 0) and (j>0) and (k>0):
        box = np.array([255]*20*500).reshape(20,500)
        _,m=box.shape
        w = 15
        g = 10
        #first digit
        box[:,0 : w*i] = 0
        box[:,(w*i)+ g : w*(i+j)+ g ] = 0
        box[:,w*(i+j)+ (2*g) : w*(i+j+k) + (2*g)] = 0
        #box[:,w*(i+j+k)+ (3*g) : m  ] = 0
        return box
    else:
        return None
    
#Generate the marker dot for the template matching
#https://stackoverflow.com/questions/10031580/how-to-write-simple-geometric-shapes-into-numpy-arrays
def gen_dot(x,y,r):
    xx, yy = np.mgrid[:x, :y]    
    circle = (xx - x//2) ** 2 + (yy - y//2) ** 2    
    dot = np.logical_and(circle < (r**2), circle > 0).astype(int)
    dot[dot >1] = 0
    dot[dot <1] =255
    dot[x//2,y//2]=0
    return(dot)

      
#Input
form, answers,output = sys.argv[1],sys.argv[2],sys.argv[3]

#Store and generate keys
key_dict,key_code=store_keys(answers,data)

#Generate the box
box = genbox(key_code)

#Generate marker dot
dot = gen_dot(20,20,8)

#Import Original form
im = np.asarray(Image.open(form).convert('L'))
im.setflags(write=1)

#Inject the box at the end of the original image
a,b = im.shape
c,d = dot.shape
x,y = box.shape
im[a-50-c//2:a-50+c//2, (b//2)-30-(y//2):(b//2)+(y//2)-30] = box
#im[a-c:a,0:d] = dot
#im[a-c:a,b-d:b] = dot
im[a-50-c//2:a-50+c//2,50-d//2:d//2+50] = dot
im[a-50-c//2:a-50+c//2,b-50-d//2:b-50+d//2] = dot
Image.fromarray(im).show()
Image.fromarray(im).save(output)


#Save the keydict to a json file with the answer keys into the current directory
with open('key_dic.json', 'w') as fp:
    json.dump(key_dict, fp)
       
            
