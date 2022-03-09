# importing required packages

import cv2
import HandTrackingModule as htm
from time import sleep
from pynput.keyboard import Controller

cap=cv2.VideoCapture(0)  # creating VideoCapture() object
# setting width and height of the image
cap.set(3, 1280)
cap.set(4, 720)

# initializing HandDetector from HandTrackingModule
detector = htm.handDetector(detectionCon=0.75)
keys_lst=[["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
          ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
          ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
final_txt=""
keyBoard = Controller()
# drawing button texts for all the buttons created in button_lst(i.e., buttons objects are created once, but have to
# draw for every frame
def drawAll(img, button_lst):
    for button in button_lst:
        cv2.rectangle(img, button.pos, (button.pos[0] + button.size[0], button.pos[1] + button.size[1]), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (button.pos[0] + 15, button.pos[1] + 65), cv2.FONT_HERSHEY_COMPLEX_SMALL, 4,
                    (255, 255, 255), 3)
    return img

# creating Button class to create button
class Button():
    def __init__(self, pos, text, size=[85, 85]):
        self.pos=pos
        self.text=text
        self.size=size
    # def draw(self, img):
        # return img

# initializing button class
# button = Button([100, 100], "S")
button_lst=[]
for i in range(len(keys_lst)):
    for indx, txt in enumerate(keys_lst[i]):
        button_lst.append(Button([100 * indx + 50, 100 * i + 50], txt))
while True:
    _, img=cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    img = drawAll(img, button_lst)

    # if hand is present in the frame
    if lmList:
        # print("Hand is present...")
        # print(lmList)
        # print(lmList[8][1], lmList[8][2])
        # print("****************")
        # cv2.circle(img, (lmList[8][0], lmList[8][1]), 15, (255, 255, 255), cv2.FILLED)
        for button in button_lst:
            x, y=button.pos
            w, h=button.size
            # print("we are here now..")
            # print(button.pos)
            # print(button.size)
            # print(lmList)

            # lmList[8] is indexing finger tio and [0] is the X co-ordinate of that
            # print(x)
            # print(lmList[8][0])
            # print(x+w)
            # print(x, y)
            # print(x+w, y+h)
            if x < lmList[8][1] < x+w and y < lmList[8][2] < y+h:
                # print("checking lmList")
                # print("********")
                # print("we're in the boundary")
                # print("********")

                cv2.rectangle(img, (x-5, y-5), (x+w+5, y+h+5),
                              (80, 127, 255), cv2.FILLED)
                # print("now we are here")
                cv2.putText(img, button.text, (x + 15, y + 65), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            4, (255, 255, 255), 3)
                l, _, _ = detector.findDistance(8, 12, img, draw = False)

                # when the distance between the tips is too less(i.e., clicked)
                # print(l)
                if l<30:
                    keyBoard.press(button.text)
                    cv2.rectangle(img, (button.pos[0]-10, button.pos[1]-10), (x + w+10, y + h+10),
                                  (0, 255, 0), cv2.FILLED)
                    # print("now we are here")
                    cv2.putText(img, button.text, (x + 15, y + 65), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                4, (255, 255, 255), 3)
                    # concatenating the text that is pressed at each frame to put it on the frame
                    final_txt+=button.text
                    sleep(0.40)

    cv2.rectangle(img, (50, 350), (700, 450),
                  (80, 127, 255), cv2.FILLED)
    # at end of each frame we are printing the final text on the screen
    cv2.putText(img, final_txt, (60, 425), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                4, (255, 255, 255), 3)

    # img = button.draw(img)

    cv2.imshow("Image", img)
    cv2.waitKey(1)