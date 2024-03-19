import cv2
import numpy as np
import time
import matplotlib.image as mpimg
from imgdetect import convertImgtoArray

## HELPFUL COPY / PASTES ##
## TEST / DEBUG ##
## PASSING image variable as save / load file
#from debugging import saveImage
#saveImage(image, 'logs/passing/')
    
## PASSING image variable as save / load file with MP
# from debugging import saveImageMP
# saveImageMP (image, 'logs/passing/')

## VIEWING array as image
# from debugging import viewArray
# viewArray(image, 'descriptive_title_here')

def getfiletitle ():
    """Get filename / file title (for debugging)"""
    return 'test-' + str((int(round(time.time(),2)*100)))[-8:-1]

def viewArray (image_obj, title='Title'):
    """View array as image (temp)"""
    cv2.imshow(title, image_obj)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def blurshrinkImgArray (image):
    """Blur and shrink image"""
    # If image is not numpy array, convert it
    if not isinstance(image, np.ndarray):
        image = convertImgtoArray(image)
    image = cv2.blur(image, (20,20)) # blur image
    image = cv2.resize(image, (0,0), fx=0.2, fy=0.2) 
    return image

def saveArrayasImgCensored (image, filename='', filename_prefix='', filename_suffix='-censored', detections=[], classes=[], small=False, includeuncensored=False):
    """Save array as image (temp) after censoring"""

    if not filename:
        ftitle = getfiletitle()
        filename = filename_prefix + ftitle + filename_suffix + '.jpg'

    if not detections: # if no detections, just save image (no censoring, don't pass on suffix)
        filenameuncensored = filename_prefix + ftitle + '.jpg'
        return saveArrayasImg (image, filename=filenameuncensored, small=small)
    
    if includeuncensored: # just save image (no censoring, don't pass on suffix)
        filenameuncensored = filename_prefix + ftitle + '.jpg'
        saveArrayasImg (image, filename=filenameuncensored, small=small)

    if classes:
        detections = [
            detection for detection in detections if detection["class"] in classes
        ]

    for detection in detections:
        box = detection["box"]
        x, y, w, h = box[0], box[1], box[2], box[3]
        # change these pixels to pure black
        image[y : y + h, x : x + w] = (0, 0, 0)

    return saveArrayasImg (image, filename=filename, small=small)


def saveArrayasImg (image, filename='', filename_prefix='', filename_suffix='', small=False):
    """Save array as image (temp)"""
    if not filename:
        filename = filename_prefix + getfiletitle() + filename_suffix + '.jpg'
    if small: # assuming this is for logging; so shrink and blur image
        image = blurshrinkImgArray (image)
    cv2.imwrite(filename, image)
    return filename

def saveImage (image, filename_prefix=''):
    """Save array/image as file"""
    #TEST / DEBUG: PASSING image variable as save / load file
    filename = getfiletitle() + '.jpg'
    image.save(filename_prefix + filename, format='jpeg')

def saveImageMP (image, filename_prefix=''):
    """Save array/image as file with MatPlotLib.image"""
    #TEST / DEBUG: PASSING image variable as save / load file
    filename = getfiletitle() + '.jpg'
    mpimg.imsave(filename_prefix + filename, image)

def compareImgs (image1, image2):
    """Compare two images"""
    if not isinstance(image1, np.ndarray):
        image1 = convertImgtoArray(image1)
    if not isinstance(image2, np.ndarray):
        image2 = convertImgtoArray(image2)

    if image1.shape == image2.shape:
        difference = cv2.subtract(image1, image2)
        b, g, r = cv2.split(difference)
        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
            return 0 # no difference
    return 1 # difference