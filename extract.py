#!/usr/bin/env python3
"""
Created on Mon Feb 11 21:25:53 2019

@author: sivac
"""
#The extraction process uses the marker dots injected from the inject code 
#and the image orientation is obtained from the line joining the location of the marker dots 
#The location of the marker dots in the corners are identified using template matching along the corners
#Using the alignment, the image is rotated to its correct orientation.
#Then a window array for the barcode is selected using th dots as relative postions
#The subarray flattened to mean across columns and a threshold is applied to identify black and white pixels of the barcode
# The series of black pixels are counted and divided by the fixed width of a number used in inject.py
#to obtain the unique code that was injected.
#The obtained unique code is then used to look up the answer key in the json file created while injecting
#Then the answers are saved into an output file as specified.

#Instructions to run the code
#Make sure that the key_dic.json generated while inject.py file is in the same directory as the extract.py 
#Then the answers are saved into an output file as specified.

#Importing required  libraries

import sys
import os
import numpy as np
from PIL import Image
import json
from scipy.ndimage import rotate
import math


#Check if a earlier key file exists in the location
try:    
    with open('key_dic.json', 'r') as fp:
        key_dict = json.load(fp)
except:
    sys.exit("Ouch! key dict json file not found! Check if the extract.py and key_dic.json are in the same directory")

#Generate the dot for template matching
def gen_dot(x,y,r):
    xx, yy = np.mgrid[:x, :y]    
    circle = (xx - x//2) ** 2 + (yy - y//2) ** 2    
    dot = np.logical_and(circle < (r**2), circle > 0).astype(int)
    dot[dot >1] = 0
    dot[dot <1] =255
    dot[x//2,y//2]=0
    return(dot)



#Function to match the dot in left corner
def dot_match_l(image,template):
    a,b = image.shape
    x,y = template.shape
    mat = np.inf
    X = 0
    Y = 0
    for i in range(100-x):
        for j in range(100-y):
            x_c = a -i -x//2-10
            y_c = j + y//2 + 10        
            sim = np.sum(image[x_c-10:x_c+10,y_c-10:y_c+10] - template)
            if sim < mat:
                #print(x_c,y_c,sim)
                mat = sim
                X = x_c
                Y = y_c
    return X,Y
                
#Function to match the dot in right corner           


def dot_match_r(image,template):
    a,b = image.shape
    x,y = template.shape
    mat = np.inf 
    X = 0
    Y = 0
    for i in range(100-x):
        for j in range(100-y):
            x_c = a - i -x//2 -10
            y_c = b - j - y//2 -10          
            sim = np.sum(image[x_c-10:x_c+10,y_c-10:y_c+10] - template)
            if sim < mat:
                #print(x_c,y_c,sim)
                mat = sim
                X = x_c
                Y = y_c           
              
    return X,Y
                
#Function to give the subarray from the rotated image which contans the barcode
#Rotation identified using the locations of the dot in the corners
def gen_line_index(x1,y1,x2,y2,image,dot):
    x,y = image.shape    
    xx, yy = np.mgrid[:x, :y]  
    m = (x2-x1)/(y1-y2)  
    #print(m,x1,y1,x2,y2)
    if m ==0:
#        p_line1 = yy - min(y1,y2)
#        p_line2 = yy - max(y1,y2)   
        avg_x = x1
        l_y = min(y1,y2)
        r_y = max(y1,y2)
        image_rot=image
    else:        
        angle = -1*math.degrees(math.atan(m))
        image_rot = rotate(image,angle,mode='constant',cval=255)
        l_x,l_y = dot_match_l(image_rot,dot)             
        r_x,r_y = dot_match_r(image_rot,dot)
        ##print(l_x,l_y,r_x,r_y, angle)
        ##Image.fromarray(image_rot).show()
        avg_x = (l_x +r_x)//2
#        m = (r_x-l_x)/(l_y-r_y)        
#        c = l_x - m*l_y
#        line = xx -m*yy - c
#        m2 = -1/m
#        c1 = l_x - m2*l_y
#        c2 = r_x - m2*r_y
#        p_line1 = xx -m2*yy - c1
#        p_line2 = xx -m2*yy - c2  
#        line_bool = ((line < 8) & (line > -8)  & (p_line1 <0) & (p_line2 >0)).astype(int)
##
#        a = []
#        for i in range(-10,10,1):            
#            line_bool = ((line==i)  & (p_line1 < 0) & (p_line2 > 0)).astype(int)
#            print(linebool.sum)
#            a.append(image[line_bool==1])
    #index = np.argwhere(line_bool==1)
    #line_bool[index[:,0].min():index[:,0].max()+1,index[:,1].min():index[:,1].max()+1] = 1
    #return image[line_bool==1].reshape(21,1700).reshape(21,r_y-l_y-1)
    return image_rot[avg_x-20:avg_x+20,l_y:r_y]
    #return image[line_bool==1].reshape(index[:,0].max()-index[:,0].min()+1,index[:,1].max()-index[:,1].min()+1)
    #return image_rot,l_x,l_y,r_x,r_y,m,angle
    #return image[line_bool==1]#.reshape(21,1700)

#im,x1,y1,x2,y2,m,angle=gen_line_index(l_x,l_y,r_x,r_y,image,dot)
#
#Image.fromarray(image).show()
#Image.fromarray(im).show()


#Decode the barcode from the subarray returned from the above function
#Applying  a threshhold on the mean of the subarray to find the barcode
#Count the sequence of 0's and divide the sequnce by the width of 15 to get the unique code    
def scanner(subarray):
    x,y=subarray.shape
    subarray = subarray[:,200:y-200]
    c = subarray.all(axis=1) 
    subarray = subarray[ ~c,:]    
    rd = subarray.mean(axis=0)
    rd[rd>=100] = 255
    rd[rd<100] = 0
    
    a = []
    j = 0
    for i in range(len(rd)):
        if rd[i] == 0:            
            j += 1
        elif rd[i] >0:
            if j >0:
              a.append(int(np.ceil(j/15)))
            j = 0
    return int(''.join(map(str,a)))
    #return subarray

#Taking the inputs from the user
injected,output = sys.argv[1],sys.argv[2]
#convert the image to grayscale and numpy array
image = np.asarray(Image.open(injected).convert('L'))
#generate dot for template matching
dot = gen_dot(20,20,8)
#Find the coordinates of left dot
l_x,l_y = dot_match_l(image,dot)
#Find the coordinates of right dot             
r_x,r_y = dot_match_r(image,dot)
#Find the subarray containing the bar code
subarray = gen_line_index(l_x,l_y,r_x,r_y,image,dot)
#Extract the key from the barcode
key  = scanner(subarray)
#print(key)
#Write the output from the dictionary using th key extracted to a text file
with open(output, 'w') as f:
    f.write("\n".join(key_dict[str(key)]))


