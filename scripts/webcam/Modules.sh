ls -l /dev/ttyUSB*
sudo lsmod

sudo modprobe i2c_bcm2708
sudo modprobe uio_pdrv_genirq
sudo modprobe uio
sudo lsmod
sudo modprobe usbserial
sudo i2cdetect -y 1    
sudo modprobe pl2303
sudo modprobe -r usbserial
sudo modprobe usbserial vendor=0x0403 product=0x6001
sudo modprobe pl2303
sudo modprobe ftdi_sio

sudo chmod 777 /dev/ttyUSB0
dmesg | grep ttyUSB*

ls -l /dev/ttyUSB*

