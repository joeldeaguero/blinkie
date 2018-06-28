# blinkie
We're making a 3D printer.  A very custom one!

* apt update
* sudo apt-get dist-upgrade
* Fix keyboard layout
* Change password for pi
* Enable SSH
* Enable SPI
* Enable I2C
* Enable Serial
* sudo apt-get install python-serial

* To look in boot for whether or not the serial port is enabled:
grep uart /config/boot.txt 
Reference: https://www.raspberrypi.org/forums/viewtopic.php?t=172958
