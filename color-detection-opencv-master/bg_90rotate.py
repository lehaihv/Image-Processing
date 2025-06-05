from rembg import new_session, remove
from PIL import Image
import os

model_name = "u2net"
session = new_session(model_name)

def remove_background(input_path, output_path):
    """Rotates image 90° clockwise, removes background, and saves the result."""
    try:
        input_image = Image.open(input_path)

        # Rotate 90 degrees clockwise
        rotated_image = input_image.rotate(90, expand=True) #-90

        # Remove background
        output_image = remove(rotated_image, session=session, bgcolor=[128, 128, 128, 255])

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save output
        output_image.save(output_path)
        print(f"Rotated, background removed, and saved to: {output_path}")
    except FileNotFoundError:
        print(f"Error: Input image not found at {input_path}")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    input_image_path = "Pics/BG/1/2.jpg"
    output_image_path = "Pics/BG/1/2a.png"
    remove_background(input_image_path, output_image_path)
