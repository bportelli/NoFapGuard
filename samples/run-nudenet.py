#nude_detector.detect('image.jpg') # Returns list of detections

detection_example = [
 {'class': 'BELLY_EXPOSED',
  'score': 0.799403190612793,
  'box': [64, 182, 49, 51]},
 {'class': 'FACE_FEMALE',
  'score': 0.7881264686584473,
  'box': [82, 66, 36, 43]},
 ]


#nude_detector.censor('image.jpg') # returns censored image output path

# optional censor(self, image_path, classes=[], output_path=None) classes and output_path can be passed

all_labels = [
    "FEMALE_GENITALIA_COVERED",
    "FACE_FEMALE",
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "ANUS_EXPOSED",
    "FEET_EXPOSED",
    "BELLY_COVERED",
    "FEET_COVERED",
    "ARMPITS_COVERED",
    "ARMPITS_EXPOSED",
    "FACE_MALE",
    "BELLY_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_COVERED",
    "FEMALE_BREAST_COVERED",
    "BUTTOCKS_COVERED",
]

## Quick Check if it spots unsafe elements in all sample images
import os

def maintest():
    from nudenet import NudeDetector
    nude_detector = NudeDetector()
    ## CURRENT DIR
    dirname = 'samples/sample-imgs'
    #dirname = 'samples/sample-screenshots'

    #get all files (not dirs)
    imgs = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]

    for im in imgs:
        pass
        #nude_detector.censor(dirname + '/'+im, output_path=dirname + '/censored/censored-'+im) 
        #print(nude_detector.detect(dirname + '/'+im))

def censorImageObjNN_test():
    # TESTING NEW FUNCTION: detectfromImage
    # Screen rect samples: (0, 0, 1536, 864), (-1280, 0, 0, 1024)
    from screengrab import grab_rect
    from numpy import array as nparray
    #from PIL import Image as PILImage
    import cv2
    from nudenetImage import NudeDetector # Note the new (expanded) library
    nude_detector = NudeDetector()

    image_grab = grab_rect((-1280, 0, 0, 1024))

    #print(image_grab)

    image = nparray(image_grab)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print(image)

    # cv2.imshow('titleNOW', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    print(nude_detector.detectfromImage(image))
    print(nude_detector.censorfromImage(image,output_path='test.jpg'))
    # check the image
    # image = PILImage.fromarray(image)
    # image.save('test.jpg', format='jpeg')
    print(nude_detector.detect('test.jpg')) # test to make sure the original functions still work
    print(nude_detector.censor('test.jpg',output_path='test2.jpg'))

censorImageObjNN_test()