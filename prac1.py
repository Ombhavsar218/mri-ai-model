import cv2
import numpy as np

def draw_bounding_boxes(image, detections):
    """
    Draw bounding boxes with labels and confidence scores.
    
    Parameters:
        image (numpy array): The brain MRI image.
        detections (list of dict): List of detections with 'bbox', 'label', and 'confidence'.
                                   Example: [{'bbox': (x, y, w, h), 'label': 'tumor', 'confidence': 0.95}, ...]
    """
    for detection in detections:
        x, y, w, h = detection['bbox']
        label = detection['label']
        confidence = detection['confidence']

        # Draw the bounding box
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 165, 255), 2)

        # Create the label with confidence
        text = f"{label} {confidence:.2f}"
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(image, (x, y - text_height - 10), (x + text_width, y), (0, 165, 255), -1)
        cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return image

# Example usage:
image_path = "D:/Final Project/Brain_Tumor/Training/notumor/Tr-no_0026.jpg"
image = cv2.imread(image_path)

# Example detections
detections = [
    {"bbox": (100, 150, 80, 120), "label": "tumor", "confidence": 0.85},
    {"bbox": (200, 300, 60, 90), "label": "tumor", "confidence": 0.78},
]

# Draw bounding boxes
annotated_image = draw_bounding_boxes(image, detections)

# Save or display the image
cv2.imwrite("annotated_image.jpg", annotated_image)
cv2.imshow("Annotated Image", annotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
