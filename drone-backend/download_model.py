from ultralytics import YOLO

print("Downloading YOLOv8n model...")
model = YOLO('yolov8n.pt')
print("Model downloaded successfully!")
print(f"Model saved at: {model.ckpt_path}")