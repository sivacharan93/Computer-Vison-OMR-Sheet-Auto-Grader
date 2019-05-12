#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 20:28:19 2019

@author: Adithya
"""

#Importing required packages

#import cv2
import numpy as np
from PIL import Image
import os, sys
import time
from collections import Counter


#Function to read a pre defined template, this template was contructed by looking at the blank answer sheet given
def reading_template():
    with open("basic_template.txt") as fp:
        data = fp.readlines()
    fil_data = []
    for i in data:
        d = [float(j) for j in i.strip().split("\t")]
        fil_data.append(d)
        
    filte = np.array(fil_data, dtype = float)
    return filte

#Function to convert given grey image with pixels ranging from 0 to 255 to binary pixels (0,1)
#All pixles values from original image if less than 127 replaced with 0 and if greater than 127 repaced with 1
def rescale_pixels(normal_image):
#    return (normal_image > 127).astype(float)
#    """
    rescale_image = np.array(normal_image)
    for i in range(len(normal_image)):
        for j in range(len(normal_image[i])):
            rescale_image[i,j] = 0 if normal_image[i,j] < 127 else 1
    return rescale_image
#    """


#Below function were created for using in template matching, but as we are using 
# numpy arrays with just 0 and 1 as pixels values we used inbuilt numpy function to
# caluclate the similarity between a image portion and template, so these functions are not being used now
"""
def pixel_match(actual_image_section, template):        
    count = 0        
    for i in range(len(template)):
        if 2 <= i < len(template)-2:
            for j in [0,1,len(template[i])-2,len(template[i])-1]:
                if actual_image_section[i,j] == template[i,j]:
                    count += 1
        else:
            for j in range(len(template[i])):
                if actual_image_section[i,j] == template[i,j]:
                    count += 1
    return count

def one_vector_similarity(x,y):
    count = 0
    count = sum([1 for i in range(len(x)) if x[i] == y[i]])
    return count
"""

#Function to do the template maching (seeing the number of same pixels, in template edge and in actual image by different locations)

def finding_patterns(actual_image, template):
#defining max_count to select few positions in actual images to consider by comapring the template maching score to max_count
    max_count = 0
#defining two dictionaries to store and return all location based matching score and favarable location matching score
    d = {}
    f = {}
#looping over all pixel values of the input image
    for i in range(0,len(actual_image) - len(template)):
        for j in range(0,len(actual_image[0]) - len(template[0])):
            try:
#                print (i,j)
#caluclating the no: zeros(as template and image has binary pixels values and edges being dark will have zero) 
# on each row and coloumn for the edge. As the template edge has two pixel array,
#we are considering two upper rows, two bottom rows and two left columns and two right columns
                r1 = np.count_nonzero(actual_image[i][j:j+len(template[0])] == 0)
#                print (r1)
                r2 = np.count_nonzero(actual_image[i+1][j:j+len(template[0])] == 0)
#                print (r2)
                r3 = np.count_nonzero(actual_image[i+len(template[:,0])-1][j:j+len(template[0])] == 0)
#                print (r3)
                r4 = np.count_nonzero(actual_image[i+len(template[:,0]) -2][j:j+len(template[0])] == 0)
#                print (r4)
                c1 = np.count_nonzero(actual_image[:,j][i:i+len(template)][2:-2] == 0)
#                print (c1)
                c2 = np.count_nonzero(actual_image[:,j+1][i:i+len(template)][2:-2] == 0)
#                print (c2)
                c3 = np.count_nonzero(actual_image[:,j+len(template[0])-1][i:i+len(template)][2:-2] == 0)
#                print (c3)
                c4 = np.count_nonzero(actual_image[:,j+len(template[0])-2][i:i+len(template)][2:-2] == 0)
#                print (c4)

#The overall matching score is sum of all the zeros in the edges of the selected position
                d[i,j] = r1+r2+r3+r4+c1+c2+c3+c4

#updating max_count
                if d[i,j] > max_count:
                    max_count = d[i,j]

            except Exception as e:
                print (str(e))
                print (i,j)
#                print (d)
                sys.exit()

#adding location to favorable dictionary only is match score in greater than 70% of the max_count
            if d[i,j] > max_count * .7: #268/2
                f[i,j] = d[i,j]
                
    return d, f, max_count


#Function to give good horizontal and vertical cordinates, based on the number of times these cordinates were present in the vavorable dictionary
#As most of the boxes are parallel to each other, these helps us in removing not so good cordinates
def finding_keys(d, max_count):
#taking horizontal and vertical cordinates counts, if theor respective template matching score is within 70% of the max_count
    count_x = Counter(k[0] for k in d if d[k] > max_count * .7)
    count_y = Counter(k[1] for k in d if d[k] > max_count * .7)

#getting those horizontal cordinates, which appear atleast 8 times in the counter
    count_xx = {}
    for k in count_x:
        if count_x[k] > 8:
            count_xx[k] = count_x[k]
#Similarly slecting y cordinates
    count_yy = {}
    for k in count_y:
        if count_y[k] > 12:
            count_yy[k] = count_y[k]

    return dict(count_xx), dict(count_yy)

"""
def finding_location(d, x, y):
    di = {}
    for k in d:
        if k[0] in x and k[1] in y:
#            if x[k[0]] > 3
            di[k] = d[k]
    return di
"""

#Function to give average intensity of the region in actual image given its starting horzontal and vertical cordinate and the template used so far
#the required region will be inside of the template, therefore template structure is used here
def intensity(x,y,actual_image, template):
    required_portion = actual_image[x+2:len(template)+x-4,y+2:len(template[0])+y-4]
#returning mean intensity of the required region
    return np.mean(required_portion)

#Function to change the intensity of a region in actual image given its starting horzontal and vertical cordinate and the template used so far
#this function is used in giving output image with some mark on it, with specifies the region detected by the model
def intensity_changer(x, y, inter_image, template):
#reducing the soxe of the region to be changed to add a small box
    xx = len(template)-15
    yy = len(template[0]) - 15
#    arr = np.ones((x+2:len(template)+x-4,y+2:len(template[0])+y-4), dtype = float)
    arr = np.full((xx,yy), 200, dtype = float)
    inter_image[x+7:len(template)+x-8,y+7:len(template[0])+y-8] = arr
#    return inter_image


#function to modify the current set of axis(coordinates) a little by moving axis slightly down or right
#this is mostly done by cross checking the output and rectifying it
def box_finder(x_dict, y_dict):
    l = []
#only considering the horizontal axis below 600 pixel as all the answer boxes start after 600 pixels horizontally
#similarly vertical cordinates after 200 were considered
    x_min = 600
#    y_min = 200
#sorting the list, this will help in modofying the cordinates
    x = sorted(x_dict.keys())
    y = sorted(y_dict.keys())

#selecting one horizontal axis per 40 pixels, as we know the horizan axis are seperated by roughly 45 pixels
#similarly slecting one vertical axis per 35 vertical pixels
    for i in range(len(x)-1):
        y_min = 200
        if x[i] > x_min:
            x_min  = x[i]+40
            for j in range(len(y)-1):
                if y[j] > y_min:
                    y_min = y[j]+35
#if two horizontal lines in the intial list (which means ther are quite favorable to become actual final axis) is seperated by less than 10 pixels,
#we have shilfted the current horizontal axis by 5 pixels down
#similarly we have shilfted vertical axus by 2 units to the left
                    if x[i+1] - x[i] < 10:
                        if y[j+1] - y[j] < 10:
                            l.append((x[i]+5,y[j] + 2))
                        else:
                            l.append((x[i]+5,y[j]))
                    else:
                        if y[j+1] - y[j] < 10:
                            l.append((x[i]+2,y[j] + 2))
                        else:
                            l.append((x[i]+2,y[j]))

    return l
    
#Function to impute the missing horizon cordinates, with the helpm of already found cordinates
#As the perfect hoerizon axis will be parallel to each other, with a distance of roughly 45 pixels between them, 
#used this information to impute the missing horizontal lines
def box_index_finder(fun_l):
#As the last horizon axis(pixel position of the last set of question was in 2000 range and most of time,
#we are missing on this particular axis, we have imputed this with the help of already present lower most horizontal axis)
    l = list(fun_l)
    while l[-1][0] < 2000:
        l.append((l[-2][0] + 45, l[-2][1]))

#creating two lists to accomadate unique horizontal and vertical cordinates of the boxes
#this lists will give the intial cordinates of all the boxes present in the sheet
    x_unique = []
    y_unique = []

#adding a missing horizontal axis
#horizontal axis was considered missing by selecting top to down horizontal axis one by one seeing the difference between two consecutive axis
#if the difference if more than 70, then a line was added
    i = 0
    while i < len(l)-1:
        if l[i+1][0] - l[i][0] > 70:
            l.insert(i+1,(l[i][0]+45, l[i][1]))

#adding uniques horizontal, vertical cordinates to the list
        x, y = l[i][0], l[i][1]
        
        if x not in x_unique:
            x_unique.append(x)
        if y not in y_unique:
            y_unique.append(y)
        i +=1
    if l[-1][0] not in x_unique:
        x_unique.append(l[-1][0])
    if l[-1][1] not in y_unique:
        y_unique.append(l[-1][1])

    return x_unique, y_unique


#function to given the actual answer dictionaries by taking actaul image, template and touple containing x and y cordinates of the boxes  
def answer_finder(box, actual_image, template, inter_image):
#defining functional parametrs to store results and finally will return them
    d = {}
    dd = {}
    ddd = {}
#dictionary to allocate string answers from int answer
    inter_dict = {"1":"A", "2":"B", "3":"C", "4": "D", "5": "E"}
#initializing dictionaries
    for i in range(1,86):
        d[i] = []
        dd[i] = []
        ddd[i] = []
#getting the horizontal, vertical box coordinates
    x,y = box[0], box[1]
#loopin over all x, y(each x,y corrsponds to a box in the sheet)
    for i in range(len(x)):
        for j in range(len(y)):

#as sheet id divided into 3 sections vertically, we have maintained three conditions 
#for each section there will be muliple questions, decoding accordingly
#first five boxes (question one boxes), will be in first vertical section, therefore 0<= j <=4
#seconde five boxes (question one in the seconde vertical block), therefore 5<=j<=9
            if 0 <= j <= 4:
                if j == 0:
#for each box the average intensity was caluclated and appended to reuired dictionary
#the first j value corresponds to first box (option A), therefore along with current intensity, average intensity to the left of this block was caluclated, to check for the presence of any charecters
                    curr_intensity = intensity(x[i], y[j], actual_image, template)
#As the student write charecters in a space left to question, the space contraint is a bit flexible for them, so checking multiple intensity values to the left an dpicking the minimum value to commapre to the threshold
                    left_intensity = min(intensity(x[i], y[j]-100, actual_image, template), intensity(x[i], y[j]-70, actual_image, template))
                    d[i+1].append(left_intensity)
                    d[i+1].append(curr_intensity)
#if current intensity is less than 0.65 (all the whole imahe was binarised with 0 and 1) it was considered to be filled in by the student
                    if curr_intensity < 0.65:
                        dd[i+1].append(inter_dict[str(j+1)])
#changing the intenstity of this position in the intermiedate image, this was done to output a modified image
                        intensity_changer(x[i], y[j], inter_image, template)
#if left intensity is less than 0.9, we are concluding the presence of a charecter to the left of question, therefore appending "x" to a spereate dictionary
                    if left_intensity < 0.9:
                        ddd[i+1].append("x")
#                        intensity_changer(x[i], y[j]-90, inter_image, template)
                else:
#doing similar work for all the questions (all vertical sections)
                    curr_intensity = intensity(x[i], y[j], actual_image, template)
                    d[i+1].append(curr_intensity)
                    if curr_intensity < 0.65:
                        dd[i+1].append(inter_dict[str(j+1)])
                        intensity_changer(x[i], y[j], inter_image, template)
#                print ("")
            elif 5<= j <=9:
                if j == 5:
                    curr_intensity = intensity(x[i], y[j], actual_image, template)
                    left_intensity = min(intensity(x[i], y[j]-100, actual_image, template), intensity(x[i], y[j]-70, actual_image, template))
                    d[i+1+29].append(left_intensity)
                    d[i+1+29].append(curr_intensity)
                    if curr_intensity < 0.65:
                        dd[i+1+29].append(inter_dict[str(j+1-5)])
                        intensity_changer(x[i], y[j], inter_image, template)
                    if left_intensity < 0.9:
                        ddd[i+1+29].append("x")
#                        intensity_changer(x[i], y[j]-90, inter_image, template)
                else:
                    curr_intensity = intensity(x[i], y[j], actual_image, template)
                    d[i+1+29].append(curr_intensity)
                    if curr_intensity < 0.65:
                        dd[i+1+29].append(inter_dict[str(j+1-5)])
                        intensity_changer(x[i], y[j], inter_image, template)
#                d[i+1+29]
#                print ()
            else:
                if i > 26:
                    continue
                else:
                    if j == 10:
                        curr_intensity = intensity(x[i], y[j], actual_image, template)
                        left_intensity = min(intensity(x[i], y[j]-100, actual_image, template), intensity(x[i], y[j]-70, actual_image, template))
                        d[i+1+58].append(left_intensity)
                        d[i+1+58].append(curr_intensity)
                        if curr_intensity < 0.65:
                            dd[i+1+58].append(inter_dict[str(j+1-10)])
                            intensity_changer(x[i], y[j], inter_image, template)
                        if left_intensity < 0.9:
                            ddd[i+1+58].append("x")
#                            intensity_changer(x[i], y[j]-90, inter_image, template)
                    else:
                        curr_intensity = intensity(x[i], y[j], actual_image, template)
                        d[i+1+58].append(curr_intensity)
                        if curr_intensity < 0.65:
                            dd[i+1+58].append(inter_dict[str(j+1-10)])
                            intensity_changer(x[i], y[j], inter_image, template)
                        
#passing the dictionaries with question wose intensity values, answer value, left intensity flag value
    return d, dd,ddd, inter_image

#Function to take the dictionaries files create and output qa text file as required
def file_writing(d, dd, out_file):
    print ("writing file")
    l = []
    for k in d:
#        print (k)
        if dd[k]:
            a = "".join(d[k]) + " "+dd[k][0]
        else:
            a = "".join(d[k])
        l.append(str(str(k) + " " +str(a)))
    with open(out_file, 'w') as f:
        for item in l:
            f.write("%s\n" % item)
    print ("saved file")
#        outfile.write("\n".join(itemlist))


#main function         
if __name__ == '__main__':
    print ("Recognizing from input image")
    input_image = sys.argv[1]
#    input_image = "F:\\IU_Acads\\Sem2\\CV\\A1\\aboppana-sdasara-simang-a1\\test-images\\a-30.jpg"
    output_image = sys.argv[2]
#    output_image = "F:\\IU_Acads\\Sem2\\CV\\A1\\lol_check_pil.jpg"
    output_file = sys.argv[3]
#    output_file = "F:\\IU_Acads\\Sem2\\CV\\A1\\text_out_pil.txt"
    start_time = time.time()
    image = Image.open(input_image)
#converting image to numpy array
    image = np.array(image)
#creating a intermediate image, to edit the itensity vaues at predicted answer position
    intermidiate_image = image
#reading template file
    template = reading_template()
    reading_time = time.time()
#rescaling the image and template to binary pixel values
    image_rescale = rescale_pixels(image)
    template_rescale = rescale_pixels(template)
    rescaling_time = time.time()
    print ("Rescaling time: "+str(rescaling_time - reading_time))
#doing the template matching
    d,f, max_count = finding_patterns(image_rescale, template_rescale)
    pattern_time = time.time()
    print ("Template time: "+str(pattern_time - rescaling_time))
#getting good cordinate points of both the axis
    good_keys_x, good_keys_y = finding_keys(f, max_count)
#getting modifed coordinates values
    intermediate_box_list = box_finder(good_keys_x, good_keys_y)
#getting final touple containing the actual box starting coordinates
    final_box = box_index_finder(intermediate_box_list)
    final_time = time.time()
#getting the intensity, answer, left intensity values of each question
    answer, answer_option, x_option, changed_image = answer_finder(final_box, image_rescale, template_rescale, intermidiate_image)
    answer_time = time.time()
    print ("final answer time: " + str(answer_time - final_time))
#saving the intensity changed image
    result = Image.fromarray(changed_image)
    result.save(output_image)    
    print ("output image saved")
#saving text file
    file_writing(answer_option, x_option, output_file)
    print ("process completed")
    print ("Total time taken: " + str(time.time() - start_time))
