# importing required packages
import cv2
import numpy as np

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
drawColor=(0, 0, 255)
xp, yp = 0, 0
# creating video capture object
cap=cv2.VideoCapture(0)
cap.set(3, 1280)  # setting the width
cap.set(4, 720)  # setting the height

# initializing hand detector class from hand tracking module
detector = htm.handDetector(detectionCon=0.8)

imgCanvas = np.zeros((720, 1280, 3), np.uint8)
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
            # print("we are in selection mode now")
            xp, yp = 0, 0
            if y1<108:
                if 200<x1<450:
                    header=overLayLst[0]
                    drawColor = (0, 0, 255)
                elif 500<x1<750:
                    header=overLayLst[1]
                    drawColor = (0, 255, 0)
                elif 800<x1<1100:
                    header=overLayLst[2]
                    drawColor = (255, 0, 0)
                elif 1150<x1<1280:
                    header=overLayLst[3]
                    drawColor = (0, 0, 0)
        # if only index finger is up, we'll consider this as drawing mode
        if fingers[1] and fingers[2]==0:
            # print("We are in drawing mode now")
            # if we are in first frame, the lines starts drawing from (0, 0) which might look backward, so we're changing
            if xp==0 and yp==0:
                xp, yp=x1, y1
            if drawColor ==(0, 0, 0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, 50)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, 50)
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, 15)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, 15)
            xp, yp=x1, y1  # updating the previous points to propagate the line

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)
    img[0:125, 0:1280]=header  # overlaying the header on the image

    # adding both the images(i.e., original webcam image and canvas image)
    # cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)
    cv2.imshow("Image", img)
    cv2.imshow("Image Canvas", imgCanvas)
    cv2.imshow("Image Inverse", imgInv)
    cv2.waitKey(1)