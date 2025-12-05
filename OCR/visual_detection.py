import cv2
import numpy as np
import onnxruntime as ort
import time
import os
import sys

def load_onnx_model(onnx_path):
    """Load ONNX model and return session"""
    if not os.path.exists(onnx_path):
        print(f"❌ ONNX model not found: {onnx_path}")
        return None
    
    try:
        session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        print(f"✅ ONNX model loaded: {onnx_path}")
        return session
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def preprocess_image(image, target_size=(640, 640)):
    """Preprocess image for ONNX model"""
    # Resize
    resized = cv2.resize(image, target_size)
    
    # BGR to RGB
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    
    # Normalize
    normalized = rgb.astype(np.float32) / 255.0
    
    # Transpose to CHW and add batch dimension
    input_tensor = np.transpose(normalized, (2, 0, 1))[None, :, :, :]
    
    return input_tensor

def postprocess_yolo_output(outputs, original_shape, conf_threshold=0.25):
    """Postprocess YOLO ONNX outputs"""
    predictions = outputs[0]  # (1, 84, 8400)
    predictions = np.transpose(predictions, (0, 2, 1))[0]  # (8400, 84)
    
    # Extract boxes and scores
    boxes = predictions[:, :4]  # (8400, 4)
    scores = predictions[:, 4:]  # (8400, 80)
    
    # Get class with highest confidence
    class_ids = np.argmax(scores, axis=1)
    confidences = np.max(scores, axis=1)
    
    # Filter by confidence
    mask = confidences > conf_threshold
    boxes = boxes[mask]
    confidences = confidences[mask]
    class_ids = class_ids[mask]
    
    if len(boxes) == 0:
        return []
    
    # Convert center format to corner format
    x_center, y_center, width, height = boxes.T
    x1 = x_center - width / 2
    y1 = y_center - height / 2
    x2 = x_center + width / 2
    y2 = y_center + height / 2
    
    # Scale to original image size
    h, w = original_shape[:2]
    x1 *= w
    y1 *= h
    x2 *= w
    y2 *= h
    
    # Apply NMS
    indices = cv2.dnn.NMSBoxes(
        boxes.tolist(), 
        confidences.tolist(), 
        conf_threshold, 
        0.45
    )
    
    detections = []
    if len(indices) > 0:
        indices = indices.flatten()
        for idx in indices:
            detections.append([
                x1[idx], y1[idx], x2[idx], y2[idx],
                confidences[idx], class_ids[idx]
            ])
    
    return detections

def draw_detections(image, detections):
    """Draw detections on image with very visible styling"""
    result = image.copy()
    
    # COCO class names
    class_names = [
        'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
        'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
        'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
        'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
        'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
        'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
        'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
        'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
    ]
    
    for detection in detections:
        x1, y1, x2, y2, confidence, class_id = detection
        
        # Convert to integers
        x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
        class_id = int(class_id)
        
        # Get class name
        class_name = class_names[class_id] if class_id < len(class_names) else f"class_{class_id}"
        
        # Very visible colors (bright and contrasting)
        if class_id == 0:  # person
            color = (0, 255, 0)  # Bright green
        elif class_id == 39:  # bottle
            color = (255, 0, 0)  # Bright red
        elif class_id == 67:  # cell phone
            color = (0, 0, 255)  # Bright blue
        elif class_id == 56:  # chair
            color = (255, 255, 0)  # Bright yellow
        else:
            color = (255, 0, 255)  # Bright magenta
        
        # Draw very thick bounding box
        cv2.rectangle(result, (x1, y1), (x2, y2), color, 5)
        
        # Draw label with very visible background
        label = f"{class_name}: {confidence:.2f}"
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)
        
        # Draw label background
        cv2.rectangle(result, (x1, y1 - text_height - 20), (x1 + text_width + 10, y1), color, -1)
        
        # Draw label text
        cv2.putText(result, label, (x1 + 5, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
        
        # Print detection info to console
        print(f"🔍 VISUAL: {class_name} at ({x1},{y1})-({x2},{y2}) with confidence {confidence:.2f}")
    
    return result

def test_display():
    """Test if display is working"""
    print("🔍 Testing display capabilities...")
    
    # Create a test image
    test_img = np.zeros((480, 640, 3), dtype=np.uint8)
    test_img[:] = (100, 100, 100)  # Gray background
    
    # Add some text
    cv2.putText(test_img, "DISPLAY TEST", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(test_img, "Press any key to continue", (150, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Try to show the test image
    cv2.imshow("Display Test", test_img)
    
    print("👀 Look for a window titled 'Display Test'")
    print("💡 If you don't see it, try:")
    print("   - Alt+Tab to switch windows")
    print("   - Check your taskbar")
    print("   - Try pressing any key to continue")
    
    key = cv2.waitKey(0) & 0xFF
    cv2.destroyAllWindows()
    
    if key != 255:
        print("✅ Display test successful!")
        return True
    else:
        print("❌ Display test failed - no key pressed")
        return False

def main():
    """Main function with enhanced visual debugging"""
    print("🚀 Starting VISUAL ONNX Camera Detection")
    print("=" * 50)
    
    # Test display first
    if not test_display():
        print("❌ Display test failed. Trying alternative methods...")
    
    # Default ONNX path
    default_onnx_path = "/home/sonny/Documents/GitHub/Image-Processing/runs/detect/train2/weights/best.onnx"
    
    # Get ONNX path from command line or use default
    onnx_path = sys.argv[1] if len(sys.argv) > 1 else default_onnx_path
    
    print(f"🔍 Looking for ONNX model: {onnx_path}")
    
    # Load model
    session = load_onnx_model(onnx_path)
    if session is None:
        return
    
    # Get input info
    input_name = session.get_inputs()[0].name
    output_names = [output.name for output in session.get_outputs()]
    
    print(f"📊 Model input: {input_name}")
    print(f"📊 Model outputs: {output_names}")
    
    # Initialize camera
    print("🎥 Initializing camera...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("❌ Could not open camera")
        return
    
    print("✅ Camera initialized successfully")
    print("🎮 Controls: 'q' = quit, 's' = save screenshot")
    print("👀 Look for the camera window to appear...")
    print("💡 If you don't see the window, try Alt+Tab or check your taskbar")
    
    # Performance tracking
    frame_count = 0
    start_time = time.time()
    detection_count = 0
    
    # Force window creation
    cv2.namedWindow("VISUAL Object Detection", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("VISUAL Object Detection", 1280, 720)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Could not read frame")
                break
            
            print(f"📸 Processing frame {frame_count + 1}...")
            
            # Preprocess
            input_tensor = preprocess_image(frame)
            
            # Inference
            outputs = session.run(output_names, {input_name: input_tensor})
            
            # Postprocess
            detections = postprocess_yolo_output(outputs, frame.shape, conf_threshold=0.25)
            
            # Update detection count
            if len(detections) > 0:
                detection_count += len(detections)
                print(f"🎯 Found {len(detections)} objects in this frame!")
            
            # Draw results
            result_frame = draw_detections(frame, detections)
            
            # Add very visible status text
            cv2.putText(result_frame, "LIVE DETECTION ACTIVE", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            cv2.putText(result_frame, f"Frame: {frame_count}", (10, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(result_frame, f"Detections: {len(detections)}", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(result_frame, f"Total: {detection_count}", (10, 160), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Calculate FPS
            frame_count += 1
            if frame_count % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - start_time)
                start_time = current_time
                cv2.putText(result_frame, f"FPS: {fps:.1f}", (10, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display with forced window
            cv2.imshow("VISUAL Object Detection", result_frame)
            
            # Check if window is visible
            window_visible = cv2.getWindowProperty("VISUAL Object Detection", cv2.WND_PROP_VISIBLE)
            if window_visible < 1:
                print("⚠️  Warning: Detection window may not be visible")
                print("💡 Try Alt+Tab or check your taskbar for 'VISUAL Object Detection'")
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("👋 Quitting detection...")
                break
            elif key == ord('s'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"visual_detection_{timestamp}.jpg"
                cv2.imwrite(filename, result_frame)
                print(f"📸 Screenshot saved: {filename}")
            elif key != 255:
                print(f"🔑 Key pressed: {key}")
    
    except KeyboardInterrupt:
        print("⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error during detection: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"📊 Final stats: {frame_count} frames processed, {detection_count} total detections")
        print("👋 Detection stopped")

if __name__ == "__main__":
    main()



