# blinkie
![blinkie](https://raw.githubusercontent.com/joeldeaguero/blinkie/master/blinkie.png)

Setting up a new raspberry pi:
* passwd
* sudo apt update
* sudo apt-get dist-upgrade
* sudo apt-get install python-serial
* Fix keyboard layout
* Enable SSH
* Enable SPI
* Enable I2C
* Enable Serial

* To look in boot for whether or not the serial port is enabled:
grep uart /config/boot.txt 
Reference: https://www.raspberrypi.org/forums/viewtopic.php?t=172958
