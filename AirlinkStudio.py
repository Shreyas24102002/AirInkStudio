import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm
import tkinter as tk
from tkinter import filedialog

brushThickness = 15
eraserThickness = 70  # Increased eraser thickness

folderPath = "Header"
myList = os.listdir(folderPath)
print(myList)
overLayList = []

for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overLayList.append(image)
print(len(overLayList))

header = overLayList[0]
drawColor = (255, 0, 255)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

undo_stack = []  # To store the drawing history

drawing = False  # Indicates whether the user is currently drawing

brush_styles = {
    "Normal Brush": (15, False),
    "Airbrush": (5, True),
    "Oil Brush": (20, False),
    "Crayon": (10, False),
    "Marker": (10, False),
    "Natural Pencil": (8, False),
    "Watercolor Brush": (15, False),
    "Stencil": (30, False),  # Improved Stencil brush style
    "Spray": (10, True),
}
current_brush_style = "Normal Brush"  # Default brush style

def undo():
    if len(undo_stack) > 0:
        action = undo_stack.pop()
        redraw_canvas()

def redraw_canvas():
    imgCanvas[:] = 0  # Clear the canvas
    for action in undo_stack:
        if action[0] == 'line':
            cv2.line(imgCanvas, action[1], action[2], action[3], action[4])
        elif action[0] == 'rect':
            cv2.rectangle(imgCanvas, action[1], action[2], action[3], action[4])

while True:
    # Import Image
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Find Hand Landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Tip of Index and Middle Finger
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # Check which fingers are up
        fingers = detector.fingersUp()

        # If selection mode - Two Fingers are up
        if fingers[1] and fingers[2]:
            xp, yp = 0, 0
            # Checking for the click
            if y1 < 125:
                if 250 < x1 < 450:
                    header = overLayList[0]
                    drawColor = (255, 0, 255)
                elif 550 < x1 < 750:
                    header = overLayList[1]
                    drawColor = (255, 0, 0)
                elif 800 < x1 < 950:
                    header = overLayList[2]
                    drawColor = (0, 255, 0)
                elif 1050 < x1 < 1200:
                    header = overLayList[3]
                    drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1, y1 - 35), (x2, y2 + 35), drawColor, cv2.FILLED)
            drawing = False

        # If Drawing Mode - Index finger is up
        if fingers[1] and fingers[2] == False:
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            brush_thickness, spray_mode = brush_styles[current_brush_style]

            if spray_mode:
                # Simulate a spray paint effect
                for _ in range(10):
                    sx = np.random.randint(x1 - brush_thickness, x1 + brush_thickness)
                    sy = np.random.randint(y1 - brush_thickness, y1 + brush_thickness)
                    cv2.circle(imgCanvas, (sx, sy), 2, drawColor, cv2.FILLED)
            else:
                if current_brush_style == "Crayon":
                    # Crayon style drawing
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_thickness, lineType=cv2.LINE_AA)
                elif current_brush_style == "Stencil":
                    # Improved Stencil style drawing
                    cv2.putText(imgCanvas, 'A', (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, brush_thickness/15, drawColor, brush_thickness, lineType=cv2.LINE_AA)
                elif current_brush_style == "Oil Brush":
                    # Oil Brush style drawing
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_thickness, lineType=cv2.LINE_AA)
                elif current_brush_style == "Airbrush":
                    # Airbrush style drawing
                    cv2.circle(imgCanvas, (x1, y1), brush_thickness, drawColor, cv2.FILLED, lineType=cv2.LINE_AA)
                elif current_brush_style == "Watercolor Brush":
                    # Watercolor Brush style drawing
                    cv2.circle(imgCanvas, (x1, y1), brush_thickness, drawColor, cv2.FILLED, lineType=cv2.LINE_AA)
                else:
                    # Other brush styles
                    cv2.line(img, (xp, yp), (x1, y1), drawColor, brush_thickness)
                    if not drawing:
                        undo_stack.append(('line', (xp, yp), (x1, y1), drawColor, brush_thickness))
                    cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_thickness)

            xp, yp = x1, y1
            drawing = True

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 20, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # Setting the header image
    img[0:125, 0:1280] = header

    # Add visual indicators for undo, save, and quit
    cv2.putText(img, "U - Undo", (10, 150), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    cv2.putText(img, "S - Save", (10, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.putText(img, "Q - Quit", (10, 250), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
    cv2.putText(img, f"B - {current_brush_style}", (10, 300), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

    key = cv2.waitKey(1)
    if key == ord('s'):
        # Prompt the user to choose a save location and filename
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            # Save the canvas as an image
            cv2.imwrite(file_path, imgCanvas)
            print(f"Image saved as {file_path}")
    elif key == ord('q'):
        break  # Exit the program
    elif key == ord('u'):
        undo()
    elif key == ord('b'):
        # Toggle between brush styles
        brush_styles_keys = list(brush_styles.keys())
        current_brush_style = brush_styles_keys[(brush_styles_keys.index(current_brush_style) + 1) % len(brush_styles)]

    cv2.imshow("Image", img)
    cv2.imshow("Canvas", imgCanvas)

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()
