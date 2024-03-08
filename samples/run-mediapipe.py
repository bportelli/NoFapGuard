## Pose Landmarks Reference:
##int	LEFT_ANKLE	The landmark which corresponds to the left ankle.
##int	LEFT_EAR	The landmark which corresponds to the left ear.
##int	LEFT_ELBOW	The landmark which corresponds to the left elbow.
##int	LEFT_EYE	The landmark which corresponds to the left eye.
##int	LEFT_EYE_INNER	The landmark which corresponds to the inner left eye.
##int	LEFT_EYE_OUTER	The landmark which corresponds to the outer left eye.
##int	LEFT_FOOT_INDEX	The landmark which corresponds to the left foot index.
##int	LEFT_HEEL	The landmark which corresponds to the left heel.
##int	LEFT_HIP	The landmark which corresponds to the left hip.
##int	LEFT_INDEX	The landmark which corresponds to the left index finger.
##int	LEFT_KNEE	The landmark which corresponds to the left knee.
##int	LEFT_MOUTH	The landmark which corresponds to the left mouth.
##int	LEFT_PINKY	The landmark which corresponds to the left pinky.
##int	LEFT_SHOULDER	The landmark which corresponds to the left shoulder.
##int	LEFT_THUMB	The landmark which corresponds to the left thumb.
##int	LEFT_WRIST	The landmark which corresponds to the left wrist.
##int	NOSE	The landmark which corresponds to the nose.
##int	RIGHT_ANKLE	The landmark which corresponds to the right ankle.
##int	RIGHT_EAR	The landmark which corresponds to the right ear.
##int	RIGHT_ELBOW	The landmark which corresponds to the right elbow.
##int	RIGHT_EYE	The landmark which corresponds to the left eye.
##int	RIGHT_EYE_INNER	The landmark which corresponds to the inner left eye.
##int	RIGHT_EYE_OUTER	The landmark which corresponds to the outer left eye.
##int	RIGHT_FOOT_INDEX	The landmark which corresponds to the right foot index.
##int	RIGHT_HEEL	The landmark which corresponds to the right heel.
##int	RIGHT_HIP	The landmark which corresponds to the right hip.
##int	RIGHT_INDEX	The landmark which corresponds to the right index finger.
##int	RIGHT_KNEE	The landmark which corresponds to the right knee.
##int	RIGHT_MOUTH	The landmark which corresponds to the right mouth.
##int	RIGHT_PINKY	The landmark which corresponds to the right pinky.
##int	RIGHT_SHOULDER	The landmark which corresponds to the right shoulder.
##int	RIGHT_THUMB	The landmark which corresponds to the right thumb.
##int	RIGHT_WRIST	The landmark which corresponds to the right wrist.

## CURRENT DIR
#dirname = 'sample-imgs'
dirname = 'sample-screenshots'

import mediapipe as mp
import matplotlib.image as mpimg # NB: contains imread and imsave
#import matplotlib.patches as mppatches
from numpy import uint8

mp_pose = mp.solutions.pose

## List of landmarks of interest
landmarksindexlist = [
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

def processnolandmarks(image):
    # remove bottom 25%, top 20% and 10% from either side
    image = image[0:int(image.shape[0]*0.8), int(image.shape[1]*0.1):int(image.shape[1]*0.9)]
    return image


def capture_landmarks(image_input, output_path):
    with mp_pose.Pose(min_detection_confidence=0.5) as pose:
        
        # is image a string (path?) or an image?
        if type(image_input) == str:
            image = mpimg.imread(image_input)[:,:,:3] #sample image (forcing 3 channels: RGB, ignoring alpha)

            img_RGB = image/image.max()#it's the casting of float32 to uint8
            img_RGB = 255 * img_RGB#it's the casting of float32 to uint8
            image = img_RGB.astype(uint8) #it's the casting of float32 to uint8

        else: 
            image = image_input

        results = pose.process(image)

        if not results.pose_landmarks:
            print('FAILED ON: ' + str(image_input))
            img_out = processnolandmarks(image)
            return (False, str(image_input), output_path, img_out)

        landmarks = results.pose_landmarks.landmark

        h , w , c = image.shape

        # Work out coordinates for an area of ??px  around (rightCx, rightCy)
        # CONSTANTS
        bwx, bwy = (300, 300)
        bwxoffset = int(bwx/2)
        bwyoffset = int(bwy/2)

        # box area (starting values)
        upperbound = h-10
        lowerbound = 0
        leftbound = w
        rightbound = 0
        for poselandmark in landmarksindexlist:
            rightCx = int(results.pose_landmarks.landmark[poselandmark].x * w)
            rightCy = int(results.pose_landmarks.landmark[poselandmark].y * h)

            if rightCx > w or rightCy > h or rightCx < 0 or rightCy < 0 :
                continue

            print(poselandmark)
            print((rightCx, rightCy))

            # box area: work out the area that will catch all landmarks
            upperbound = max(0, min(upperbound, rightCy - bwyoffset))
            lowerbound = min(h, max(lowerbound, rightCy + bwyoffset))
            leftbound = max(0, min(leftbound, rightCx - bwxoffset))
            rightbound = min(w, max(rightbound, rightCx + bwxoffset))
            #upperbound = 0
            #lowerbound = h
            #leftbound = 0
            #rightbound = w
        
        #print((rightCy-50, rightCy+50, rightCx-50, rightCx+50))
        #(718, 818, 200, 300)

        img_out = image [upperbound:lowerbound, leftbound:rightbound]

        if img_out.shape[0] < 10 or img_out.shape[1] < 10:
            print('FAILED ON: ' + str(image_input))
            print('Cropping image instead')
            img_out = processnolandmarks(image)
            
            return (False, str(image_input), output_path, img_out)

        return (True, str(image_input), output_path, img_out) # success

## Main
       
## Quick Check if it catches landmarks in all sample images
import os

#get all files (not dirs)
imgs = [f for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f))]

with open("Log.txt", "w") as logfile:
    for im in imgs:
        im = str(im)
        print(im)

        success, inpath, outpath, img_out = capture_landmarks(dirname + '/' + im, output_path=dirname + '/landmarks/landmarks-'+im)

        if not success:
            logfile.write("FAILED: " + inpath + '\n')

        mpimg.imsave(outpath, img_out)


## Quick Check if it spots unsafe elements in all images AFTER MediaPipe
from nudenet import NudeDetector
nude_detector = NudeDetector()
#get all files (not dirs)
imgs = [f for f in os.listdir(dirname + '/landmarks') if os.path.isfile(os.path.join(dirname + '/landmarks', f))]

for im in imgs:
	nude_detector.censor(dirname + '/landmarks/'+im, output_path=dirname + '/landmarks/censored/censored-'+im) 