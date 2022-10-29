import cv2
import mediapipe as mp
import time  #to check the frame rate

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
# It contains parameters like static_mode, max_num_hands=2, min_detection_confidence
# min_tracking_confidence. We are keeping the default parameter setting only


while True:
    success, img = cap.read()


    cv2.imshow("Image", img)
    cv2.waitKey(1)

