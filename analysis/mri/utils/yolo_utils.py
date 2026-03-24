from ultralytics import YOLO
import os
import base64
from django.conf import settings

_yolo_model = None

def get_yolo_model():
    global _yolo_model
    if _yolo_model is None:
        model_path = os.path.join(settings.MEDIA_ROOT, 'model', 'best.pt')
        _yolo_model = YOLO(model_path)
    return _yolo_model

def yolo_inference(image_path):
    model = get_yolo_model()

    results = model(image_path)

    # Save annotated image
    annotated_path = image_path.replace('.jpg', '_annotated.jpg')
    results[0].save(filename=annotated_path)

    # Count detected boxes
    tumor_count = len(results[0].boxes)

    return annotated_path, tumor_count
