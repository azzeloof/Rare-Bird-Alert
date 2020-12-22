rare bird alert

requires
PIL
scipy (numpy)
picamera

raspi-config:
enable camera
Set pi GPU memory to at least 126mb (if full resolution desired)
set {hostname} to birds (if desired)

Set up apache server
set up dashboard at {hostname}.local:8080
reverse proxy main interface to {hostname}.local