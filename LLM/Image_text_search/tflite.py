import tensorflow as tf
import numpy as np
from PIL import Image, ImageDraw

# Load TFLite model and allocate tensors
interpreter = tf.lite.Interpreter(model_path="ssd_mobilenet_v2_coco.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print("Input details:", input_details)
print("Output details:", output_details)    

# Load and preprocess image
img = Image.open("data/girl_2.jpg").convert("RGB").resize((300, 300))
input_data = np.expand_dims(np.array(img, dtype=np.uint8), axis=0)

# Set input tensor
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()

# Get output tensors
boxes = interpreter.get_tensor(output_details[0]['index'])[0]        # Bounding box coordinates of detected objects
classes = interpreter.get_tensor(output_details[1]['index'])[0]      # Class index of detected objects
scores = interpreter.get_tensor(output_details[2]['index'])[0]       # Confidence of detected objects

# Load COCO labels
with open("coco_labels.txt", "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Draw bounding boxes for detected persons
image_orig = Image.open("data/girl_2.jpg").convert("RGB")
draw = ImageDraw.Draw(image_orig)
im_width, im_height = image_orig.size

print("Detected persons:")
for i in range(len(scores)):
    if scores[i] > 0.5 and labels[int(classes[i])] == "person":
        ymin, xmin, ymax, xmax = boxes[i]
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                      ymin * im_height, ymax * im_height)
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        print(f"Person {i+1}: Score={scores[i]:.2f}, Box=({int(left)}, {int(top)}, {int(right)}, {int(bottom)})")

# Save or show the result
image_orig.save("detected_persons.jpg")
print("Detection results saved to detected_persons.jpg")