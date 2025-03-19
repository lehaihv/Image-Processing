# Python code for Multiple Color Detection 


import numpy as np 
import cv2 


# Capturing video through webcam 
#webcam = cv2.VideoCapture(0) 
#########
# Open the default camera
cam = cv2.VideoCapture(0)

""" # Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height)) """

while True:
    ret, frame = cam.read()

    # Write the frame to the output file
    # out.write(frame)

    # Display the captured frame
    cv2.imshow('Camera', frame)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == ord('q'):
        # take image and save 
        # saving image in local storage 
        cv2.imwrite("Pics/GeeksForGeeks.png", frame) 
        break

# Release the capture and writer objects
cam.release()
#out.release()
cv2.destroyAllWindows()
#######

# Start a while loop 
while(1): 
    
    # Reading the video from the 
    # webcam in image frames 
    #_, imageFrame = webcam.read() 
    imageFrame = cv2.imread("Pics/GeeksForGeeks.png") #Multiple_obj.jpg Blue_pen.jpg pic_4.jpg

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
    num_objs = 0
    contours, hierarchy = cv2.findContours(blue_mask, 
                                        cv2.RETR_TREE, 
                                        cv2.CHAIN_APPROX_SIMPLE) 
    for pic, contour in enumerate(contours): 
        area = cv2.contourArea(contour) 
        if(4000 > area > 1000):     #300
            num_objs +=1
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
                        1.0, (0, 255, 0)) 
            print ("HSV : " ,hsv)
            print("Coordinates of pixel: X: ",x,"Y: ",y)
            """temp = hue_channel[0,0]/3 # + saturation_channel[0,0]        #int(value_channel[0])
            temp1 = saturation_channel[0,0]/3
            temp2 = value_channel[0,0]/3
            tempp = float(temp + temp1 + temp2) """
            print(f"{tempp}")
            
            #print(f"{temp1}")

    print("Number of objects:", num_objs)        
    # Program Termination 
    cv2.imshow("Multiple Color Detection in Real-TIme", imageFrame) 
    if cv2.waitKey(0): #(10) & 0xFF == ord('q'): 
        #webcam.release() 
        cv2.destroyAllWindows() 
        break
    