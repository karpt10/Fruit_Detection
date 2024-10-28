import cv2
import numpy as np

# Load your image
image_path = "C:\\Users\\kp140\\Downloads\\reregardingdetailsofaimlprojectguibased_\\Original_Image.jpg"
img = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply a threshold to create a binary image
_, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# Define a kernel for morphological operations
kernel = np.ones((3, 3), np.uint8)  # Adjust size as needed

# Apply closing to close small gaps within objects
closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# Apply opening to separate overlapping objects
opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

# Find contours on the processed binary image
contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Count the contours, assuming each contour is an arecanut
arecanut_count = len(contours)

# Draw contours on the original image for visualization
output_image = img.copy()
cv2.drawContours(output_image, contours, -1, (0, 255, 0), 2)

# Display the count
print(f"Total arecanuts counted: {arecanut_count}")

# Optionally display the images at different steps for verification
cv2.imshow("Threshold", thresh)
cv2.imshow("Closed", closed)
cv2.imshow("Opened", opened)
cv2.imshow("Arecanut Count", output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
