# importing required packages
import cv2
import HandTrackingModule as htm
import numpy
import time
import os

path='Header'
img_lst=os.listdir(path)
print(img_lst)
overLayLst=[]
for each in img_lst:
    img=cv2.imread(path+'/{}'.format(each))
    overLayLst.append(img)

print(len(overLayLst))
header=overLayLst[0]  # selecting the first image as the header

# creating video capture object
cap=cv2.VideoCapture(0)
cap.set(3, 1280)  # setting the width
cap.set(4, 720)  # setting the height

# initializing hand detector class from hand tracking module
detector = htm.handDetector(detectionCon=0.8)
while True:
    _, img=cap.read(0)
    img = cv2.flip(img, 1)  # flipping the image in first direction

    img=detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)
    # print(lmList)

    if len(lmList) != 0:
        # getting the tip of middle finger and index finger values
        x1, y1 = lmList[8][1], lmList[8][2]
        x2, y3 = lmList[12][1], lmList[12][2]
        fingers=detector.fingersUp()
        # because of image flip above here we have to change the thumb value(.i.e., thumb considers left and right
        # positions of it's tip to check if it's up
        if fingers[0]==0:
            fingers[0]=1
        else:
            fingers[0]=0
        print(fingers)

        # if both the index and middle fingers are up, we will consider it as selection mode(color selection)
        if fingers[1] and fingers[2]:
            print("we are in selection mode now")
            if y1<108:
                if 200<x1<450:
                    header=overLayLst[0]
                elif 500<x1<750:
                    header=overLayLst[1]
                elif 800<x1<1100:
                    header=overLayLst[2]
                elif 1150<x1<1280:
                    header=overLayLst[3]
        # if only index finger is up, we'll consider this as drawing mode
        if fingers[1] and fingers[2]==0:
            print("We are in drawing mode now")


    img[0:125, 0:1280]=header  # overlaying the header on the image
    cv2.imshow("Image", img)
    cv2.waitKey(1)