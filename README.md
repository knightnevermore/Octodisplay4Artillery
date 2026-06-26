My friend gifted me an Artillery Sidewinder X2 3D-printer. It was nice to play around with it and make a few prints,
but over time it got annoying to always copy the file to the USB stick, bring it over to the printer and then start
printing from there.

So I checked out some options and realized that I can use a Raspberry Pi 4 computer to be able to print straight from
my slicer (OrcaSlicer).
After I had it running it was great. Besides the fact that I always had to check the webinterface to see how far the
print was. But then I remembered that the PI has GPIO pins, so I connected a display and made it work.
Then I added a camera and got everything running.
I also printed my own Raspberry Pi holder, my display mount and a camera mount, all modular.

I thought this turned out pretty well, so I decided to release everything publicly, so in case someone else wants to
upgrade their Sidewinder X2 with these components as well, then give it a go.

What you need:
==============
- A Raspberry Pi 4B+ (might work with older models as well, but I didn't test it, so no promises here.
- A display from Aliexpress*
- A camera from Aliexpress*

*I bought these two devices:
- TENSTAR ROBO 2,8 inch 240x320 320x480 SPI TFT Serial Port Module 5V/3,3V PCB Adapter ST7789V/ST7796S LCD Display  (2.8 Inch version)
(https://de.aliexpress.com/item/1005006175220737.html)
- Raspberry Pi 4 Camera 5 MP for Raspberry Pi 4B 3B+ 3B Zero  (I 130 version)
(https://de.aliexpress.com/item/32668508991.html)

The 3D printed modules released here:
<todo: add link>

Installation instructions:
==========================
- Install OctoPi on a SD card using the Raspberry Pi Imager (configure WiFi and everything to your environment)
- Connect to the OctoPi via SSH (Putty)
- run sudo raspi-config and enable GPIO
- shutdown the OctoPi
- connect your display (see PinConnections.jpg)
- (optional) connect the camera
- Reboot the OctoPi
- run sudo apt install -y python3-pip python3-pil python3-numpy
- run sudo apt install -y python3-venv python3-full
- run sudo apt install libopenjp2-7 libtiff5
- run python3 -m venv venv
- run source venv/bin/activate
- Connect to the OctoPi with a FTP program like Filezilla, using your IP, SFTP Protocol and your SSH user login data
- (optional) edit the octodisplay.py file (top section with the api key etc.)
- transfer the .py files and the background picture(s) of your choice into a subfolder of your choice on the pi
- (optional) edit the octodisplay.py (setup) by running nano octodisplay.py
- test the script to see if it works by running python octodisplay.py  (end the script with ctrl + c)

- if it works and you want the script to start automatically at bootup follow these steps:
- run sudo nano /etc/systemd/system/octodisplay.service 
- enter/paste the following content (modify the ExecStart and WorkingDirectory path to fit your system):
[Unit]
Description=OctoPrint ST7789 Display
After=network.target

[Service]
ExecStart=/home/admin/octodisplay/venv/bin/python /home/admin/octodisplay/octodisplay.py
WorkingDirectory=/home/admin/octodisplay
Restart=always
User=admin

[Install]
WantedBy=multi-user.target

- run sudo systemctl daemon-reload
- run sudo systemctl enable octodisplay.service 
- run sudo systemctl start octodisplay.service
- try rebooting the pi and see if the script starts (if not, the path or the script might be wrong)


File explanation:
=================
background_xx.png => example background files for the display (transparent if you want to use another color).
octodisplay.py    => the main script that reads out the values from the octopi api and writes the values to the display
st7789_hw.py      => driver for the aliexpress display. If you have another display, you will have to modify things yourself.


Editing instructions:
=====================
octodisplay.py:
---------------

- API_KEY -> Get the API key from your octopi and enter it, by replacing the example "abcdefg...." in the file. This is mandatory for the display to work!
- OCTO_JOBURL -> only edit if you want to read values from another pi or using another API address
- OCTO_PRINTERURL -> only edit if you want to read values from another pi or using another API address
- BACKGROUND_PATH -> set the path to your background file.

(optional parts)
when using another display, you need to install the corresponding driver, e.g. adafruit etc. and use another display initialization
display = ...

you might also have to adjust the drawing of the image on the display according to what your displays offers
display.image(image)

if you want the display to refresh faster or slower, adjust the refresh time at the end (don't go too fast, unless you absolutely need it, lower = faster)
time.sleep(2)
