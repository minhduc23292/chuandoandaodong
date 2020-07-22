import time
import smbus2
from time import sleep
bus = smbus2.SMBus(1)
addr = 0x08
val = 0x10
length=10
count=0
t0=time.time()
store_arr=[]
while(count<length):
	bus.write_byte(addr,val)
	ahihi=bus.read_i2c_block_data()
	print(ahihi)
	count+=1
