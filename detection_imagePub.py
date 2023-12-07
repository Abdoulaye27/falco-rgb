from julia.api import Julia
jl = Julia(compiled_modules=False)

# Load your Julia functions
jl.eval('include("falco_function.jl")')

# Initialize belief using Julia's initialize_belief()
belief = jl.eval("reset_belief()")

from cProfile import label

# The following script imports the ObjectDetection class
from imageai.Detection import ObjectDetection

# Import the message publisher function
#from objectInfomessagePublisher import messagePublisher2 
from image_messagePublisher import publish_image

import cv2
# The script below creates an object of the object detection class.
obj_detect = ObjectDetection()

# The next step is to set the model type for object detection. Since we’ll be using the YOLO algorithm, you need to call the setModelTypeAsYOLOv3() method as shown in the script below:
obj_detect.setModelTypeAsYOLOv3()

# The next step is to load the actual Yolo model. The Yolo model the imageai library uses for object detection is available at the following Github Link: https://bit.ly/2UqlRGD
# To load the model, first you need to call the setModelPath() method from your ObjectDetection class object and pass it the path where you downloaded the yolo.h5 model. 
# Next, you need to call the loadModel() method to actually load the model. Look at the following script for reference:
obj_detect.setModelPath(r"/home/walle/COHRINT/yolo.h5")
obj_detect.loadModel()

# The next step is to capture your webcam stream. To do so, execute the script below:
cam_feed = cv2.VideoCapture(0)
#cam_feed = cv2.VideoCapture("rtsp://rinao:unicorn@192.168.1.5:8554/streaming/live/1")

# Next, you need to define height and width for the frame that will display the detected objects from your live feed. 
# Execute the following script to do so, recognizing you can change the integer values near the end to match your desired dimensions:
cam_feed.set(cv2.CAP_PROP_FRAME_WIDTH, 650)
cam_feed.set(cv2.CAP_PROP_FRAME_HEIGHT, 750)

#obj2 = ImagePublisher()
#obj1 = messagePublisher2()

count_frame = 0
while True:    
    # Reads the next frame captured by the camera
    ret, img = cam_feed.read()   

    count_frame += 1
    if count_frame %5==0:
      # This function outputs the annote_image and a dictionnary of the detected object containing its name, percentage probability, and bounding boxes dimensions
      annotated_image, preds = obj_detect.detectObjectsFromImage(input_image=img,
                      input_type="array",
                        output_type="array",
                        display_percentage_probability=True,
                        display_object_name=True)
      
      cv2.imshow("", annotated_image)
      if preds and preds[0]:
        dict_obj = preds[0]
        cs = dict_obj['percentage_probability']
        target = dict_obj['name']
        print('Confidence score is {}'.format(cs))
        print('Detected target is {}'.format(target))
        #print(belief)
        if cs is None:
          cs = 0
        action, belief = jl.eval(f"generate_action({cs})") 
        if action == 1:
          print('ALERT OPERATOR!')
        if action == 2:
          print('GATHER INFORMATION!')
        if action == 3:
          print('CONTINUE MISSION!')
        print("----------------------------------------------------")
      else:
        print("No objects detected in the current frame.")
        print("----------------------------------------------------")
    # Publish the message (detected object dictionnary)
    #obj1.message_publisher2(preds)
    #obj2.publish_image(annotated_image)
    #publish_image(annotated_image)
    #publish_image(img)
    # Display the current frame containing our detected objects
    #cv2.imshow("", img)

    # To stop the program, press "q" or "ESC"
    if (cv2.waitKey(1) & 0xFF == ord("q")) or (cv2.waitKey(1)==27):
        break
    

cam_feed.release()
cv2.destroyAllWindows()
