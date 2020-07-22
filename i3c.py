import time
import smbus
from time import sleep
from threading import Thread
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool
binh=[]
def read_data():
    data = bus.read_i2c_block_data(0x1D, 0x00, 7)
    xAccl = (data[1] * 256 + data[2]) / 4
    if xAccl > 8192:
        xAccl -= 16384
    xAccl = xAccl / 4096 * 9.8
    yAccl = (data[3] * 256 + data[4]) / 4
    if yAccl > 8192:
        yAccl -= 16384
    yAccl = yAccl / 4096 * 9.8
    zAccl = (data[5] * 256 + data[6]) / 4
    if zAccl > 8192:
        zAccl -= 16384
    zAccl = zAccl / 4096 * 9.8
    global binh
    binh.append(xAccl)
    # print('X direction:', xAccl)
    # print('Y direction:', yAccl)
    # print('Z direction:', zAccl)
    return [xAccl,yAccl,zAccl]
def creatThread():
    runT=Thread(target=read_data)
    # runT.setDaemon(True)
    runT.start()
    runT.join()
    # pool1=Pool(1)
    # re=pool1.map(read_data,[])
    # # pool1.join()
    # return re

def creatThread2():
    runT2 = Thread(target=read_data)
    # runT2.setDaemon(True)
    runT2.start()
    runT2.join()
    # pool2=ThreadPool(processes=10)
    # re2=pool2.apply_async(read_data)
    # # pool2.
    # return re2.get()
if __name__=='__main__':
    bus = smbus.SMBus(1)
    # pool=[]
    # for i in range(0,1000):
    #     pool.append(ThreadPool(processes=1))
    val = 6
    length = 3
    count = 0
    i2c_address = 0x1C
    mma8451_reg_ctrl1 = 0x2A
    mma8451_reg_ctrl2 = 0x2B
    mma8451_reg_ctrl4 = 0x2A
    mma8451_reg_ctrl5 = 0x2A
    mma8451_reg_xyz_data_cfg = 0x0E
    store_arr = []
    # bus.write_byte_data(0x1D,0x2A,0x00)
    bus.write_byte_data(i2c_address, mma8451_reg_ctrl2, 0x40)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, mma8451_reg_xyz_data_cfg, 0x10)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, mma8451_reg_ctrl2, 0x01)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, mma8451_reg_ctrl4, 0x01)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, mma8451_reg_ctrl5, 0x01)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, mma8451_reg_ctrl1, 0x04 | 0x01)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, 0x11, 0x40)
    time.sleep(0.1)
    bus.write_byte_data(i2c_address, 0x0F, 0x20)
    time.sleep(0.1)
    t0=time.time()
    t1=t0
    while (count<1024):
        if((time.time()-t0)>=0.001):
            t0=time.time()
            # creatThread()
            # read_data()
            # pool=ThreadPool(processes=1)
            if (count%2==0):
                creatThread()
            else:
                creatThread2()
            # print(time.time()-t0)
            count+=1
        else:
            pass
    period=time.time()-t1
    print('count=:',count)
    print('period=:',period)
    print(binh)
