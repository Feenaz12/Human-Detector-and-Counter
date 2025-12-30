import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

def detect_humans(frame):
    results = model(frame, conf=0.3)
    count = 0

    for r in results:
        for box in r.boxes:
            if int(box.cls[0]) == 0:
                count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])

                cv2.rectangle(frame, (x1, y1), (x2, y2),
                              (0, 255, 0), 2)
                cv2.putText(frame, f"Person {conf:.2f}",
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 0), 2)

    return frame, count
