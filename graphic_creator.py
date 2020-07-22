
from datetime import datetime
import matplotlib
import os,sys
current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
sys.path.insert(0, parent_directory)
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D, proj3d
from matplotlib import cm, dates
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.ticker as ticker

from scipy import fftpack, signal
import numpy as np
import sys
import tkinter as Tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import Canvas
from tkinter import Menu
from tkinter.font import Font
import string
import serial
import serial.tools.list_ports
import time
# import home/pi/Downloads/project/xulydata/calculate.py
import creatTab
import Plot_data as Pd
import file_operation
import smbus
from threading import Thread
from multiprocessing.pool import ThreadPool
import ADS1256
import RPi.GPIO as GPIO
data_length = 512 # Amount of samples to read.16384
sample_rate = 800
g_scale = (3.3 / 1024) * (1000 / 300)
max_freq = sample_rate / 2  # Maximum signal frequency, X and Y axis (accelerometer).1500
max_freq_z = sample_rate / 2  # Maximum signal frequency, Z axis (accelerometer).500
fft_data_ch1=[]
fft_data_ch2=[]
fft_data_ch3=[]
g_chanel_1 = []  # Global canal_1
g_chanel_2 = []  # Global canal_2
g_chanel_3 = []  # Global canal_3
t_timeout = 30  # Timeout time in seconds.
binh1=[]
binh2=[]
binh3=[]

class Application():
    load_data = [1]
    def __init__(self, parent):
        self.parent = parent
        self.frames()
        self.f_saved = True  # Sampled data saved
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.bus1 = smbus.SMBus(1)
        self.bus2 = smbus.SMBus(2)
        self.i2c_address1 = 0x1D
        self.i2c_addrses2 = 0x1C


    def on_closing(self):
        if (self.f_saved == False):
            if messagebox.askokcancel("Quit", "Sampled data not saved. Do you wanto to quit?"):
                root.destroy()
        else:
            root.destroy()

    def _quit(self):
        root.quit()
        root.destroy()
        exit()
    def ch1Callback(self):
        global g_chanel_1
        canal=g_chanel_1
        Pd.PLT.plot1chanel(self.canvas1, canal,1)

    def ch2Callback(self):
        global g_chanel_2
        canal = g_chanel_2
        Pd.PLT.plot1chanel(self.canvas1, canal, 2)

    def ch3Callback(self):
        global g_chanel_3
        canal = g_chanel_3
        Pd.PLT.plot1chanel(self.canvas1, canal, 3)
    def allChCallback(self):
        global g_chanel_1, g_chanel_2, g_chanel_3
        canal1=g_chanel_1
        canal2=g_chanel_2
        canal3=g_chanel_3
        Pd.PLT.plot_all_chanel(self.canvas1, canal1, canal2, canal3)
    def tab3LoadCallback(self):
        self.load_data=file_operation.FileOperation(root).open_and_read()
        numOfGraph = len(self.load_data)
        fig3 = creatTab.CRT.creatFigure(self.tab3Frame2, numOfGraph-1)
        fig3.set_visible(True)
        self.canvas3 = FigureCanvasTkAgg(fig3,master=self.tab3Frame2)
        self.canvas3.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.toolbar3 = NavigationToolbar2Tk(self.canvas3,self.tab3Frame2)
        self.toolbar3.update()
        self.canvas3._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        Pd.PLT.plot_all_history(self.canvas3, self.load_data[:len(self.load_data)-1],self.load_data[len(self.load_data)-1])
        Pd.PLT.plot_trend(self.canvas4, self.load_data[:len(self.load_data) - 1],self.load_data[len(self.load_data) - 1])

    def rebalance_callback(self):
        Pd.PLT.plot_polar(self.canvas5)
    def scan_serial_port(self):
        portName=[]
        ports = list(serial.tools.list_ports.comports())
        for index in range(len(ports)):
            portName.append(ports[index][0])
        return portName
    def scan_ports(self):
        portnames = []
        self.portnames = self.scan_serial_port()
        print("kieu cua portname: ",len(self.portnames))
        self.tab1Bt4.configure(text="Active port"+"\n"+str(self.portnames[0])+"\n"+"Ready")
    def read_serial(self):
        status_serial = False
        try:
            serial_avr = serial.Serial(port='/dev/ttyAMA0',baudrate=2000000,
                                       bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,
                                       stopbits=serial.STOPBITS_ONE,timeout=0)
            time.sleep(2)
            print("Initializing...")
            print('ten tap la:',str(self.portnames[0]))
            if(serial_avr.isOpen()==True):
                status_serial=True
                print('KET NOI TOT')
            else:
                status_serial=False

        except(serial.SerialException,ValueError) as ex:
            messagebox.showerror("Result", "Can not open serial port"+ str(ex))
        if(status_serial==True):
            global g_chanel_1, g_chanel_2, g_chanel_3, data_length
            chanel1=[]
            chanel2=[]
            chanel3=[]
            buffer=[]
            temp_value=[]
            value=[]
            serial_avr.flushInput()
            serial_avr.flushOutput()
            valores_decod1 = []
            valores_decod2 = []
            valores_decod3 = []
            count=0
            serial_avr.write(b'INI')
            serial_avr.write(b'\x7E')
            global t_timeout
            timeout_state=False
            t0=time.time()
            while((count<data_length)and(timeout_state==False)):
                if(serial_avr.inWaiting()):
                    read_buffer = serial_avr.read(serial_avr.inWaiting())
                    buffer += read_buffer
                    value=[]
                if len(buffer) > 11:
                    try:
                        i=buffer.index(0x7E)
                    except(ValueError):
                        i=-1
                    if i>0:
                        temp_value = buffer[:i]
                        buffer = buffer[i + 1:]
                        value=[i for i in temp_value]
                        if len(value) == 18:
                            x=0
                            dem=0
                            count += 1
                            # print(count)
                            while x<18:
                                if ((value[x] == 0x2D) or (value[x] == 0x2B)) and (dem == 0):
                                    if(value[x]==0x2D):
                                        valores_decod1.append(-1)
                                    else:
                                        valores_decod1.append(1)
                                    valores_decod1.append(value[x + 1] - 48)
                                    valores_decod1.append(value[x + 2] - 48)
                                    valores_decod1.append(value[x + 3] - 48)
                                    valores_decod1.append(value[x + 4] - 48)
                                    valores_decod1.append(value[x + 5] - 48)
                                    x += 1
                                    dem+=1
                                if ((value[x] == 0x2D) or value[x] == 0x2B) and (dem == 1):
                                    if (value[x] == 0x2D):
                                        valores_decod2.append(-1)
                                    else:
                                        valores_decod2.append(1)
                                    valores_decod2.append(value[x + 1] - 48)
                                    valores_decod2.append(value[x + 2] - 48)
                                    valores_decod2.append(value[x + 3] - 48)
                                    valores_decod2.append(value[x + 4] - 48)
                                    valores_decod2.append(value[x + 5] - 48)
                                    x += 1
                                    dem += 1
                                if ((value[x] == 0x2D) or value[x] == 0x2B) and (dem == 2):
                                    if (value[x] == 0x2D):
                                        valores_decod3.append(-1)
                                    else:
                                        valores_decod3.append(1)
                                    valores_decod3.append(value[x + 1] - 48)
                                    valores_decod3.append(value[x + 2] - 48)
                                    valores_decod3.append(value[x + 3] - 48)
                                    valores_decod3.append(value[x + 4] - 48)
                                    valores_decod3.append(value[x + 5] - 48)
                                    x += 1
                                    dem =0
                                else:
                                    x += 1
                        else:
                            print("khong lam gi")

                        canal1 = valores_decod1[0] * (
                                    (valores_decod1[1] * 10000) + valores_decod1[2] * 1000 + valores_decod1[3] * 100 +
                                    valores_decod1[4] * 10 + valores_decod1[5]) / 1000
                        canal2 = valores_decod2[0] * (
                                    (valores_decod2[1] * 10000) + valores_decod2[2] * 1000 + valores_decod2[3] * 100 +
                                    valores_decod2[4] * 10 + valores_decod2[5]) / 1000
                        canal3 = valores_decod3[0] * (
                                    (valores_decod3[1] * 10000) + valores_decod3[2] * 1000 + valores_decod3[3] * 100 +
                                    valores_decod3[4] * 10 + valores_decod3[5]) / 1000
                        chanel1.append(canal1)
                        chanel2.append(canal2)
                        chanel3.append(canal3)
                        print("Canal 1: %s    Canal2: %s   Canal3: %s " % (canal1, canal2, canal3))
                        value = []
                        valores_decod1 = []
                        valores_decod2 = []
                        valores_decod3 = []

                if(time.time()-t0) > t_timeout:
                    timeout_state=True
            if (timeout_state == False):

                totalTime=time.time() - t0
                print(totalTime)
                self.tab1Bt8.configure(text="READ SENSOR"+"\n"+str(totalTime)[:6])
                print("Sending PAR")
                serial_avr.write(b'PAR')  # Stop data sampling.
                serial_avr.write(b"\x7E")  # End of packet.

                serial_avr.close()  # Close serial port.

                print("Amount of samples channel 1: %s" % len(chanel1))
                print("Amount of samples channel 2: %s" % len(chanel2))
                print("Amount of samples channel 3: %s" % len(chanel3))


                # Keep a copy of the original values
                g_chanel_1 = chanel1[:]  # Copy list by value not by reference
                g_chanel_2 = chanel2[:]
                g_chanel_3 = chanel3[:]
                self.f_saved = False
                # Sampled data not saved
                Pd.PLT.plot_all_chanel(self.canvas1, chanel1, chanel2, chanel3)
                Pd.PLT.plot_fft(self.canvas2, chanel1, chanel2, chanel3, win_var=1)
                Pd.PLT.plot_rms(self.canvas4,[chanel1, chanel2, chanel3])
            else:
                serial_avr.write(b'PAR')  # Stop data sampling.
                serial_avr.write(b"\x7E")  # End of packet.
                serial_avr.close()  # Close serial port.
                print("Serial port timeout")
                message_string = ("Serial port timeout \n")

    def frames(self):
        style = ttk.Style()
        style.configure('TNotebook.Tab',width=50, height=50,font=('Helvetica', 20),relief='raised',fg='red')
        style.configure('TNotebook', tabposition='s', font=('Helvetica', 18),fg='red')
        note = ttk.Notebook(root,cursor="arrow",height=2000,width=200,style='TNotebook')
        [self.tab1,self.tab2, self.tab3, self.tab4, self.tab5, self.tab6] = creatTab.CRT.creattab(note)
        [self.tab1Frame1, self.tab1Frame2, self.tab1Frame3] = creatTab.CRT.creatFrame(self.tab1)
        [self.tab2Frame1, self.tab2Frame2, self.tab2Frame3] = creatTab.CRT.creatFrame(self.tab2)
        [self.tab3Frame1, self.tab3Frame2, self.tab3Frame3] = creatTab.CRT.creatFrame(self.tab3)
        [self.tab4Frame1, self.tab4Frame2, self.tab4Frame3] = creatTab.CRT.creatFrame(self.tab4)
        [self.tab5Frame1, self.tab5Frame2, self.tab5Frame3] = creatTab.CRT.creatFrame(self.tab5)
        [self.tab6Frame1, self.tab6Frame2, self.tab6Frame3] = creatTab.CRT.creatFrame(self.tab6)
#tab1 frame
        self.tab1Frame1.pack(side='left')
        self.tab1Frame2.pack(side='left', fill='both', expand='true')
        self.tab1Frame3.pack(side='right', expand='true')
        [self.tab1Bt1,self.tab1Bt2, self.tab1Bt3, self.tab1Bt4] = creatTab.CRT.drawLeftTab(self.tab1Frame1, ['CH', 'CH2', 'CH1', 'SCAN'],
                                 ['disable', 'normal', 'normal', 'normal'],['grey', 'cyan', 'cyan', 'cyan'])
        [self.tab1Bt5,self.tab1Bt6, self.tab1Bt7, self.tab1Bt8] = creatTab.CRT.drawRightTab(self.tab1Frame3, ['CH', 'CH3', 'ALL CHANEL', 'READ SENSOR'],
                                  ['disable', 'normal', 'normal', 'normal'],['grey','cyan','cyan','cyan'])

        self.tab1Photo= PhotoImage(file="/home/pi/Downloads/project/image/channel1.gif")
        self.tab1Photo1 = PhotoImage(file="/home/pi/Downloads/project/image/serial1.gif")
        self.tab1Photo2 = PhotoImage(file="/home/pi/Downloads/project/image/readdata.gif")
        self.tab6Photo1 = PhotoImage(file="/home/pi/Downloads/project/image/shutdown1.gif")
        self.tab1Bt6.configure(command=self.ch3Callback,width=70,height=130, image=self.tab1Photo, compound="top")
        self.tab1Bt1.configure(width=70,height=110,image=self.tab1Photo,compound="top")
        self.tab1Bt5.configure(width=70,height=110,image=self.tab1Photo,compound="top")
        self.tab1Bt2.configure(command=self.ch2Callback,width=70,height=130, image=self.tab1Photo, compound="top")
        self.tab1Bt3.configure(command=self.ch1Callback,width=70,height=130, image=self.tab1Photo, compound="top")
        self.tab1Bt4.configure(command=self.scan_ports,width=70,height=130, image=self.tab1Photo1, compound="top")
        self.tab1Bt7.configure(command=self.allChCallback,width=70,height=130, image=self.tab1Photo, compound="top")
        self.tab1Bt8.configure(command=self.read_spi, width=70,height=130, image=self.tab1Photo2, compound="top")
        self.scan_ports()

#tab2 frame
        self.tab2Frame1.pack(side='left')
        self.tab2Frame2.pack(side='left', fill='both', expand='true')
        self.tab2Frame3.pack(side='right', expand='true')
        [self.tab2Bt1, self.tab2Bt2, self.tab2Bt3, self.tab2Bt4]=creatTab.CRT.drawLeftTab(self.tab2Frame1,
                               ['', '', '', ''],['disable', 'disable', 'disable', 'disable'],
                                 ['grey','grey','grey','grey'])
        [self.tab2Bt5, self.tab2Bt6, self.tab2Bt7, self.tab2Bt8]=creatTab.CRT.drawRightTab(self.tab2Frame3,['', '', '', ''],
                                  ['disable', 'disable', 'disable', 'disable'],['grey','grey','grey','grey'])

# tab3 frame
        self.tab3Frame1.pack(side='left')
        self.tab3Frame2.pack(side='left', fill='both', expand='true')
        self.tab3Frame3.pack(side='right', expand='true')
        [self.tab3Bt1, self.tab3Bt2, self.tab3Bt3, self.tab3Bt4] = creatTab.CRT.drawLeftTab(self.tab3Frame1,
                                                                                            ['', '', '', ''],
                                                                                            ['disable', 'disable',
                                                                                             'disable', 'disable'],
                                                                                            ['grey', 'grey', 'grey',
                                                                                             'grey'])
        [self.tab3Bt5, self.tab3Bt6, self.tab3Bt7, self.tab3Bt8]=creatTab.CRT.drawRightTab(self.tab3Frame3, ['', '', '', 'LOAD'],
                                  ['disable', 'disable', 'disable', 'normal'], ['grey', 'grey', 'grey', 'cyan'])
        self.tab3Bt8.configure(command=self.tab3LoadCallback)
        self.tab3Bt1.configure(width=8,height=8)
        self.tab3Bt5.configure(width=8,height=8)
# tab4 frame
        self.tab4Frame1.pack(side='left')
        self.tab4Frame2.pack(side='left', fill='both', expand='true')
        self.tab4Frame3.pack(side='right', expand='true')
        [self.tab4Bt1, self.tab4Bt2, self.tab4Bt3, self.tab4Bt4] = creatTab.CRT.drawLeftTab(self.tab4Frame1,
                                                                                            ['', '', '', ''],
                                                                                            ['disable', 'disable',
                                                                                             'disable', 'disable'],
                                                                                            ['grey', 'grey', 'grey',
                                                                                             'grey'])
        creatTab.CRT.drawRightTab(self.tab4Frame3, ['', '', '', ''],
                                  ['disable', 'disable', 'disable', 'disable'], ['grey', 'grey', 'grey', 'grey'])

#tab5Frame
        self.tab5Frame1.pack(side='left')
        self.tab5Frame2.pack(side='left', fill='both', expand='true')
        self.tab5Frame3.pack(side='right', expand='true')
        [self.tab5Bt1,self.tab5Bt2, self.tab5Bt3,self.tab5Bt4] = creatTab.CRT.drawLeftTab(self.tab5Frame1,
                                  ['', '', 'Trial Mass 1', 'Trial Mass 2'],['disable', 'disable', 'normal', 'normal'],
                                 ['grey','grey','cyan','cyan'])
        [self.tab5Bt5,self.tab5Bt6, self.tab5Bt7,self.tab5Bt8] = creatTab.CRT.drawRightTab(self.tab5Frame3, ['', '', 'Trial Mass 3', 'reBALANCE'],
                                  ['disable', 'disable', 'normal', 'normal'],['grey','grey','cyan','cyan'])


        self.tab5Bt8.configure(command=self.rebalance_callback)
#tab6 frame
        self.tab6Frame1.pack(side='left')
        self.tab6Frame2.pack(side='left', fill='both', expand='false')
        self.tab6Frame3.pack(side='right', expand='true')

        [self.tab6Bt1,self.tab6Bt2, self.tab6Bt3, self.tab6Bt4] = creatTab.CRT.drawLeftTab(self.tab6Frame1, ['', '', '', 'SHUTDOWN'],
                                 ['disable', 'disable', 'disable', 'normal'],['grey', 'grey', 'grey', 'cyan'])
        [self.tab6Bt5,self.tab6Bt6, self.tab6Bt7, self.tab6Bt8] = creatTab.CRT.drawRightTab(self.tab6Frame3, ['', '', '', 'CONFIRM'],
                                  ['disable', 'disable', 'disable', 'normal'],['grey','grey','grey','cyan'])
        self.tab6Bt4.configure(width=70, height=120, image=self.tab6Photo1, compound="top")
        self.tab6Bt8.configure(width=70,height=130, image=self.tab1Photo2, compound="top")

#tab6 button

        self.photo = PhotoImage(file="/home/pi/Downloads/project/image/motor.gif")
        self.photo1 = PhotoImage(file="/home/pi/Downloads/project/image/turbine.gif")
        self.photo2= PhotoImage(file="/home/pi/Downloads/project/image/motor.gif")
        self.photo3 = PhotoImage(file="/home/pi/Downloads/project/image/motor.gif")
        self.imageButton1 = Tk.Button(self.tab6Frame2,text="", width=190, height=190, activebackground='blue',
                                      bg="white",image=self.photo,state='normal')
        self.imageButton1.grid(column=0, row=0,sticky='w')
        self.imageButton2 = Tk.Button(self.tab6Frame2,text="", width=190, height=190, activebackground='blue',
                                      bg="white",image=self.photo1,state='normal')
        self.imageButton2.grid(column=1, row=0,sticky='w')
        self.imageButton3 = Tk.Button(self.tab6Frame2,text="", width=190, height=190, activebackground='blue',
                                      bg="white",image=self.photo,state='normal')
        self.imageButton3.grid(column=2,row=0,sticky='w')
        self.imageButton4 = Tk.Button(self.tab6Frame2,text="", width=190, height=190, activebackground='blue',
                                      bg="white",image=self.photo,state='normal')
        self.imageButton4.grid(column=3,row=0, sticky='w')

        self.driveCheck = Tk.IntVar()
        self.gearBoxCheck = Tk.IntVar()
        self.drivenCheck = Tk.IntVar()
        self.driveCheck.set(0)
        self.gearBoxCheck.set(0)
        self.drivenCheck.set(0)
        self.content1 = Tk.StringVar()
        self.content2 = Tk.StringVar()
        self.labelFrame1=Tk.LabelFrame(self.tab6Frame2, text="Driver unit",bg='white')
        self.labelFrame1.grid(column=0,row=1,sticky="W", padx=5, pady=5,columnspan=4)
        self.ratioButton1=Tk.Checkbutton(self.labelFrame1, text="Electric Motor",offvalue=0,onvalue=1,
                                         variable=self.driveCheck,bg='white')
        self.ratioButton1.grid(column=0,row=0, padx=60)
        self.ratioButton2=Tk.Checkbutton(self.labelFrame1, text="Turbine",offvalue=0,onvalue=2,variable=self.driveCheck,bg='white')
        self.ratioButton2.grid(column=1,row=0, padx=70)
        self.ratioButton3=Tk.Checkbutton(self.labelFrame1, text="Fan",offvalue=0,onvalue=3,variable=self.driveCheck,bg='white')
        self.ratioButton3.grid(column=2,row=0, padx=70)
        self.ratioButton4=Tk.Checkbutton(self.labelFrame1, text="Other",offvalue=0,onvalue=4,variable=self.driveCheck,bg='white')
        self.ratioButton4.grid(column=3,row=0, padx=30)

        self.rpmLabel=Tk.Label(self.labelFrame1,text="RPM",bg='white')
        self.rpmLabel.grid(column=0,row=1,padx=70,sticky='w')
        self.powerLabel = Tk.Label(self.labelFrame1, text="POWER(kW)",bg='white')
        self.powerLabel.grid(column=0, row=2, padx=70, sticky='w')
        self.rpmEntry=Tk.Entry(self.labelFrame1,width=15, textvariable=self.content1,bg='white')
        self.rpmEntry.grid(column=1,row=1)
        self.powerEntry=Tk.Entry(self.labelFrame1,width=15, textvariable=self.content2,bg='white')
        self.powerEntry.grid(column=1,row=2)

        self.labelFrame2=Tk.LabelFrame(self.tab6Frame2, text="Gear box",bg='white')
        self.labelFrame2.grid(column=0,row=2,sticky="W", padx=5, pady=5,columnspan=4)
        self.ratioButton5=Tk.Checkbutton(self.labelFrame2, text="No gear box",offvalue=0,onvalue=1,
                                         variable=self.gearBoxCheck,bg='white')
        self.ratioButton5.grid(column=0,row=2, padx=60)
        self.ratioButton6=Tk.Checkbutton(self.labelFrame2, text="Use gear box",offvalue=0,onvalue=2,
                                         variable=self.gearBoxCheck,bg='white')
        self.ratioButton6.grid(column=1,row=2, padx=78)

        self.labelFrame3=Tk.LabelFrame(self.tab6Frame2, text="Driven unit",background='white')
        self.labelFrame3.grid(column=0,row=3,sticky="W", padx=5, pady=5,columnspan=4)
        self.ratioButton7=Tk.Checkbutton(self.labelFrame3, text="Pump",offvalue=0,onvalue=1,variable=self.drivenCheck,bg='white')
        self.ratioButton7.grid(column=0,row=0, padx=60)
        self.ratioButton8=Tk.Checkbutton(self.labelFrame3, text="Fan",offvalue=0,onvalue=2,variable=self.drivenCheck,bg='white')
        self.ratioButton8.grid(column=1,row=0, padx=110)
        self.ratioButton9=Tk.Checkbutton(self.labelFrame3, text="Mixer",offvalue=0,onvalue=3,variable=self.drivenCheck,bg='white')
        self.ratioButton9.grid(column=2,row=0, padx=60)
        self.ratioButton10=Tk.Checkbutton(self.labelFrame3, text="Generator",offvalue=0,onvalue=4,
                                          variable=self.drivenCheck,bg='white')
        self.ratioButton10.grid(column=3,row=0, padx=30)

        fig1 = creatTab.CRT.creatFigure(self.tab1,3)
        fig2 = creatTab.CRT.creatFigure(self.tab2,3)
        fig1.set_visible(False)
        fig2.set_visible(False)
        self.canvas1=FigureCanvasTkAgg(fig1,master=self.tab1Frame2)
        self.canvas1.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.toolbar=NavigationToolbar2Tk(self.canvas1,self.tab1Frame2)
        self.toolbar.update()
        self.canvas1._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        self.canvas2 = FigureCanvasTkAgg(fig2,master=self.tab2Frame2)
        self.canvas2.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2,self.tab2Frame2)
        self.toolbar2.update()
        self.canvas2._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        date_arr=[1,2,3]
        rms_arr2 = 1.4 * np.ones(3)
        rms_arr3 = 1.4 * np.ones(3)
        rms_arr4 = 1.7 * np.ones(3)
        rms_arr5 = 20.5 * np.ones(3)
        # fig4 = plt.Figure(figsize=(8.4, 8))
        # ax_41 = fig4.add_subplot()
        fig4 = Figure(figsize=(8.1,8))
        ax_41= fig4.add_subplot(1,1,1)
        ax_41.stackplot(date_arr, rms_arr2, rms_arr3, rms_arr4,rms_arr5, colors=['green', 'yellow', 'orange','red'],
                        labels=['new', 'accept', 'warning','fault'])
        ax_41.set_xlabel('time')
        ax_41.set_ylabel('Standard Velocity RMS value ISO-10816 (mm/s)')
        ax_41.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.0)
        ax_41.grid()
        self.canvas4 = FigureCanvasTkAgg(fig4,master=self.tab4Frame2)
        self.canvas4.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.toolbar4 = NavigationToolbar2Tk(self.canvas4,self.tab4Frame2)
        self.toolbar4.update()
        self.canvas4._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        fig5=plt.figure(figsize=(8.1,8))
        fig5.add_subplot(1,1,1,projection='polar', autoscale_on=True)
        self.canvas5 = FigureCanvasTkAgg(fig5, master=self.tab5Frame2)
        self.canvas5.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.toolbar5 = NavigationToolbar2Tk(self.canvas5, self.tab5Frame2)
        self.toolbar5.update()
        self.canvas5._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

    def read_i2c_ch1(self):
        data = self.bus1.read_i2c_block_data(self.i2c_address1, 0x00, 7)
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
        # print('X direction: %d', xAccl)
        # print('Y direction: %d', yAccl)
        # print('Z direction: %d', zAccl)
        # global binh1,binh2,binh3
        # binh1.append(xAccl)
        # binh2.append(yAccl)
        # binh3.append(zAccl)
        return [xAccl,yAccl,zAccl]


    def read_i2c_ch2(self):
        data = self.bus2.read_i2c_block_data(self.i2c_address2, 0x00, 7)
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
        # print('X direction: %d', xAccl)
        # print('Y direction: %d', yAccl)
        # print('Z direction: %d', zAccl)
        # global binh1,binh2,binh3
        # binh1.append(xAccl)
        # binh2.append(yAccl)
        # binh3.append(zAccl)
        return [xAccl,yAccl,zAccl]


    def creatThread(self):
        runT = Thread(target=self.read_data1)
        # runT.setDaemon(True)
        runT.start()
        runT.join()

    def creatThread2(self):
        runT2 = Thread(target=self.read_data1)
        # runT2.setDaemon(True)
        runT2.start()
        runT2.join()
    def read_i2c(self):
        self.i2c_config()
        time.sleep(2)
        global g_chanel_1, g_chanel_2, g_chanel_3, data_length
        chanel1 = []
        chanel2 = []
        chanel3 = []
        countt = 0
        timeout_state = False
        t0 = time.time()
        t1 = t0
        while ((countt < data_length) and (timeout_state == False)):
            if ((time.time() - t0) >= 0.00125):
                t0 = time.time()
                # self.creatThread()
                [xAcc1, yAcc1, zAcc1]=self.read_i2c_ch1()
                [xAcc2, yAcc2, zAcc2] = self.read_i2c_ch2()
                chanel1.append(zAcc1)
                chanel2.append(zAcc2)
                chanel3.append(xAcc2)
                countt += 1
                # print("Canal 1: %2.4s    Canal2: %2.4s  Canal: %2.4s " % (xAccl, yAccl, zAccl))
            else:
                pass
            if (time.time() - t1) > t_timeout:
                timeout_state = True
        if (timeout_state == False):
            print(time.time() - t1)
            # print("Sending PAR")
            # print("Amount of samples channel 1: %s" % len(chanel1))
            # print("Amount of samples channel 2: %s" % len(chanel2))
            # print("Amount of samples channel 3: %s" % len(chanel3))
            # Keep a copy of the original values
            # global binh1, binh2, binh3
            g_chanel_1 = chanel1[:]  # Copy list by value not by reference
            g_chanel_2 = chanel2[:]
            g_chanel_3 = chanel3[:]

            self.f_saved = False  # Sampled data not saved
            Pd.PLT.plot_all_chanel(self.canvas1, chanel1, chanel2, chanel3)
            Pd.PLT.plot_fft(self.canvas2, chanel1, chanel2, chanel3, win_var=1)
            Pd.PLT.plot_rms(self.canvas4, [chanel1, chanel2, chanel3])
            # binh1=[]
            # binh2=[]
            # binh3=[]
        else:
            print("Serial port timeout")
            message_string = ("Serial port timeout \n")

    def read_spi(self):
        ADC = ADS1256.ADS1256()
        ADC.ADS1256_init()
        time.sleep(1)
        global g_chanel_1, g_chanel_2, g_chanel_3, data_length
        chanel1 = []
        chanel2 = []
        chanel3 = []
        countt = 0
        timeout_state = False
        t0 = time.time()
        t1 = t0
        while ((countt < data_length) and (timeout_state == False)):
            if ((time.time() - t0) >= 0.02):
                t0 = time.time()
                # self.creatThread()
                ADC_Value = ADC.ADS1256_GetChannalValue(7)
                gt1=(ADC_Value*5.0/0x7fffff)/120*1000
                # print(gt1)
                chanel1.append(gt1*1.5625-6.5)
                chanel2.append(gt1*1.5625-6.5)
                chanel3.append(gt1*1.5625-6.5)
                countt += 1
                # print("Canal 1: %2.4s    Canal2: %2.4s  Canal: %2.4s " % (ADC_Value*5.0/0x7fffff, ADC_Value, ADC_Value))
            else:
                pass
            if (time.time() - t1) > t_timeout:
                timeout_state = True
        if (timeout_state == False):
            print(time.time() - t1)
            # print("Sending PAR")
            # print("Amount of samples channel 1: %s" % len(chanel1))
            # print("Amount of samples channel 2: %s" % len(chanel2))
            # print("Amount of samples channel 3: %s" % len(chanel3))
            # Keep a copy of the original values
            # global binh1, binh2, binh3
            g_chanel_1 = chanel1[:]  # Copy list by value not by reference
            g_chanel_2 = chanel2[:]
            g_chanel_3 = chanel3[:]

            self.f_saved = False  # Sampled data not saved
            Pd.PLT.plot_all_chanel(self.canvas1, chanel1, chanel2, chanel3)
            Pd.PLT.plot_fft(self.canvas2, chanel1, chanel2, chanel3, win_var=1)
            Pd.PLT.plot_rms(self.canvas4, [chanel1, chanel2, chanel3])
            # binh1=[]
            # binh2=[]
            # binh3=[]
        else:
            print("Serial port timeout")
            message_string = ("Serial port timeout \n")
    def i2c_config(self):

        mma8451_reg_ctrl1 = 0x2A
        mma8451_reg_ctrl2 = 0x2B
        mma8451_reg_ctrl4 = 0x2A
        mma8451_reg_ctrl5 = 0x2A
        mma8451_reg_xyz_data_cfg = 0x0E

        self.bus1.write_byte_data(self.i2c_address1, mma8451_reg_ctrl2, 0x40)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, mma8451_reg_xyz_data_cfg, 0x00)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, mma8451_reg_ctrl2, 0x01)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, mma8451_reg_ctrl4, 0x01)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, mma8451_reg_ctrl5, 0x01)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, mma8451_reg_ctrl1, 0x04 | 0x01)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, 0x11, 0x40)
        time.sleep(0.1)
        self.bus1.write_byte_data(self.i2c_address1, 0x0F, 0x20)
        time.sleep(0.1)

        self.bus2.write_byte_data(self.i2c_address2, mma8451_reg_ctrl2, 0x40)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, mma8451_reg_xyz_data_cfg, 0x00)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, mma8451_reg_ctrl2, 0x01)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, mma8451_reg_ctrl4, 0x01)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, mma8451_reg_ctrl5, 0x01)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, mma8451_reg_ctrl1, 0x04 | 0x01)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, 0x11, 0x40)
        time.sleep(0.1)
        self.bus2.write_byte_data(self.i2c_address2, 0x0F, 0x20)
        time.sleep(0.1)

if __name__ == '__main__':
    root = Tk.Tk()
    #root.iconbitmap(r"/home/pi/Downloads/project/image/otani_icon.ico")
    root.geometry("1024x600")
    root.resizable(0,0)
    #root.config(cursor='none')
    # style = ttk.Style()
    # style.configure("TNotebook", background='red', foreground='green')
    # style.theme_create("MyStyle", parent="alt", settings={
    #     "TNotebook": {"configure": {"tabmargins": [12, 5, 5, 0]}},
    #     "TNotebook.Tab": {"configure": {"padding": [105, 20]},}})
    #
    # style.theme_use("MyStyle")
    # root.wm_attributes('-fullscreen','true')
    # root.attributes('-fullscreen', True)
    # root.call("wm", "attributes", ".", "-fullscreen", "true")  # Fullscreen mode
    root.title('OTANI-UP FFT ANALYSER')
    app = Application(root)
    root.mainloop()