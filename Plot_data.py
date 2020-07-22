import tkinter as Tk
import calculate
import numpy as np
from scipy import fftpack, signal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import dates
from datetime import datetime
#import xulydata
import matplotlib.pyplot as plt
sample_rate = 800
max_freq = sample_rate / 2
max_freq_z = sample_rate / 2
class PLT(FigureCanvasTkAgg):
    def plot1chanel(self, canal, ch):
        num_datos = len(canal)
        X = range(0, num_datos, 1)
        # Calculates medium value for each channel.
        vdc_canal_1 = 0

        for indice in X:
            vdc_canal_1 += canal[indice]
        vdc_canal_1 = vdc_canal_1 / num_datos
        # print("Vdc Channel 1: {0}, Vdc Channel 2: {1}".format(vdc_canal_1, vdc_canal_2))
        # dua ve gia tri trung binh 0
        # Substract DC offset
        for indice in X:
            canal[indice] -= 0

        # ----------------- Plotting ----------
        X1 = np.linspace(0, 2*int(num_datos), num_datos)  # X axis, 5000 sps, 1/5 ms.

        # Figure 1. Sampled signals.
        # Channel X
        rms_valX = calculate.rmsValue(canal)
        titX = "Ch " + str(ch) + "|RMS: " + str(rms_valX)[:5] + ' mm/s'
        ax_11, ax_12, ax_13 = self.figure.get_axes()
        self.figure.delaxes(ax_13)
        self.figure.subplots_adjust(top=0.95, bottom=-0.3)
        ax_11.clear()
        ax_11.plot(X1, canal, color='blue', linewidth=0.4)
        # ax_11.set_title(titX)
        ax_11.set_ylabel(titX)
        ax_11.grid()  # Shows grid.
        canal_fft = []
        canal_fft = canal

        N = len(canal_fft)  # length of the signal

        # Window function
        w = signal.hann(N, sym=False)  # Hann (Hanning) window

        T = 1.0 / sample_rate
        y = canal_fft
        yf = fftpack.fft(y * w) * (2 / N)
        yf = yf[2:(int(N / 2))]
        # kenh1=yf
        xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
        # print(xf[:10])
        ax_12.clear()
        # ax_21.plot(xf, 2.0/N * np.abs(yf[:N/2]))
        ax_12.plot(xf[2:], np.abs(yf), color='blue', linewidth=0.5)
        ax_12.grid()
        ax_12.set_title("ms")
        ax_12.set_ylabel('Amplitude mm/s')
        ax_12.set_xlabel('hz')
        ax_12.set_xlim(xmax=max_freq)
        self.draw()
        self.figure.add_axes(ax_13)
        self.figure.subplots_adjust(left=0.1, right=0.91, top=0.95, bottom=0.1)

    def plot_all_chanel(self, canal_1, canal_2, canal_3):

        num_datos = len(canal_1)
        X = range(0, num_datos, 1)
        vdc_canal_1 = 0
        vdc_canal_2 = 0
        vdc_canal_3 = 0
        for indice in X:
            vdc_canal_1 += canal_1[indice]
            vdc_canal_2 += canal_2[indice]
            vdc_canal_3 += canal_3[indice]

        vdc_canal_1 = vdc_canal_1 / num_datos
        vdc_canal_2 = vdc_canal_2 / num_datos
        vdc_canal_3 = vdc_canal_3 / num_datos
        # print("Vdc Channel 1: {0}, Vdc Channel 2: {1}".format(vdc_canal_1, vdc_canal_2))
        # dua ve gia tri trung binh 0
        # Substract DC offset
        for indice in X:
            canal_1[indice] -= 0
            canal_2[indice] -= 0
            canal_3[indice] -= 0

        # ----------------- Plotting ----------
        X1 = np.linspace(0, int(num_datos), num=num_datos)  # X axis, 5000 sps, 1/5 ms.

        # Figure 1. Sampled signals.
        # Channel X
        rms_valX = calculate.rmsValue(canal_1)
        rms_valY = calculate.rmsValue(canal_2)
        rms_valZ = calculate.rmsValue(canal_3)
        titX = "Ch1" + "|RMS: " + str(rms_valX)[:5] + ' mm/s'
        titY = "Ch2" + "|RMS: " + str(rms_valY)[:5] + ' mm/s'
        titZ = "Ch3" + "|RMS: " + str(rms_valZ)[:5] + ' mm/s'
        # if len(self.canvas1.figure.get_axes()):
        # self.canvas1.figure.add_axes(self.ax_13)
        ax_11, ax_12, ax_13 = self.figure.get_axes()
        self.figure.set_visible(True)
        ax_11.clear()
        ax_11.plot(X1, canal_1, color='blue', linewidth=0.4)
        # ax_11.set_title(titX)
        ax_11.set_ylabel(titX)
        ax_11.grid()  # Shows grid.

        # Channel Y
        ax_12.clear()
        ax_12.plot(X1, canal_2, color='blue', linewidth=0.4)
        # ax_12.set_title(titY)
        ax_12.set_ylabel(titY)
        # ax_12.set_xlabel('ms')
        ax_12.grid()  # Shows grid.

        # Channel Z
        ax_13.clear()
        ax_13.plot(X1, canal_3, color='blue', linewidth=0.4)
        # ax_13.set_title(titZ)
        # ax_13.set_xlabel(titZ)
        ax_13.set_ylabel(titZ)
        ax_13.grid()  # Shows grid.
        self.draw()

    def plot_fft(self, canal_1, canal_2, canal_3, win_var=1):
        # Calculates medium value for each channel.
        canal_fft = canal_1
        N = len(canal_fft)  # length of the signal
        # Window function
        w = signal.hann(N, sym=False)  # Hann (Hanning) window

        T = 1.0 / sample_rate
        y = canal_fft
        yf = fftpack.fft(y * w) * (2 / N)
        yf = yf[2:(int(N / 2))]
        yyf=np.abs(yf)
        print('vi tri max 1= %d',calculate.find_max(yyf))
        xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
        ax_21, ax_22, ax_23 = self.figure.get_axes()
        self.figure.set_visible(True)
        ax_21.clear()
        ax_21.plot(xf[2:], np.abs(yf), color='blue', linewidth=0.5)
        ax_21.grid()
        ax_21.set_title("Ch1")
        ax_21.set_ylabel('Amplitude mm/s')
        ax_21.set_xlim(xmax=max_freq)

        # Channel Y
        canal_fft = []
        canal_fft = canal_2

        N = len(canal_fft)  # length of the signal
        T = 1.0 / sample_rate
        y = canal_fft
        yf = fftpack.fft(y * w) * (2 / N)
        yf = yf[2:int(N / 2)]
        xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))

        ax_22.clear()
        ax_22.plot(xf[2:], np.abs(yf), color='blue', linewidth=0.5)
        ax_22.grid()
        ax_22.set_title("Ch2")
        # ax_22.set_xlabel('Hz')
        ax_22.set_xlim(xmax=max_freq)
        ax_22.set_ylabel('Amplitude mm/s')

        # Channel Z
        canal_fft = []
        canal_fft = canal_3

        N = len(canal_fft)  # length of the signal
        T = 1.0 / sample_rate
        y = canal_fft
        yf = fftpack.fft(y * w) * (2 / N)
        yf = yf[2:int(N / 2)]
        xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
        ax_23.clear()
        # ax_23.plot(xf, 2.0/N * np.abs(yf[:N/2]))
        ax_23.plot(xf[2:], np.abs(yf), color='blue', linewidth=0.5)
        ax_23.grid()
        ax_23.set_title("Ch3")
        ax_23.set_xlabel('Hz')
        # ax_23.set_xlim(xmax=max_freq)
        ax_23.set_xlim(xmax=max_freq_z)
        ax_23.set_ylabel('Amplitude mm/s')
        self.draw()

    def plot_all_history(self, arr, d_arr, win_var=1):
        h_num = len(arr)
        N = len(arr[0])  # length of the signal
        T = 1.0 / sample_rate
        axes_arr=[]
        axes_arr = self.figure.get_axes()
        # print(len(axes_arr))
        # cc=len(axes_arr)
        # while cc>h_num:
        #     self.figure.delaxes(axes_arr[cc-1])
        #     cc-=1
        # axes_arr = self.figure.get_axes()
        xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
        zf = []
        w = signal.hann(N, sym=False)  # Hann (Hanning) window
        for i in range(0, h_num):
            y = arr[i]
            yf = fftpack.fft(y * w) * (2 / N)
            yf = yf[2:int(N / 2)]
            axes_arr[i].plot(xf[2:], np.abs(yf), color='blue', linewidth=0.5)
            axes_arr[i].grid()
            axes_arr[i].yaxis.set_ticks([])
            if i<h_num-1:
                axes_arr[i].xaxis.set_ticks([])
            date= datetime.fromtimestamp(int(d_arr[i][0]))
            axes_arr[i].set_ylabel(str(date)[:10]+'|')
            # print((d_arr[i][0]))
            # print(date)
        self.draw()
    def plot_trend(self,arr, d_arr):
        h_num = len(arr)
        N = len(arr[0])  # length of the signal
        T = 1.0 / sample_rate
        hfmt = dates.DateFormatter('%Y-%m-%d')
        # Window function
        rms_arr = []
        rms_arr2 = 1.4 * np.ones(h_num)
        rms_arr3 = 1.4 * np.ones(h_num)
        rms_arr4 = 1.7 * np.ones(h_num)
        rms_arr5 = 20.5 * np.ones(h_num)
        date_arr = []
        for i in range(0, h_num):
            rms_arr.append(calculate.rmsValue(arr[i]))

            date_arr.append(d_arr[i][0])
        ax_41, = self.figure.get_axes()
        ax_41.clear()
        # labels = ["Fibonacci ", "Evens", "Odds"]'
        ax_41.stackplot(date_arr,rms_arr2,rms_arr3,rms_arr4,rms_arr5,colors=['green','yellow','orange','red'],labels=['new','accept','warning','fault'])
        ax_41.plot(date_arr, rms_arr, color="blue", label="RMS Value")
        ax_41.set_title("RMS BELONG TIME")
        ax_41.set_xlabel('time')
        ax_41.set_ylabel('Standard Velocity RMS value ISO-10816 (mm/s)')
        ax_41.xaxis.set_major_locator(dates.AutoDateLocator())
        ax_41.xaxis.set_major_formatter(hfmt)
        ax_41.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.0)
        # labels = 'MISALIGMENT', 'BELT', 'UNBALANCE', 'LOOSE', 'BENT SHAFT'
        # sizes = [67, 20, 10, 5, 5]
        # explode = (0.1, 0.1, 0.1, 0.1, 0.1)  # only "explode" the 2nd slice (i.e. 'Hogs')
        # ax_43.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        #           shadow=True, startangle=90)
        # ax_43.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        # ax_43.set_title('Fault type')
        self.draw()

    def plot_rms(self, arr, win_var=1):
        h_num = len(arr)
        rms_arr = []
        rms_arr2 = 1.4 * np.ones(h_num)
        rms_arr3 = 1.4 * np.ones(h_num)
        rms_arr4 = 1.7 * np.ones(h_num)
        rms_arr5 = 20.5 * np.ones(h_num)
        date_arr = []
        for i in range(1,h_num+1):
            date_arr.append(i)
        for i in range(0, h_num):
            rms_arr.append(calculate.rmsValue(arr[i]))
        ax_41, = self.figure.get_axes()
        ax_41.clear()
        ax_41.stackplot(date_arr, rms_arr2, rms_arr3, rms_arr4,rms_arr5, colors=['green', 'yellow', 'orange','red'],
                        labels=['new', 'accept', 'warning','fault'])
        ax_41.plot(date_arr, rms_arr, color="blue", label="RMS Value")
        ax_41.set_title("Velocity RMS: "+str(rms_arr[0])[0:4])
        ax_41.set_xlabel('time')
        ax_41.set_ylabel('Standard Velocity RMS value ISO-10816 (mm/s)')
        ax_41.legend(bbox_to_anchor=(1, 1), loc='upper right', borderaxespad=0.0)
        self.draw()
    def plot_polar(self):
        xs = [0, 3.14]
        org = [2.6, 6.5, 1.9]
        trial = org[1:3]
        vt = np.sqrt((org[1] ** 2 + org[2] ** 2 - 2 * (org[0] ** 2)) / 2)
        amp = [vt, vt]
        theta = np.arccos((org[1] ** 2 - org[2] ** 2) / (4 * vt * org[0]))
        mcom = org[0] * 10 / vt
        # print(trial)
        # print("vt=", vt)
        # print('theta=', theta)
        ax_51 = self.figure.get_axes()
        ax_51.clear()
        for x1, y1 in zip(xs, amp):
            plt.polar(x1, y1, "*")
            plt.text(x1, y1, '(%0.2f, %0.1f)' % (x1, y1))

        plt.polar(theta, org[0], "*")
        plt.text(theta, org[0], '(%0.2f, %0.1f)' % (theta, org[0]))

        plt.polar(theta + np.pi, org[0], "*")
        plt.text(theta + np.pi, org[0], '(comp mass %0.2f, %0.1f, %0.1f)' % (theta + np.pi, org[0], mcom))
        plt.plot([0, theta + np.pi], [0, org[0]], '-y')
        plt.plot([0, 0], [0, vt], '-g')
        plt.plot([0, np.pi], [0, vt], '-b')
        plt.plot([0, theta], [0, org[0]], '-r')
        self.draw()


