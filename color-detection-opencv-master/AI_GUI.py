import cv2
import numpy as np
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

def detect_blue_objects(img_path):
    image = cv2.imread(img_path)
    if image is None:
        return None, 0, 0

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    small_count = 0
    large_count = 0

    for contour in contours:
        if cv2.contourArea(contour) > 500:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            size_text = f"{w}x{h}px"
            cv2.putText(image, size_text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            if w < 150:
                small_count += 1
            else:
                large_count += 1

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb), small_count, large_count

def open_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    result_img, small, large = detect_blue_objects(file_path)
    if result_img is None:
        result_label.config(text="Failed to load image.")
        return

    # Resize for display
    result_img = result_img.resize((500, 400), Image.ANTIALIAS)
    tk_image = ImageTk.PhotoImage(result_img)
    image_label.config(image=tk_image)
    image_label.image = tk_image

    # Update text box with counts
    result_text.set(f"Small objects: {small}\nLarge objects: {large}")

def exit_program():
    root.destroy()

# GUI setup
root = Tk()
root.title("Blue Object Detector")

# Buttons
open_btn = Button(root, text="Open Image", command=open_image, width=20, bg="lightblue")
open_btn.grid(row=0, column=0, padx=10, pady=10)

exit_btn = Button(root, text="Exit", command=exit_program, width=20, bg="lightcoral")
exit_btn.grid(row=0, column=1, padx=10, pady=10)

# Text box
result_text = StringVar()
result_entry = Label(root, textvariable=result_text, width=30, height=4, relief="sunken", anchor="nw", justify=LEFT)
result_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Image display
image_label = Label(root, bg="gray", width=500, height=400)
image_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
