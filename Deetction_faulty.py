import cv2
import numpy as np
import os

def nothing(x):
    pass

# Load image using the provided path
image_path = r"C:\Users\kp140\Downloads\reregardingdetailsofaimlprojectguibased_\Original_Image.jpg"
frame = cv2.imread(image_path)
frame1 = cv2.imread(image_path)

# Convert image to HSV and apply mask
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
l_b = np.array([10, 14, 128])
u_b = np.array([33, 238, 255])
mask = cv2.inRange(hsv, l_b, u_b)

# Define kernel size and clean the mask
kernel = np.ones((7, 7), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# Apply mask and detect contours
res = cv2.bitwise_and(frame, frame, mask=mask)
contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
output = cv2.drawContours(res, contours, -1, (0, 0, 255), 3)

# Convert result to grayscale and blur it
gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
gray_blurred = cv2.blur(gray, (3, 3))

# Apply Hough Circle Transform
detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 45, param1=5, param2=20, minRadius=1, maxRadius=40)

# Check if any circles are detected
if detected_circles is not None:
    detected_circles = np.uint16(np.around(detected_circles))
    num_rows, faulty, num_cols = detected_circles.shape
    print("No of faulty arecanuts:", faulty)

    # Draw the detected circles
    for pt in detected_circles[0, :]:
        a, b, r = pt[0], pt[1], pt[2]
        cv2.circle(frame, (a, b), r, (0, 255, 0), 2)

    # Show the detected circles
    cv2.imshow("Detected Circle", frame)
else:
    print("No circles detected")

# Wait for key press and close windows
key = cv2.waitKey(0)
cv2.destroyAllWindows()
