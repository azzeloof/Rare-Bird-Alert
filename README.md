# Rare Bird Alert
Okay, this doesn't actally alert you about rare birds (yet?), but it does take pictures of birds. Hopefully.

Rare Bird Alert is a Raspberry Pi-based birdfeeder camera. 

## Requirements

+ PIL
+ scipy (numpy, matplotlib)
+ picamera
+ tensorflow (installed with instructions [here](https://raspberrypi.stackexchange.com/questions/107483/error-installing-tensorflow-cannot-find-libhdfs-so))
+ func-timeout

## Setup
run `sudo raspi-config` and:
+ Enable camera
+ Set pi GPU memory to at least 126mb (if we want to capture full resolution images with the HQ camera)
+ set the hostname to birds (if desired)
+ Set up apache server
+ Set up reverse proxy main interface to {hostname}.local
+ Download MobileNet labels and save them at `src/mobilenet-labels.json` (maybe do this in .sh?)

Now, the software can be run by executing `rareBirdAlert.sh` and the camera web interface can be accessed at `http://birds.local`

