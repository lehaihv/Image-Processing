import cv2
import pytesseract
import numpy as np
from ultralytics import YOLO

# -----------------------------
# Load pre-trained YOLOv8n model
# -----------------------------
# This model is general-purpose; for text detection, you can use a text-detection dataset if available.
model = YOLO("yolov8n.pt")  # nano model for speed

# -----------------------------
# OCR function
# -----------------------------
def ocr_crop(image, box):
    """
    Crop the detected box and run OCR.
    box: [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = map(int, box)
    crop = image[y1:y2, x1:x2]
    text = pytesseract.image_to_string(crop, config='--psm 6')
    return text.strip()

# -----------------------------
# Start live camera feed
# -----------------------------
cap = cv2.VideoCapture(0)  # 0 = default webcam
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLO inference with CPU
    results = model(frame, device='cpu')[0]  # Force CPU usage
    boxes = results.boxes.xyxy.cpu().numpy()  # Bounding boxes [x1, y1, x2, y2]
    scores = results.boxes.conf.cpu().numpy()
    class_ids = results.boxes.cls.cpu().numpy()

    for box, score, class_id in zip(boxes, scores, class_ids):
        if score < 0.3:
            continue

        # Run OCR on the detected region
        text = ocr_crop(frame, box)
        x1, y1, x2, y2 = map(int, box)

        # Draw bounding box and OCR text
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    # Display live feed
    cv2.imshow("YOLO + OCR Live", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
