Setting up a new raspberry pi:
* passwd
  - *The default password for the pi user is raspberry.  Change this default password ASAP.  Extremely hostile malware is in the wild.*
* sudo apt update
* sudo apt-get dist-upgrade
* sudo apt-get install python-serial libffi-dev libssl-dev libperl-dev libgtk2.0-dev libgirepository1.0-dev gtk+3
* sudo raspi-config
  * Under localization, fix the keyboard
    * My Raspberry Pi defaulted to en-GB and I use an en-US keyboard
  * Under interface, turn on peripherals
    * Set the hostname, suggestion: blinkie0, blinkie1...
    * Enable SSH
    * Enable SPI
    * Enable I2C
    * Enable Serial
