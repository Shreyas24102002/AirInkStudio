import cv2
import numpy as np
import os
import HandTrackingModule as htm
import tkinter as tk
from tkinter import simpledialog
from tkinter import filedialog
import webbrowser
from tkinter import Text, Button


brushThickness = 10  #15
eraserThickness = 50
textThickness = 1 #Thickness for our text feature
textSize = 1
image_mode = False
loaded_image = None
image_position = None  # We need this to eliminate the error of over sized image
fixed_width, fixed_height = 300, 300  # Bug fixed: When we use to import the image
# The size of the image used to be huge and uneven for different images so decided
# to keep the dimensions of the image to be constant.

def switch_mode(x):
    global drawColor, current_brush_style
    # When the eraser is selected, set the brush style to "Eraser" and color to white (or any color to indicate erasure)
    if cv2.getTrackbarPos("Eraser", "Color Palette") == 1:
        current_brush_style = "Eraser"
        drawColor = (255, 255, 255)  # Assuming white is the background color
    else:
        # When the drawing mode is selected, revert to the previously chosen color and brush style
        current_brush_style = "Normal Brush"  # or any other default/previous brush style
        b = cv2.getTrackbarPos("Blue", "Color Palette")
        g = cv2.getTrackbarPos("Green", "Color Palette")
        r = cv2.getTrackbarPos("Red", "Color Palette")
        drawColor = (b, g, r)

cv2.namedWindow("Color Palette")
cv2.resizeWindow("Color Palette", 300, 400)
cv2.createTrackbar("Blue", "Color Palette", 0, 255, lambda x: None)
cv2.createTrackbar("Green", "Color Palette", 0, 255, lambda x: None)
cv2.createTrackbar("Red", "Color Palette", 0, 255, lambda x: None)
cv2.createTrackbar("Eraser", "Color Palette", 0, 1, switch_mode)
cv2.createTrackbar("Eraser Size", "Color Palette", 1, 100, lambda x: None)
cv2.createTrackbar("Line Mode", "Color Palette", 0, 1, lambda x: None)
cv2.createTrackbar("Circle Mode", "Color Palette", 0, 1, lambda x: None)
cv2.createTrackbar("Rectangle Mode", "Color Palette", 0, 1, lambda x: None)


folderPath = "Header"
myList = os.listdir(folderPath)
overLayList = []

for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overLayList.append(image)

header = overLayList[0]
drawColor = (255, 0, 255)
textColor = (255, 255, 255)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = htm.handDetector(detectionCon=0.85)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

undo_stack = []

line_mode = False
rectangle_mode = False
circle_mode = False
text_mode = False
shape_start = None

brush_styles = {
    "Normal Brush": (15, False),
    "Airbrush": (5, True),
    "Oil Brush": (20, False),
    "Crayon": (15, False),
    "Marker": (10, False),
    "Natural Pencil": (8, False),
    "Watercolor Brush": (15, False),
    "Stencil": (30, False),
    "Spray": (10, True),
    "Needle": (1, False),
    "Signature": (2, False),
}
current_brush_style = "Normal Brush"


#  Buttons code: -

# Function to handle star click
def rate_application(rating):
    for i in range(rating):
        stars[i].config(bg="gold")
    for i in range(rating, 5):
        stars[i].config(bg="gray")

def open_showcase():
    webbrowser.open("https://airinkstudio.netlify.app/")

def open_chat():
    webbrowser.open("https://fluffy-hotteok-0d25ae.netlify.app/")

root = tk.Tk()
root.title("Thank you")

# Text widget for colorful text
text_widget = Text(root, height=2, width=30, bg=root.cget("background"), bd=0)
text_widget.pack(expand=True, fill='both')
text_widget.tag_configure("red", foreground="red")
text_widget.tag_configure("blue", foreground="blue")
text_widget.tag_configure("green", foreground="green")
text_widget.tag_configure("yellow", foreground="yellow")
text_widget.tag_configure("cyan", foreground="cyan")
text_widget.tag_configure("center", justify='center')

text_widget.insert("1.0", "Thanks for using ", "center")
text_widget.insert("end", "AirInk ", "red center")
text_widget.insert("end", "Studio", "blue center")
text_widget.configure(state="disabled")

# Stars for rating
stars_frame = tk.Frame(root)
stars_frame.pack()
stars = []
for i in range(1, 6):
    star = Button(stars_frame, text="★", bg="gray", command=lambda i=i: rate_application(i))
    star.pack(side=tk.LEFT, padx=5)
    stars.append(star)

# "Rate us" text
rate_us_label = tk.Label(root, text="Rate us", bg="white")
rate_us_label.pack(side=tk.TOP, pady=5)


btn_showcase = tk.Button(root, text="Showcase Community", command=open_showcase)
btn_showcase.pack(side=tk.LEFT, padx=10, pady=10)

btn_chat = tk.Button(root, text="Chat with Others", command=open_chat)
btn_chat.pack(side=tk.LEFT, padx=10, pady=10)




def undo():
    if undo_stack:
        undo_stack.pop()  # Remove the last action
        imgCanvas.fill(0)  # Clear the canvas
        for action in undo_stack:  # Redraw all actions except the last one
            if action[0] == 'line':
                cv2.line(imgCanvas, action[1], action[2], action[3], action[4])
            elif action[0] == 'rectangle':
                cv2.rectangle(imgCanvas, action[1], action[2], action[3], action[4])
            elif action[0] == 'circle':
                cv2.circle(imgCanvas, action[1], action[2], action[3], action[4])
            elif action[0] == 'text':
                cv2.putText(imgCanvas, action[1], action[2], cv2.FONT_HERSHEY_SIMPLEX, action[3], action[4], action[5])


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)


    if current_brush_style != "Eraser":
        b = cv2.getTrackbarPos("Blue", "Color Palette")
        g = cv2.getTrackbarPos("Green", "Color Palette")
        r = cv2.getTrackbarPos("Red", "Color Palette")
        drawColor = (b, g, r)

    # Get the current positions of the color trackbars
    b = cv2.getTrackbarPos("Blue", "Color Palette")
    g = cv2.getTrackbarPos("Green", "Color Palette")
    r = cv2.getTrackbarPos("Red", "Color Palette")
    current_color = (max(1, b), max(1, g), max(1, r))



    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()

        if cv2.getTrackbarPos("Eraser", "Color Palette") == 1:
            eraserThickness = cv2.getTrackbarPos("Eraser Size", "Color Palette")

        line_mode = cv2.getTrackbarPos("Line Mode", "Color Palette") == 1
        circle_mode = cv2.getTrackbarPos("Circle Mode", "Color Palette") == 1
        rectangle_mode = cv2.getTrackbarPos("Rectangle Mode", "Color Palette") == 1

        # Disable other modes when one mode is active
        if circle_mode:
            rectangle_mode = line_mode = False
        elif rectangle_mode:
            circle_mode = line_mode = False

        # Selection Mode:  using Headers on the top
        # if fingers[1] and fingers[2]:
        #     xp, yp = 0, 0
        #     # Checking for the click
        #     if y1 < 125:
        #         if 250 < x1 < 450:
        #             header = overLayList[0]
        #             drawColor = (255, 0, 255)
        #         elif 550 < x1 < 750:
        #             header = overLayList[1]
        #             drawColor = (255, 0, 0)
        #         elif 800 < x1 < 950:
        #             header = overLayList[2]
        #             drawColor = (0, 255, 0)
        #         elif 1050 < x1 < 1200:
        #             header = overLayList[3]
        #             drawColor = (0, 0, 0)

        # Placing the image at the recorded position

        #Image Import Method 1: -

        # if image_mode and loaded_image is not None and image_position:
        #     h, w, _ = loaded_image.shape
        #     canvas_height, canvas_width, _ = imgCanvas.shape
        #
        #     # Ensure the image fits within the canvas boundaries
        #     if image_position[1] + h > canvas_height or image_position[0] + w > canvas_width:
        #         # Resize or truncate the image if it doesn't fit
        #         h_fit = min(h, canvas_height - image_position[1])
        #         w_fit = min(w, canvas_width - image_position[0])
        #         loaded_image = cv2.resize(loaded_image, (w_fit, h_fit))
        #
        #     imgCanvas[image_position[1]:image_position[1] + h_fit,
        #     image_position[0]:image_position[0] + w_fit] = loaded_image
        #     image_mode = False  # Reset image mode

        #Image Import Method 2: -
        if image_mode and loaded_image is not None:
            imgCanvas[y1:y1 + fixed_height, x1:x1 + fixed_width] = loaded_image
            image_mode = False  # Reset image mode once the image is placed

        if key == ord('t') and fingers[1] and fingers[2]:
            text_mode = True

        # Handling text mode
        if text_mode and fingers[1] and fingers[2]:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            input_text = simpledialog.askstring("Text Input", "Enter the text:")
            root.destroy()  # Destroy the root window after input is taken
            if input_text:
                cv2.putText(imgCanvas, input_text, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, textSize, textColor, textThickness)
                undo_stack.append(('text', input_text, (x1, y1), textSize, textColor, textThickness))
            text_mode = False

        if line_mode or rectangle_mode or circle_mode:
            if fingers[1] and not fingers[2]:
                if shape_start is None:
                    shape_start = (x1, y1)
                if line_mode:
                    cv2.line(img, shape_start, (x1, y1), drawColor, brushThickness)
                elif rectangle_mode:
                    cv2.rectangle(img, shape_start, (x1, y1), drawColor, brushThickness)
                elif circle_mode:
                    radius = int(np.linalg.norm(np.array(shape_start) - np.array((x1, y1))))
                    cv2.circle(img, shape_start, radius, drawColor, brushThickness)
            elif fingers[1] and fingers[2] and shape_start:  # Finalize the shape when selection mode is entered
                if line_mode:
                    cv2.line(imgCanvas, shape_start, (x1, y1), drawColor, brushThickness)
                    undo_stack.append(('line', shape_start, (x1, y1), drawColor, brushThickness))
                elif rectangle_mode:
                    cv2.rectangle(imgCanvas, shape_start, (x1, y1), drawColor, brushThickness)
                    undo_stack.append(('rectangle', shape_start, (x1, y1), drawColor, brushThickness))
                elif circle_mode:
                    radius = int(np.linalg.norm(np.array(shape_start) - np.array((x1, y1))))
                    cv2.circle(imgCanvas, shape_start, radius, drawColor, brushThickness)
                    undo_stack.append(('circle', shape_start, radius, drawColor, brushThickness))
                line_mode = rectangle_mode = circle_mode = False
                shape_start = None


        # Normal Drawing Mode
        elif fingers[1] and not fingers[2]:
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if line_mode:
                # When in line mode, draw a line from the starting point to the current point
                if shape_start is None:
                    shape_start = (x1, y1)
                cv2.line(img, shape_start, (x1, y1), drawColor, brushThickness)
            elif circle_mode:
                radius = int(np.linalg.norm(np.array(shape_start) - np.array((x1, y1))))
                cv2.circle(img, shape_start, radius, drawColor, brushThickness)
            elif rectangle_mode:
                cv2.rectangle(img, shape_start, (x1, y1), drawColor, brushThickness)

            if current_brush_style == "Eraser":
                brush_thickness = eraserThickness
                drawColor = (0, 0, 0)  # Or your canvas background color
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_thickness)
            elif current_brush_style == "Signature":
                brush_thickness = brush_styles["Signature"][0]
                drawColor = (b, g, r)
            else:
                brush_thickness, spray_mode = brush_styles[current_brush_style]
            if spray_mode:
                for _ in range(10):
                    sx = np.random.randint(x1 - brush_thickness, x1 + brush_thickness)
                    sy = np.random.randint(y1 - brush_thickness, y1 + brush_thickness)
                    cv2.circle(imgCanvas, (sx, sy), 2, drawColor, cv2.FILLED)
            else:
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_thickness)
            xp, yp = x1, y1
            if not (line_mode or rectangle_mode or circle_mode):
                undo_stack.append(('line', (xp, yp), (x1, y1), drawColor, brush_thickness))
        else:
            # Resetting xp and yp when the index finger is not up
            xp, yp = 0, 0

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 20, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # Setting the header image
    # img[0:125, 0:1280] = header

    # Visual indicators for features
    indicator_font_scale = 1.2  # Increased font scale for better visibility
    indicator_thickness = 2  # Increased thickness for the text

    colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 255, 0)]  # Red, Blue, Green, Cyan, Yellow

    text = "AirInk Studio"
    x_pos = int(img.shape[1] / 2 - (len(text) * indicator_font_scale * 11) / 2)  # Center the text
    y_pos = 30  # Adjusted top position to prevent cutoff

    for i, char in enumerate(text):
        color = colors[i % len(colors)]  # Cycle through the colors
        cv2.putText(img, char, (x_pos, y_pos), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale + 0.4, color,
                    2)  # Slightly larger text
        x_pos += int((indicator_font_scale + 0.4) * 11)  # Move x position for the next character

    cv2.putText(img, "U - Undo", (10, 30), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale, (255, 0, 255),
                indicator_thickness)
    cv2.putText(img, "S - Save", (10, 60), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale, (0, 255, 0),
                indicator_thickness)
    cv2.putText(img, "Q - Quit", (10, 90), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale, (0, 0, 255),
                indicator_thickness)
    cv2.putText(img, "I - Image Import", (10, 120), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale, (0, 255, 255),
                indicator_thickness)
    cv2.putText(img, "T - Text", (10, 150), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale, (255, 0, 0),
                indicator_thickness)
    cv2.putText(img, f"B - {current_brush_style}", (10, 180), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale,
                (255, 0, 255), indicator_thickness)

    key = cv2.waitKey(1)

    if key == ord('t') and (fingers[1] and fingers[2]):
        text_mode = True
        line_mode = rectangle_mode = circle_mode = False
    elif key == ord('+'):  # Increase text size
        textSize += 1
    elif key == ord('-'):  # Decrease text size
        textSize = max(1, textSize - 1)
    # Include other key controls...

    if key == ord('x'):
        line_mode = not line_mode
        rectangle_mode = circle_mode = False
        shape_start = None
    elif key == ord('r'):
        rectangle_mode = not rectangle_mode
        line_mode = circle_mode = False
        shape_start = None
    elif key == ord('c') and not circle_mode:  # Prevents conflict with color palette
        circle_mode = not circle_mode
        line_mode = rectangle_mode = False
        shape_start = None
    elif key == ord('s'):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            cv2.imwrite(file_path, imgCanvas)
    elif key == ord('q'):
        break
    elif key == ord('u'):
        undo()
    # elif key == ord('b'):
    #     current_brush_style = list(brush_styles.keys())[(list(brush_styles.keys()).index(current_brush_style) + 1) % len(brush_styles)]

    if key == ord('b'):
        brush_names = list(brush_styles.keys())
        current_index = brush_names.index(current_brush_style)
        current_index = (current_index + 1) % len(brush_names)
        current_brush_style = brush_names[current_index]
        brushThickness, _ = brush_styles[current_brush_style]  # Update brush thickness based on selected style
        cv2.putText(img, f"B - {current_brush_style}", (10, 210), cv2.FONT_HERSHEY_PLAIN, indicator_font_scale,
                    (255, 255, 0), 1)


    if key == ord('i') and fingers[1] and fingers[2]:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        image_path = filedialog.askopenfilename(title='Select an image', filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if image_path:
            loaded_image = cv2.imread(image_path)
            loaded_image = cv2.resize(loaded_image, (fixed_width, fixed_height))  # Resize image
            image_mode = True  # Set image mode to true to place the image on the canvas
        root.destroy()




    cv2.imshow("Image", img)
    # cv2.imshow("Canvas", imgCanvas)

root.mainloop()
cap.release()
cv2.destroyAllWindows()
