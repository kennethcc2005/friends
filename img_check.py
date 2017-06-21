import os
import time
import cv2
import numpy as np
from matplotlib import pyplot as plt

img_list = os.listdir("img_file/")
wrong_img = []
for img_name in img_list[1:]:
	path = "img_file/"+img_name
	pic = cv2.imread(path, 0)

	if type(pic) == "NoneType":
		print(img_name)
		cv2.imshow(" img ", pic)	
		cv2.waitKey(0)
# 	if (pic.shape[0] < 10 )or (pic.shape[1]< 10):
# 		wrong_img.append(img_name)
# print(wrong_img)
