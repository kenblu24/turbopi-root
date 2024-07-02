from ultralytics import YOLO

def find_ball(img):
    # Load a model
    model = YOLO("yolo_auxillary/yolov8s.pt")  # pretrained YOLOv8n model

    # # Run batched inference on a list of images
    # result = model("images/robopov.jpg")  # return a list of Results objects

    # Run inference on image
    model.predict(img, save=True, imgsz=320, conf=0.01, classes=[32])