import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import numpy as np 
import cv2 

# Global variable to store the file path
selected_file_path = ""

class FileDialogApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image File Selector')
        #self.setFixedSize(1200, 900)  # Set the size of the main window

        # Create buttons
        self.open_button = QPushButton('Open Image File', self)
        self.open_button.clicked.connect(self.open_file_dialog)

        self.cancel_button = QPushButton('Exit', self)
        self.cancel_button.clicked.connect(self.close_app)

        # Create a label to display the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image label

        # Create a text box to show the file path (multi-line)
        self.file_path_text_edit = QTextEdit(self)
        self.file_path_text_edit.setReadOnly(True)  # Make it read-only
        self.file_path_text_edit.setPlaceholderText("Selected file path will appear here...")
        self.file_path_text_edit.setFixedHeight(100)  # Set the height to 200 pixels

        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.file_path_text_edit)  # Add the text box to the layout
        layout.addWidget(self.open_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def open_file_dialog(self):
        global selected_file_path  # Declare the global variable
        # Clear the text box before loading a new image
        self.file_path_text_edit.clear()
        
        # Create the file dialog
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select an Image File")
        dialog.setNameFilter("Image Files (*.jpg *.jpeg *.png *.bmp *.gif)")

        # Open the dialog
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_file_path = dialog.selectedFiles()[0]  # Get the selected file path
            print(selected_file_path)
            # self.file_path_text_edit.setPlainText(selected_file_path)  # Display the file path in the text box
            self.file_path_text_edit.append(f"Selected: {selected_file_path}")  # Append the file path
            self.display_image(selected_file_path)  # Display the selected image
        else:
            print("No file selected.")

    def display_image(self, file_path):
        # Load and display the image in the QLabel
        ##############
        # Reading the video from the 
        # webcam in image frames 
        #_, imageFrame = webcam.read() 
        imageFrame = cv2.imread(file_path)  #"Pics/photo.jpg") #Multiple_obj.jpg Blue_pen.jpg pic_4.jpg

        # Convert the imageFrame in 
        # BGR(RGB color space) to 
        # HSV(hue-saturation-value) 
        # color space 
        hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV) 

        # Set range for red color and 
        # define mask 
        red_lower = np.array([136, 87, 111], np.uint8) 
        red_upper = np.array([180, 255, 255], np.uint8) 
        red_mask = cv2.inRange(hsvFrame, red_lower, red_upper) 

        # Set range for green color and 
        # define mask 
        green_lower = np.array([25, 52, 72], np.uint8) 
        green_upper = np.array([102, 255, 255], np.uint8) 
        green_mask = cv2.inRange(hsvFrame, green_lower, green_upper) 

        # Set range for blue color and 
        # define mask 
        blue_lower = np.array([94, 80, 2], np.uint8) 
        blue_upper = np.array([120, 255, 255], np.uint8) 
        blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper) 
        
        # Morphological Transform, Dilation 
        # for each color and bitwise_and operator 
        # between imageFrame and mask determines 
        # to detect only that particular color 
        kernel = np.ones((5, 5), "uint8") 
        
        # For red color 
        red_mask = cv2.dilate(red_mask, kernel)
        res_red = cv2.bitwise_and(imageFrame, imageFrame, 
                                mask = red_mask) 
        
        # For green color 
        green_mask = cv2.dilate(green_mask, kernel) 
        res_green = cv2.bitwise_and(imageFrame, imageFrame, 
                                    mask = green_mask) 
        
        # For blue color 
        blue_mask = cv2.dilate(blue_mask, kernel) 
        res_blue = cv2.bitwise_and(imageFrame, imageFrame, 
                                mask = blue_mask) 

        # Creating contour to track red color 
        """ contours, hierarchy = cv2.findContours(red_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 300): 
                x, y, w, h = cv2.boundingRect(contour) 
                imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                        (x + w, y + h), 
                                        (0, 0, 255), 2) 
                
                cv2.putText(imageFrame, "Red Colour", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, 
                            (0, 0, 255)) """     

        # Creating contour to track green color 
        """ contours, hierarchy = cv2.findContours(green_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(area > 300): 
                x, y, w, h = cv2.boundingRect(contour) 
                imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                        (x + w, y + h), 
                                        (0, 255, 0), 2) 
                
                cv2.putText(imageFrame, "Green Colour", (x, y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1.0, (0, 255, 0)) """ 

        # Creating contour to track blue color 
        num_objs_small = 0
        num_objs_large = 0
        contours, hierarchy = cv2.findContours(blue_mask, 
                                            cv2.RETR_TREE, 
                                            cv2.CHAIN_APPROX_SIMPLE) 
        for pic, contour in enumerate(contours): 
            area = cv2.contourArea(contour) 
            if(5000 > area > 1000):     #300
                num_objs_small +=1
                x, y, w, h = cv2.boundingRect(contour) 
                imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                        (x + w, y + h), 
                                        (255, 0, 0), 2) 
                # calculate coordinates of the center point of each contour cx, cy
                M = cv2.moments(contour)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                colorsB = imageFrame[cy,cx,0]
                colorsG = imageFrame[cy,cx,1]
                colorsR = imageFrame[cy,cx,2]
                colors = imageFrame[cy,cx,]
                hsv_value = np.uint8([[[colorsB ,colorsG,colorsR ]]])
                hsv = cv2.cvtColor(hsv_value,cv2.COLOR_BGR2HSV)
                # Access individual HSV values
                # Access the Hue channel
                hue_channel = hsv[:, :, 0]

                # Access the Saturation channel
                saturation_channel = hsv[:, :, 1]

                # Access the Value channel
                value_channel = hsv[:, :, 2]
                print("Hue:", hue_channel)
                print("Saturation:", saturation_channel)
                print("Value:", value_channel)
                temp = hue_channel[0,0]/3 # + saturation_channel[0,0]        #int(value_channel[0])
                temp1 = saturation_channel[0,0]/3
                temp2 = value_channel[0,0]/3
                tempp = float(temp + temp1 + temp2)
                #mea_value = f"{(hsv):.3f}"  #+avg_hsv[1]+avg_hsv[2]           
                cv2.putText(imageFrame, f"{(tempp):.3f}", (x, y), #"Blue Colour" mea_value str(x)str(hsv)
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1.0, (0, 255, 0), 2) 
                print ("HSV : " ,hsv)
                print("Coordinates of pixel: X: ",x,"Y: ",y)
                """temp = hue_channel[0,0]/3 # + saturation_channel[0,0]        #int(value_channel[0])
                temp1 = saturation_channel[0,0]/3
                temp2 = value_channel[0,0]/3
                tempp = float(temp + temp1 + temp2) """
                print(f"{tempp}")
                
                #print(f"{temp1}")
            elif (area > 6000):
                num_objs_large +=1
                x, y, w, h = cv2.boundingRect(contour) 
                imageFrame = cv2.rectangle(imageFrame, (x, y), 
                                        (x + w, y + h), 
                                        (255, 0, 0), 2) 
                # calculate coordinates of the center point of each contour cx, cy
                M = cv2.moments(contour)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                colorsB = imageFrame[cy,cx,0]
                colorsG = imageFrame[cy,cx,1]
                colorsR = imageFrame[cy,cx,2]
                colors = imageFrame[cy,cx,]
                hsv_value = np.uint8([[[colorsB ,colorsG,colorsR ]]])
                hsv = cv2.cvtColor(hsv_value,cv2.COLOR_BGR2HSV)
                # Access individual HSV values
                # Access the Hue channel
                hue_channel = hsv[:, :, 0]

                # Access the Saturation channel
                saturation_channel = hsv[:, :, 1]

                # Access the Value channel
                value_channel = hsv[:, :, 2]
                print("Hue:", hue_channel)
                print("Saturation:", saturation_channel)
                print("Value:", value_channel)
                temp = hue_channel[0,0]/3 # + saturation_channel[0,0]        #int(value_channel[0])
                temp1 = saturation_channel[0,0]/3
                temp2 = value_channel[0,0]/3
                tempp = float(temp + temp1 + temp2)
                #mea_value = f"{(hsv):.3f}"  #+avg_hsv[1]+avg_hsv[2]           
                cv2.putText(imageFrame, f"{(tempp):.3f}", (x, y), #"Blue Colour" mea_value str(x)str(hsv)
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            1.0, (0, 255, 0), 2) 
                print ("HSV : " ,hsv)
                print("Coordinates of pixel: X: ",x,"Y: ",y)

        print("Number of all objects:", num_objs_small + num_objs_large)
        print("Number of small objects:", num_objs_small)
        print("Number of large objects:", num_objs_large)
        self.append_text("Number of all objects: " + str(num_objs_small + num_objs_large))
        self.append_text("Number of small objects: " + str(num_objs_small))
        self.append_text("Number of large objects:" + str(num_objs_large))


        # Program Termination 
        # cv2.namedWindow(800,400)
        # cv2.imshow("Multiple Color Detection in Real-TIme", imageFrame) 
        ##############
        #pixmap = QPixmap(imageFrame) #file_path)  # Load the image
        #self.image_label.setPixmap(pixmap.scaled(1200, 800, Qt.AspectRatioMode.KeepAspectRatio))  # Scale the image
         # Convert the NumPy array (RGB format) to QImage
        imageFrame_rgb = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2RGB) 
        print(imageFrame.shape[2]) 
        height, width, channel = imageFrame_rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(imageFrame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

        # Display the QImage in the QLabel
        self.image_label.setPixmap(QPixmap.fromImage(q_image).scaled(1200, 800, Qt.AspectRatioMode.KeepAspectRatio))

    def append_text(self, text):
        """Method to append text to the QTextEdit."""
        self.file_path_text_edit.append(text)

    def close_app(self):
        self.close()  # Close the application

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileDialogApp()
    # in Linux
    #window.show()
    #window.setWindowState(Qt.WindowState.WindowFullScreen)
    # in windows
    window.showFullScreen()  # in windows
    sys.exit(app.exec())