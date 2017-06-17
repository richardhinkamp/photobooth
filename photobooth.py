from picamera import PiCamera
from time import sleep, strftime
from signal import pause
from PIL import Image
from gpiozero import Button
from config import VFLIP, BRIGHTNESS, EXPOSURE_MODE, PREVIEW_BRIGHTNESS, BUTTON_PIN, OVERLAY_FILENAME, COUNTDOWN_DELAY, SHOW_PHOTO_DELAY, SAVE_PATH

camera = PiCamera(resolution=(3280, 1845))
camera.vflip = VFLIP
camera.brightness = BRIGHTNESS
camera.exposure_mode = EXPOSURE_MODE
camera.brightness = PREVIEW_BRIGHTNESS
button = Button(BUTTON_PIN)

def imageToPad(img):
	# Create an image padded to the required size with mode 'RGB'
	pad = Image.new('RGBA', ( ((img.size[0] + 31) // 32) * 32, ((img.size[1] + 15) // 16) * 16 ) )
	# Paste the original image into the padded one
	pad.paste(img, (0, 0))
	return pad

def imageFilenameToPad(filename):
	img = Image.open(filename)
	return imageToPad(img)

imgOverlay = imageFilenameToPad(OVERLAY_FILENAME);
img1 = imageFilenameToPad('./overlay-1.png');
img2 = imageFilenameToPad('./overlay-2.png');
img3 = imageFilenameToPad('./overlay-3.png');
imgWhite = imageFilenameToPad('./white.png');

o = camera.add_overlay(imgOverlay.tobytes(), size=(1920, 1080), layer=6)
# By default, the overlay is in layer 0, beneath the
# preview (which defaults to layer 2). Here we make
# the new overlay semi-transparent, then move it above
# the preview

camera.start_preview(resolution=(1920, 1080))

def capture():
	# no button press during capture
	button.when_pressed = None
	
	# countdown
	overlay = camera.add_overlay(img3.tobytes(), layer=4, size=(1920, 1080));
	sleep(COUNTDOWN_DELAY)
	overlay.update(img2.tobytes())
	sleep(COUNTDOWN_DELAY)
	overlay.update(img1.tobytes())
	sleep(COUNTDOWN_DELAY)
	camera.remove_overlay(overlay)

	# capture image
	stamp = strftime("%Y%m%d-%H%M%S")
	whiteOverlay = camera.add_overlay(imgWhite.tobytes(), layer=9, size=(1920, 1080));
	camera.brightness = BRIGHTNESS
	camera.capture(SAVE_PATH + '/full/' + stamp + '.jpg', use_video_port=False)
	camera.brightness = PREVIEW_BRIGHTNESS
	
	# crop full image back to video viewport
	fullImg = Image.open('/home/pi/photos/full/' + stamp + '.jpg');
	imgVideoView = fullImg.crop((680,382,1920+680,1080+382))
	fullImg = None
	imgVideoView.save(SAVE_PATH + '/hd/' + stamp + '.jpg')
	
	# show taken picture for 5 seconds
	imgPhoto = imageToPad(imgVideoView);
	overlayPhoto = camera.add_overlay(imgPhoto.tobytes(), layer=4, size=(1920, 1080));
	camera.remove_overlay(whiteOverlay)
	sleep(SHOW_PHOTO_DELAY)
	camera.remove_overlay(overlayPhoto)

	# restore camera/button
	button.when_pressed = capture

button.when_pressed = capture

pause()
