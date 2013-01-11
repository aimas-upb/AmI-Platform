import cv

def face_detect(image):
    """ Detects whether in the given image (PIL image) there are any faces
        or not using the OpenCV Haar cascade detector. """
    
    # Save the PIL image to disk and re-load it into IplImage format for
    # OpenCV. I know this is a terrible hack but we can take care of this 
    # as an in-memory conversion later.
    from files import random_file_name
    temp_file = random_file_name('jpg')
    image.save(temp_file)
    opencv_image = cv.LoadImage(temp_file, cv.CV_LOAD_IMAGE_COLOR)
    
    # Load the data structure for Haar Cascade detector in memory
    haar_cascade = cv.Load('/home/ami/AmI-Platform/resources/haarcascade_frontalface_default.xml')
    
    # Even though the face detector from OpenCV has been trained on 20 x 20,
    # sending 20 x 20 images for face recognition to the BetaFace API
    # will result in nothing useful.
    min_size = (100, 100)
    faces = cv.HaarDetectObjects(opencv_image,
                                 haar_cascade, 
                                 cv.CreateMemStorage(),
                                 min_size = min_size)
    
    return faces