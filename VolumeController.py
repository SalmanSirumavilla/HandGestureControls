# importing basic packages
import time
import cv2
import numpy as np
import HandTrackingModule as htm  # importing hand tracking module

# importing packages required to work with the volume controls
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# initializing required packages
widCam, htCam = 1280, 720
prevTime = 0

cap = cv2.VideoCapture(0)  # initializing video capture
cap.set(3, widCam)  # propID 3 is width of cam
cap.set(4, htCam)  # propID 4 means height of the cam

# initializing the handDetector class of the HandTrackingModule
detector = htm.handDetector(maxHands=1)  # here we're giving maxHands=1, so will not look for two hands when doing
# gesture control

# pycaw initializations
# https://github.com/AndreMiras/pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# print(volume.GetVolumeRange())  # volume range is (-65.25, 0.0, 0.03125)
# volume.SetMasterVolumeLevel(-5, None)  # this method sets the volume(try to play around)

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol=0
volBar = 400  # initially setting the volume bar to zero which is 400(base point of the volume bar)
volPer = 0
fingers_gap = 0
area = 0  # to scale the area of the bounding box


while True:
    _, img = cap.read()  # reading each image frame
    img = detector.findHands(img)  # sending in the captured image as parameter to find Hands in it( returns img)
    lmList, bbox = detector.findPosition(img, draw=True)
    # print(lmList)
    if len(lmList) != 0:
        # print('now we are here')
        # print(lmList)

        # print(bbox) # here we are trying to find the area of the bounding box
        area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        # print('Area is: {}'.format(area))
        if 200<area<2000:
            # finding the distance between index and the thumb tips
            fingers_gap, img, info = detector.findDistance(4, 8, img)
            # print(fingers_gap)

            # converting the volume
            # finger gap range is [10-200](found from the above print value)
            # volume range is [-65.0 - 0] (from the volume.GetVolumeRange() function)
            # vol = np.interp(fingers_gap, [10, 200], [minVol, maxVol])
            volBar = np.interp(fingers_gap, [10, 200], [400, 150])
            volPer = np.interp(fingers_gap, [10, 200], [0, 100])
            # print(int(fingers_gap), vol)
            # volume.SetMasterVolumeLevel(vol, None) # this log scale is not performing well, so'll apply linear scale

            # reducing the resolution to make it smoother
            smoothness = 2  # even in our windows the window size is 2, so we are giving the same to replicate realtime
            volPer = smoothness * round(volPer/smoothness)

            # first we check the fingers that are up using fingersUP() function of the handDetector() class
            fingers = detector.fingersUp()
            # print(fingers)

            # if the little finger is down, then we'll set the volume and unless we just move the slider
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer/100, None)  # log scale is not working wellso applying linear scale
                cv2.circle(img, (info[4], info[5]), 15, (0, 255, 255), cv2.FILLED)

            if fingers_gap < 20:
                cv2.circle(img, (info[4], info[5]), 15, (0, 0, 0), cv2.FILLED)  # changing the color to black if gap is less

            if fingers_gap > 150:
                cv2.circle(img, (info[4], info[5]), 15, (0, 0, 255), cv2.FILLED)  # changing the color to red if gap is more(high vol)

    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)  # drawing a rectangle on the image to show the vol bar
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, '{}%'.format(int(volPer)), (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 5)

    # getting the current set volume and putting it on the image as Volume Set
    curVolume = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img, 'Volume Set: {}'.format(int(curVolume)), (400, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 5)

    # if the volume is going too high we're indicating it with red color
    if fingers_gap > 150:
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, '{}%'.format(int(volPer)), (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)

    # we're finding the fps(frames/sec) value using current time and previous time
    curTime = time.time()
    fps=1/(curTime-prevTime)
    prevTime = curTime
    # here we're pring the fps value on the image
    cv2.putText(img, 'FPS: {}'.format(int(fps)), (40,70), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 5)


    cv2.imshow("Img", img)  # showing captured/processed image
    cv2.waitKey(1)  # giving 1 milli second delay


