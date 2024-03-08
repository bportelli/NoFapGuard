from statistics import mode
import time
from desktopmagic.screengrab_win32 import (
	getDisplayRects, saveScreenToBmp, saveRectToBmp, getScreenAsImage,
	getRectAsImage, getDisplaysAsImages)

from nudenet import NudeClassifier
from nudenet import NudeDetector

## Variables
FONTSCALE = 1
BASEWIDTH = 300

def grab_two_displays_shrink_crop():
	im_filenames = []
	im_filename = 'img' + str((int(round(time.time(),2)*100)))[-8:-1]

	for displayNumber, rect in enumerate(getDisplayRects(), 1):
		im_filename_d = r'shots\\' + im_filename + '_%d.jpg' % (displayNumber,)
		if displayNumber == 1:
			rect = tuple(int(FONTSCALE * c) for c in rect)

		# CROP IMAGE (THIS IS A TEST)
		scaleF = 0.7
		rect = tuple([rect[0], rect[1], int(abs(rect[0] - rect[2])*scaleF+rect[0] ), rect[3]])

		imDisplay = getRectAsImage(rect)
		
		# SHRINK IMAGE
		wpercent = (BASEWIDTH/float(imDisplay.size[0]))
		hsize = int((float(imDisplay.size[1])*float(wpercent)))
		imDisplay = imDisplay.resize((BASEWIDTH,hsize))
		
		imDisplay.save(im_filename_d, format='jpeg')

		im_filenames.append(im_filename_d)

	return im_filenames

def grab_two_displays_shrink():
	im_filenames = []
	im_filename = 'img' + str((int(round(time.time(),2)*100)))[-8:-1]

	for displayNumber, rect in enumerate(getDisplayRects(), 1):
		im_filename_d = r'shots\\' + im_filename + '_%d.jpg' % (displayNumber,)
		if displayNumber == 1:
			rect = tuple(int(FONTSCALE * c) for c in rect)
		
		imDisplay = getRectAsImage(rect)
		
		# SHRINK IMAGE (to standard basewidth)
		wpercent = (BASEWIDTH/float(imDisplay.size[0]))
		hsize = int((float(imDisplay.size[1])*float(wpercent)))
		imDisplay = imDisplay.resize((BASEWIDTH,hsize))
		
		imDisplay.save(im_filename_d, format='jpeg')

		im_filenames.append(im_filename_d)

	return im_filenames

def grab_two_displays():
	im_filenames = []
	im_filename = 'img' + str((int(round(time.time(),2)*100)))[-8:-1]

	for displayNumber, rect in enumerate(getDisplayRects(), 1):
		im_filename_d = r'shots\\' + im_filename + '_%d.jpg' % (displayNumber,)
		if displayNumber == 1:
			rect = tuple(int(FONTSCALE * c) for c in rect)
		imDisplay = getRectAsImage(rect)
		imDisplay.save(im_filename_d, format='jpeg')

		im_filenames.append(im_filename_d)

	return im_filenames

def grab_virtual_screen():
	im_filename = 'img' + str((int(round(time.time(),2)*100)))[-8:-1]

	# Save the entire virtual screen as a JPG
	entireScreen = getScreenAsImage()
	entireScreen.save(r'shots\\' + im_filename + '.jpg', format='jpeg')

	return r'shots\\' + im_filename + '.jpg'

def assess(imgpath, **kwargs):
	outfile = kwargs.get('outfile', None)
	#imgpath = 'shots/test.jpg'
	classifier = NudeClassifier()
	detector = NudeDetector()

	## Classifier Output
	# print(classifier.classify(imgpath))
	c = classifier.classify(imgpath)
	
	if outfile:
		print(c, file=outfile)
	else:
		print(c[imgpath])

	##

	## Detector Output (Memo: the detector also puts out an estimate of the location ('box') of the items)
	#print(detector.detect(imgpath))
	#print(detector.detect(imgpath, mode="fast"))

	d = detector.detect(imgpath, mode="fast")

	if outfile:
		print(d, file=outfile)
	else:
		{print(x['label'],x['score']) for x in d}

	##