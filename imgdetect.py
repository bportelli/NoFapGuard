import mediapipe as mp
#import matplotlib.patches as mppatches
from nudenetImage import NudeDetector # Note the new (expanded) library
from numpy import array as nparray
from cv2 import cvtColor as cv2cvtColor
from cv2 import COLOR_BGR2RGB as cv2COLOR_BGR2RGB
import logging
#import time

## Initialise
mp_pose = mp.solutions.pose
nude_detector = NudeDetector()
landmarksindexlist = [ # List of landmarks of interest
    mp_pose.PoseLandmark.LEFT_ANKLE,
    mp_pose.PoseLandmark.LEFT_EAR,
    mp_pose.PoseLandmark.LEFT_EYE,
    mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
    mp_pose.PoseLandmark.LEFT_HEEL,
    mp_pose.PoseLandmark.LEFT_HIP,
    mp_pose.PoseLandmark.MOUTH_LEFT,
    mp_pose.PoseLandmark.LEFT_PINKY,
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    mp_pose.PoseLandmark.RIGHT_ANKLE,
    mp_pose.PoseLandmark.RIGHT_EAR,
    mp_pose.PoseLandmark.RIGHT_EYE,
    mp_pose.PoseLandmark.RIGHT_FOOT_INDEX,
    mp_pose.PoseLandmark.RIGHT_HEEL,
    mp_pose.PoseLandmark.RIGHT_HIP,
    mp_pose.PoseLandmark.MOUTH_RIGHT,
    mp_pose.PoseLandmark.RIGHT_PINKY,
    mp_pose.PoseLandmark.RIGHT_SHOULDER
]

# Functions
def processnolandmarks(image):
    # remove bottom 10% and 10% from either side
    image = image[0:int(image.shape[0]*0.9), int(image.shape[1]*0.05):int(image.shape[1]*0.95)]
    return image

def imgreadandprocess(image_input_path):
    import matplotlib.image as mpimg # NB: contains imread and imsave
    from numpy import uint8

    image = mpimg.imread(image_input_path)[:,:,:3] #sample image (forcing 3 channels: RGB, ignoring alpha)
    img_RGB = image/image.max()#it's the casting of float32 to uint8
    img_RGB = 255 * img_RGB#it's the casting of float32 to uint8
    image = img_RGB.astype(uint8) #it's the casting of float32 to uint8
    return image

def focus_img_on_landmarks(image_input):
    with mp_pose.Pose(min_detection_confidence=0.5) as pose:
        
        # is image a string (path?) or an image?
        if type(image_input) == str:
            image = imgreadandprocess(image_input)
        else:
            image = image_input

        image = nparray(image)
        image = cv2cvtColor(image, cv2COLOR_BGR2RGB) # fix color channels

        results = pose.process(image)

        # No landmarks: return a slightly cropped original image
        if not results.pose_landmarks:
            img_out = processnolandmarks(image)
            logging.info('MP: No landmarks found.')
            return img_out
        
        landmarks = results.pose_landmarks.landmark
        h , w , c = image.shape

        # Work out coordinates for a box of 400px around (rightCx, rightCy)
        # CONSTANTS
        bwx, bwy = (500, 500)
        bwxoffset = int(bwx/2)
        bwyoffset = int(bwy/2)

        # box area (starting values)
        upperbound = h-10
        lowerbound = 0
        leftbound = w
        rightbound = 0
        for poselandmark in landmarksindexlist:
            rightCx = int(landmarks[poselandmark].x * w)
            rightCy = int(landmarks[poselandmark].y * h)

            if rightCx > w or rightCy > h or rightCx < 0 or rightCy < 0 :
                continue

            # box area: work out the area that will catch all landmarks
            upperbound = max(0, min(upperbound, rightCy - bwyoffset))
            lowerbound = min(h, max(lowerbound, rightCy + bwyoffset))
            leftbound = max(0, min(leftbound, rightCx - bwxoffset))
            rightbound = min(w, max(rightbound, rightCx + bwxoffset))
        
        # crop image
        img_out = image [upperbound:lowerbound, leftbound:rightbound]

        # No landmarks: return a slightly cropped original image
        if img_out.shape[0] < 10 or img_out.shape[1] < 10:
            img_out = processnolandmarks(image)
            logging.error('Image too small. MP extrapolating only landmarks beyond image boundaries?')
            return img_out
        
        logging.debug('MP Landmarks found.')
        return img_out
    
def detect_unsafe_img (imagepath):
    if type(imagepath) == str: # if imagepath is a path
        #return nude_detector.censor(imagepath)
        return nude_detector.detect(imagepath)
    else: # if imagepath is an image
        #return nude_detector.censorfromImage(imagepath)
        return nude_detector.detectfromImage(imagepath)