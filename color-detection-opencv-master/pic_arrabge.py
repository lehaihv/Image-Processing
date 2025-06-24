import os
from tkinter import Tk, filedialog
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Function to browse and load multiple images
def browse_images():
    root = Tk()
    root.withdraw()  # Hide the Tkinter root window
    file_paths = filedialog.askopenfilenames(
        title="Select Images", 
        filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"), ("All files", "*.*"))
    )
    return root.tk.splitlist(file_paths)

# Function to create the PDF with images arranged as a 3-column table
def create_pdf(image_paths, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter  # Letter size (8.5 x 11 inches)
    
    # Table layout variables
    x_margin = 40
    y_margin = height - 40
    cell_width = (width - 2 * x_margin) / 3  # 3 columns
    cell_height = 200  # Set fixed height per row
    max_rows_per_page = (height - 2 * y_margin) // cell_height  # Dynamic number of rows per page
    
    # Initialize coordinates
    x_pos = x_margin
    y_pos = y_margin
    
    # Iterate through the images
    for idx, image_path in enumerate(image_paths):
        img = Image.open(image_path)
        img_width, img_height = img.size

        # Resize image to fit within the cell
        aspect_ratio = img_width / img_height
        new_width = cell_width
        new_height = new_width / aspect_ratio
        if new_height > cell_height:
            new_height = cell_height
            new_width = new_height * aspect_ratio

        # Insert the image into the cell
        c.drawImage(image_path, x_pos, y_pos - new_height, width=new_width, height=new_height)

        # Move to the next column
        x_pos += cell_width

        # Move to the next row after 3 columns
        if (idx + 1) % 3 == 0:
            x_pos = x_margin
            y_pos -= cell_height

        # Add a new page if we're out of space (based on max_rows_per_page)
        if (idx + 1) % (max_rows_per_page * 3) == 0:  # 3 images per row, max rows per page
            c.showPage()  # Create a new page
            y_pos = height - 40  # Reset Y position for the new page

    c.save()

# Main function to browse images and create PDF
def main():
    images = browse_images()
    if images:
        output_pdf = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if output_pdf:
            create_pdf(images, output_pdf)
            print(f"PDF created successfully: {output_pdf}")
        else:
            print("No output file selected.")
    else:
        print("No images selected.")

if __name__ == "__main__":
    main()
