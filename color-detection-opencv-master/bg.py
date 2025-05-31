from rembg import new_session, remove
from PIL import Image

model_name = "u2net"
#"birefnet-general" 
#"birefnet-hrsod"
#"sam" 
#"isnet-general-use"
session = new_session(model_name)

def remove_background(input_path, output_path):
    """Removes background from an image and saves the result."""
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image, session=session, bgcolor=[128,128,128,255]) #bgcolor=[0,255,0,255]) #bgcolor=[128,128,128,255])best #bgcolor=[0,0,0,255]) #
        output_image.save(output_path)
        print(f"Background removed and saved to: {output_path}")
    except FileNotFoundError:
        print(f"Error: Input image not found at {input_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    input_image_path = "Pics/BG/24.jpg"  # Replace with your image path
    output_image_path = "Pics/BG/242.png" # Replace with your desired output path

    remove_background(input_image_path, output_image_path)
