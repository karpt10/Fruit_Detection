import sys
import cv2
import numpy as np
import pyrealsense2 as rs
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QGridLayout, QWidget, QFileDialog, QMessageBox, QTabWidget, QVBoxLayout, QHBoxLayout, QFrame, QGroupBox, QScrollArea
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont

class FruitDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fruit Analysis and Defect Detection")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet("background-color: #f0f0f5; font-family: Arial;")

        # RealSense camera setup
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        try:
            self.pipeline.start(self.config)
        except Exception as e:
            self.display_error(f"RealSense camera not connected: {e}")
            sys.exit()

        # Create labels with full size to prevent cropping
        self.live_feed_label = QLabel("Live Feed", self)
        self.live_feed_label.setFixedSize(640, 480)
        self.live_feed_label.setFrameShape(QFrame.Box)
        self.live_feed_label.setStyleSheet("background-color: #000; color: #fff; font-weight: bold; padding: 5px;")

        self.depth_feed_label = QLabel("Depth Feed", self)
        self.depth_feed_label.setFixedSize(640, 480)
        self.depth_feed_label.setFrameShape(QFrame.Box)
        self.depth_feed_label.setStyleSheet("background-color: #000; color: #fff; font-weight: bold; padding: 5px;")

        self.capture_button = QPushButton("Capture and Analyze")
        self.capture_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.capture_button.clicked.connect(self.capture_image)

        self.load_button = QPushButton("Load Image from File")
        self.load_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        self.load_button.clicked.connect(self.load_image)

        self.analysis_text = QTextEdit("Detailed Analysis:\n", self)
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setFont(QFont("Arial", 10))
        self.analysis_text.setStyleSheet("background-color: #f9f9f9; color: #333; padding: 5px; border: 1px solid #ccc;")

        # Labels for analysis images with full size
        self.threshold_label = QLabel("Threshold Image", self)
        self.threshold_label.setFixedSize(640, 480)
        self.threshold_label.setFrameShape(QFrame.Box)
        self.threshold_label.setStyleSheet("background-color: #ddd; color: #555; font-weight: bold; padding: 5px;")

        self.final_output_label = QLabel("Final Output", self)
        self.final_output_label.setFixedSize(640, 480)
        self.final_output_label.setFrameShape(QFrame.Box)
        self.final_output_label.setStyleSheet("background-color: #ddd; color: #555; font-weight: bold; padding: 5px;")

        self.count_output_label = QLabel("Count Output Image", self)
        self.count_output_label.setFixedSize(640, 480)
        self.count_output_label.setFrameShape(QFrame.Box)
        self.count_output_label.setStyleSheet("background-color: #ddd; color: #555; font-weight: bold; padding: 5px;")

        self.defective_depth_label = QLabel("Defective Depth Image", self)
        self.defective_depth_label.setFixedSize(640, 480)
        self.defective_depth_label.setFrameShape(QFrame.Box)
        self.defective_depth_label.setStyleSheet("background-color: #ddd; color: #555; font-weight: bold; padding: 5px;")

        # Tabs for organizing screens
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.tab_live_feed = QWidget()
        self.tab_analysis = QWidget()
        self.tab_reports = QWidget()
        self.tabs.addTab(self.tab_live_feed, "Live Feed")
        self.tabs.addTab(self.tab_analysis, "Analysis")
        self.tabs.addTab(self.tab_reports, "Reports")

        # Live Feed tab layout with scroll area for better view
        live_feed_layout = QGridLayout()
        live_feed_layout.addWidget(self.live_feed_label, 0, 0, 1, 2)
        live_feed_layout.addWidget(self.depth_feed_label, 0, 2, 1, 2)
        live_feed_layout.addWidget(self.capture_button, 1, 1)
        live_feed_layout.addWidget(self.load_button, 1, 2)
        self.tab_live_feed.setLayout(live_feed_layout)

        # Analysis tab layout
        analysis_layout = QVBoxLayout()
        analysis_group = QGroupBox("Analysis")
        analysis_group.setStyleSheet("font-weight: bold; padding: 10px;")
        analysis_layout.addWidget(self.analysis_text)
        analysis_group.setLayout(analysis_layout)

        images_layout = QGridLayout()
        images_layout.addWidget(self.threshold_label, 0, 0)
        images_layout.addWidget(self.final_output_label, 0, 1)
        images_layout.addWidget(self.count_output_label, 1, 0)
        images_layout.addWidget(self.defective_depth_label, 1, 1)
        self.tab_analysis.setLayout(images_layout)

        # Reports tab layout
        reports_layout = QVBoxLayout()
        reports_layout.addWidget(QLabel("Reports & Summaries"))
        reports_layout.addWidget(self.analysis_text)
        self.tab_reports.setLayout(reports_layout)

        # Timer for live feed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    # The rest of your methods remain unchanged.



    def update_frame(self):
        # Wait for a frame and retrieve the color and depth frames
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        if not color_frame or not depth_frame:
            return  # Skip this frame if something goes wrong

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert color image to QImage for display
        image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_image = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Resize image based on label size
        resize_percentage = min(self.live_feed_label.width() / w, self.live_feed_label.height() / h) * 100
        self.display_image(self.live_feed_label, image, resize_percentage)

        # Convert depth image to grayscale for display
        depth_image = cv2.convertScaleAbs(depth_image, alpha=0.03)  # Adjust alpha for better visibility
        depth_image_color = cv2.cvtColor(depth_image, cv2.COLOR_GRAY2RGB)
        depth_image_rgb = cv2.cvtColor(depth_image_color, cv2.COLOR_BGR2RGB)
        qt_depth_image = QImage(depth_image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Resize depth image based on label size
        self.display_image(self.depth_feed_label, depth_image_rgb, resize_percentage)

    def capture_image(self):
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        if not color_frame or not depth_frame:
            self.display_error("Failed to capture frames.")
            return

        color_image = np.asanyarray(color_frame.get_data())

        # Process image for fruit counting and labeling
        threshold_image, labeled_image, fruit_count = self.process_and_label_fruits(color_image)

        # Perform faulty detection (circle detection)
        faulty_image, faulty_count = self.detect_faulty_fruits(color_image)
        faulty_depth_image = self.detect_faulty_depth(depth_frame)

        # Display the thresholded image with numbering on it
        self.display_image(self.threshold_label, threshold_image)

        # Display the final output image with contours and faulty fruits
        self.display_image(self.final_output_label, faulty_image)

        # Display the count output image with fruit count overlay
        self.display_image(self.count_output_label, labeled_image)

        # Display the defective depth image
        self.display_image(self.defective_depth_label, faulty_depth_image)

        # Update the overall report with the count
        self.update_overall_report(fruit_count, faulty_count)

    def load_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select an Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if filename:
            color_image = cv2.imread(filename)

            # Process image for fruit counting and labeling
            threshold_image, labeled_image, fruit_count = self.process_and_label_fruits(color_image)

            # Perform faulty detection (circle detection)
            faulty_image, faulty_count = self.detect_faulty_fruits(color_image)

            # Display the thresholded image with numbering on it
            self.display_image(self.threshold_label, threshold_image)

            # Display the final output image with contours and faulty fruits
            self.display_image(self.final_output_label, faulty_image)

            # Display the count output image with fruit count overlay
            self.display_image(self.count_output_label, labeled_image)

            # Display the defective depth image
            self.display_image(self.defective_depth_label, faulty_image)

            # Update the overall report with the count
            self.update_overall_report(fruit_count, faulty_count)

    def process_and_label_fruits(self, color_image):
        # Convert to grayscale
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        # Apply a threshold to create a binary image
        _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Define a kernel for morphological operations
        kernel = np.ones((3, 3), np.uint8)

        # Apply closing to close small gaps within objects
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Apply opening to separate overlapping objects
        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

        # Find contours on the processed binary image
        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Count the contours, assuming each contour is a fruit
        fruit_count = len(contours)
        print(f"Total fruits counted: {fruit_count}")

        # Copy the threshold image for labeling (apply numbering on threshold)
        threshold_with_numbers = np.copy(thresh)

        # Loop through each contour and add a number on the threshold image
        for i, contour in enumerate(contours):
            # Get the center of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.putText(threshold_with_numbers, str(i + 1), (cX - 10, cY - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Return processed image and count
        return threshold_with_numbers, color_image, fruit_count

    def detect_faulty_fruits(self, color_image):
        # Detect faulty fruits (example using circle detection)
        gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)

        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 30, param1=50, param2=30, minRadius=10, maxRadius=60)

        faulty_image = np.copy(color_image)
        faulty_count = 0

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center = (i[0], i[1])
                radius = i[2]
                cv2.circle(faulty_image, center, radius, (0, 255, 0), 2)  # Draw circle
                cv2.rectangle(faulty_image, (center[0] - 5, center[1] - 5), (center[0] + 5, center[1] + 5), (0, 0, 255), 3)  # Draw center

                faulty_count += 1

        return faulty_image, faulty_count

    def detect_faulty_depth(self, depth_frame):
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_image_colored = cv2.convertScaleAbs(depth_image, alpha=0.03)
        return depth_image_colored

    def update_overall_report(self, fruit_count, faulty_count):
        self.analysis_text.append(f"Total Fruits Counted: {fruit_count}")
        self.analysis_text.append(f"Faulty Fruits Detected: {faulty_count}")

    def display_image(self, label, image, resize_percentage=100):
        """Converts the OpenCV image to QImage, resizes it, and sets it to the given QLabel."""
        # Resize image based on the percentage
        resized_image = self.resize_image(image, resize_percentage)
        
        # Convert the resized image to RGB
        image_rgb = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        
        # Get the new dimensions after resizing
        h, w, ch = image_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(image_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Set the QImage to QLabel
        label.setPixmap(QPixmap.fromImage(qt_image))

    def resize_image(self, image, percentage=100):
        """Resize the image based on the percentage."""
        width = int(image.shape[1] * percentage / 100)
        height = int(image.shape[0] * percentage / 100)
        resized_image = cv2.resize(image, (width, height))
        return resized_image

    def display_error(self, message):
        """Display an error message in a message box."""
        QMessageBox.critical(self, "Error", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FruitDetectionApp()
    window.show()
    sys.exit(app.exec_())