import cv2
from detector import detect_humans

cap = cv2.VideoCapture(0)

# Reduce resolution for speed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, count = detect_humans(frame)

    # Display total count
    cv2.putText(frame,
                f"Humans: {count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 3)

    cv2.imshow("YOLO Human Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
