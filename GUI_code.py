import pyrealsense2 as rs
import numpy as np
import cv2

# Initialize Intel RealSense pipeline
pipe = rs.pipeline()
cfg = rs.config()

# Configure streams (color and depth)
cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
pipe.start(cfg)

try:
    while True:
        # Wait for frames from the camera
        frames = pipe.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        # Ensure both frames are valid
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # Convert the color image to HSV format for color-based fruit detection
        hsv_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

        # Define HSV range for the color of the fruit (adjust for your target fruit)
        lower_red = np.array([0, 120, 70])
        upper_red = np.array([10, 255, 255])

        # Create a mask for the red color
        red_mask = cv2.inRange(hsv_image, lower_red, upper_red)

        # Morphological operations to remove noise
        kernel = np.ones((5, 5), np.uint8)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)
        red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)

        # Find contours from the mask
        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Loop through contours and detect fruits
        for contour in contours:
            # Get the area of the contour
            area = cv2.contourArea(contour)
            if area > 500:  # Threshold for filtering small objects (tune as needed)
                # Get the bounding box of the detected fruit
                x, y, w, h = cv2.boundingRect(contour)

                # Draw a rectangle around the detected fruit
                cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calculate the depth at the center of the fruit
                center_x = x + w // 2
                center_y = y + h // 2
                depth_value = depth_frame.get_distance(center_x, center_y)

                # Extract the region of interest (ROI) from the depth image for depth analysis
                depth_roi = depth_image[y:y+h, x:x+w]

                # Calculate statistical features from the depth ROI
                mean_depth = np.mean(depth_roi)
                max_depth = np.max(depth_roi)
                min_depth = np.min(depth_roi)

                # Display depth-related information on the image
                cv2.putText(color_image, f"Mean Depth: {mean_depth:.2f}m", (x, y - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(color_image, f"Max Depth: {max_depth:.2f}m", (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(color_image, f"Min Depth: {min_depth:.2f}m", (x, y - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Optional: Use depth features for classification (e.g., using simple rules)
                if mean_depth > 0.5:
                    fruit_type = "Large Fruit"
                else:
                    fruit_type = "Small Fruit"

                # Display the classification result
                cv2.putText(color_image, f"Type: {fruit_type}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Display the color and depth images
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        cv2.imshow('Color Image', color_image)
        cv2.imshow('Depth Image', depth_colormap)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop streaming
    pipe.stop()
    cv2.destroyAllWindows()
