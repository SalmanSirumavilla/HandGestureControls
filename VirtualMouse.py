# reference - https://www.computervision.zone/lessons/ai-virtual-mouse-video-lesson/

# importing required modules
import cv2
import time
import HandTrackingModule as htm
import numpy as np
import mediapipe as mp

# importing autopy for mouse controls
import autopy

# width and height of the window
widCam, htCam = 1280, 720
# frame reduction
frameRed=100
# smoothening factor
smoothFact=5
# previous time
prvTime=0
# previous locations of x and y
prevLocX, prevLocY = 0, 0
curLocX, curLocY = 0,  0

# initializing video capture
cap=cv2.VideoCapture(0)

# setting width and height of the cam
cap.set(3, widCam)
cap.set(4, htCam)


# creating handDetector object to detect hands(maximum=1)
detector = htm.handDetector(maxHands=1)
widSc, htSc=autopy.screen.size() # getting the actual screen sizes
# print(widSc, htSc)

# reading the video
while True:
    _, img=cap.read()

    # finding landmarks of hands
    img=detector.findHands(img)
    lmList, bbox=detector.findPosition(img)

    # getting the tip values of index and middle finger values
    if len(lmList)!=0 : # control goes into the loop if there is something in the list
        x1, y1 = lmList[8][1:] # index finger(we want element no 1 and 2)
        x2, y2 = lmList[12][1:] # middle finger
        # print(x1, y1, x2, y2)

        # checking if the fingers are up
        fingers = detector.fingersUp()
        # print(fingers) # if the fingers are up, respective indexes will be set to 1

        # drawing a rectangle in the window to fit the handles with in the rectangle
        cv2.rectangle(img, (frameRed, frameRed), (widCam-frameRed, htCam-frameRed), (0,255,0),3)

        # if only index finger is up -  we are in Moving mode
        if fingers[1] == 1 and any(fingers[2:]) == 0:
            # converting co-ordinates with reference to screen sizes to set window sizes
            x3=np.interp(x1, (frameRed, widCam-frameRed), (0, widSc))
            y3=np.interp(y1, (frameRed, htCam-frameRed), (0, htSc))

            # smoothening the values, so that the output window will flicker less
            # instead of x3 and y3 we will send the prevLoc and curLoc values for smoothening
            curLocX = prevLocX+(x3-prevLocX)/smoothFact
            curLocY = prevLocY+(y3 - prevLocY) / smoothFact

            # Moving mouse
            autopy.mouse.move(widSc-curLocX, curLocY)
            # if the index finger is up, we're circling that with black color
            cv2.circle(img, (x1,y1), 10, (0,0,0), cv2.FILLED)
            prevLocX, prevLocY = curLocX, curLocY

        # if both index and middle are up then we will find the distance to perform click functionality based on the len
        if fingers[1] == 1 and fingers[2] == 1 and any(fingers[3:]) == 0:

            # here find distance function is returning length b/w the point, image passes and info of them
            # including the centers of them(we'll use the centre points later for click purpose)
            leng, img, info = detector.findDistance(8, 12, img)
            print(leng)

            # setting the threshold length val to 40 for click purpose
            if leng<40:
                cv2.circle(img, (info[4], info[5]), 15, (0, 255, 0), cv2.FILLED)

                # once the length between index and middle finger is belo 40 we'll perform click
                autopy.mouse.click()


    # Displaying the frame rate
    cmpTime=time.time()
    fps=1/(cmpTime-prvTime)
    prvTime=cmpTime
    cv2.putText(img, str(int(fps)), (20,50), cv2.FONT_HERSHEY_PLAIN, 3, (0,0,255), 3)
    # displaying Image
    cv2.imshow("Image",img)
    cv2.waitKey(1)