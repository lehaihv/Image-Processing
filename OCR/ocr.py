from PIL import Image
import pytesseract

# Load an image
img = Image.open('p1.png')

# Extract text from image
#text = pytesseract.image_to_string(img)
text = pytesseract.image_to_boxes(img)

print(text)
