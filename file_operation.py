from tkinter import filedialog
import tkinter as Tk
import Plot_data
sample_rate=1000
def simpleParse(mainString, beginString, endString):
    """Searches for a substring between beginString and endString lay """
    posBeginString = mainString.find(beginString) + len(beginString)
    posEndString = mainString.find(endString)
    resultado = mainString[posBeginString:posEndString]
    return resultado


# input: string, preceeding tag and post tag
# output: array of number that store the sensor data
def extraer_int_tag(datos_arch, tag):
    """ Extracts data from string datos_str, delimited by <tag> y </tag>
        and convets it to integer numbers (list of integers)"""
    str_canal = ''
    beginString = '<' + tag + '>'
    endString = '</' + tag + '>'
    str_parse = simpleParse(datos_arch, beginString, endString)
    str_canal = str_parse.split(',')

    canal = []
    n = len(str_canal)
    for i in range(n):
        canal.append(float(str_canal[i]))
    return canal


def conv_str_tag(canal, tag):
    """ Convert every channel from int to str, separated by a coma
    and adds tags at the beggining and end. """
    n = len(canal)
    s_canal = '<' + tag + '>'
    for i in range(n - 1):
        s_canal = s_canal + str(canal[i]) + ','
    s_canal = s_canal + str(canal[n - 1]) + '</' + tag + '>'
    return s_canal


def grabar(canal_1, canal_2, canal_3, archivo):
    """ Saves X and Y axis data on file archivo"""
    str_canal = ''
    str_canal += conv_str_tag(canal_1, 'L1') + '\n'
    str_canal += conv_str_tag(canal_2, 'L2') + '\n'
    str_canal += conv_str_tag(canal_3, 'L3') + '\n'

    str_aux = ''
    str_aux += '<nd>' + str(len(canal_1)) + '</nd>' + '\n'
    str_aux += '<sr>' + str(sample_rate) + '<sr>' + '\n'
    # str_aux += '<gn>' + str(ganancia) + '</gn>' + '\n'

    # Write to file
    arch = open(archivo, "w")
    arch.write(str_aux)
    arch.write(str_canal)
    arch.close()
class FileOperation():
    def __init__(self, parent):
        self.parent = parent
    def open_and_read(self):
        ftypes = [('Text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self.parent, filetypes=ftypes)
        fl1 = dlg.show()
        array1 = []
        date_arr = []
        if fl1 != '':
            file1 = open(fl1, "r")
            data = file1.readlines()
            # print(data[3])
            for line in range(2, len(data)):
                temp_arr = extraer_int_tag(data[line], 'L1')
                temp_date = extraer_int_tag(data[line], 'D')
                array1.append(temp_arr)
                date_arr.append(temp_date)
            array1.append(date_arr)
        return array1