from sys import argv
script, Element, Type, Fstart, Fstop, Points, output_file = argv

import serial
import struct
from math import *
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

Fstart = eval(Fstart)
Fstop = eval(Fstop)
Points = eval(Points)
Step = int((Fstop - Fstart) / Points)

if Type == 'plast':
    l, s, b, p = eval(input(">> L, S, B, p = "))

elif Type == 'brus':
    l, s, b, b1, p = eval(input(">> L, S, B, B1, p = "))

elif Type == 'sterzh':
    l, w, p = eval(input(">> L, W, p = "))

elif Type == 'shaiba':
    l, D, d, p = eval(input(">> L, D, d, p = "))

elif Type == 'disk':
    l, D, p = eval(input(">> L, D, p = "))

elif Type == 'trubka':
    l, D, d, p = eval(input(">> L, D, d, p = "))


# Конфигурация порта
ser = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1.2
)

#---------------------Команды-------------------------
default = (0xAA, 71) # Состояние по-умолчанию
parameters = (0xAA, 72) # Выдача измеряемой информации
scheme = (0xAA, 0x0d) # Смена схемы замещения
#-----------------------------------------------------

def set_default():
    """Проверки и перевод прибора в состояние по-умолчанию"""

    try:

        if ser.isOpen():

            ser.write(default)
            checkout = ser.read(2)

            if struct.unpack('>2B', checkout) == default:
                ser.read(4)

        else:
            print(">> Неполадки с портом\n")

    except struct.error:
        print(">> Нет соединения с прибором\n")


def calc_C():
    """Вычисление ёмкости и тангенса"""

    global c, tg, z

    ser.write(parameters)
    data = struct.unpack('>3B3bhiff', ser.read(20))

    f, z, fi = data[7], data[8], data[9]

    c = 1 / (2 * pi * f * abs(z) * sin(-fi))
    tg = 2 * pi * f * c * abs(z) * cos(-fi) * 100
    print("\n>> Cэл = ",c, " Ф")
    print("   tg = %.2f %%\n   Z = %.2f Ом\n" % (tg, z))


def change_scheme():
    """Изменение схемы замещения"""

    ser.write(scheme)
    check_scheme = ser.read(2)

    if struct.unpack('>2B', check_scheme) == scheme:
        ser.read(2)


def set_freq(F):
    """Установка частоты"""


    if F // 256 > 256:
        f1 = 0
        f2 = F // 256 // 256
        f3 = F // 256 % 256
        f4 = F % 256

    else:
        f1 = 0
        f2 = 0
        f3 = F // 256
        f4 = F % 256

    freq = (0xAA, 67, f1, f2, f3, f4)
    ser.write(freq)
    ser.read(4)


def calc_all():
    """Измерение всех величин"""

    global Gp,Gs,Rp,Rs,Fp,Fa,df,Gp_list,Gs_list,Rp_list,Rs_list,Cp_list,Cs_list,Z_list

    Gp_list = []
    Gs_list = []
    Rp_list = []
    Rs_list = []
    Cp_list = []
    Cs_list = []
    Z_list = []

    change_scheme()

    for i in range(Fstart, Fstop + Step, Step):

        set_freq(i)

        ser.write(parameters)
        data = struct.unpack('>3B3bhiff', ser.read(20))

        f, z, fi = data[7], data[8], data[9]

        Gp_list.append(cos(fi) / abs(z))
        Rp_list.append(abs(z) / cos(fi))
        Cp_list.append(sin(fi) / (2 * pi * f))


    change_scheme()

    for i in range(Fstart, Fstop + Step, Step):

        set_freq(i)

        ser.write(parameters)
        data = struct.unpack('>3B3bhiff', ser.read(20))

        f, z, fi = data[7], data[8], data[9]

        Gs_list.append(1 / (abs(z) * cos(-fi)))
        Rs_list.append(abs(z) * cos(-fi))
        Cs_list.append(1 / (2 * pi * f * abs(z) * sin(-fi)))
        Z_list.append(z)

    Gp = max(Gp_list)
    Gs = min(Gs_list)
    Rp = min(Rp_list)
    Rs = max(Rs_list)

    Fp_index = Gp_list.index(Gp)
    axis_Fp = list(range(Fstart, Fstop + Step, Step))
    Fp = axis_Fp[Fp_index]

    Fa_index = Gs_list.index(Gs)
    axis_Fa = list(range(Fstart, Fstop + Step, Step))
    Fa = axis_Fa[Fa_index]

    df = Fa - Fp

    print(">> Параметры, измеренные программно:\n   Fр = %.2f Гц\n   Fa = %.2f Гц\n   Gp = %.6f См\n   Gs = %.6f См\n   Rp = %.2f Ом\n   Rs = %.2f Ом\n" % (Fp,Fa,Gp,Gs,Rp,Rs))


def on_key(event):
    """Функция для взаимодействия (выделения резонанса и антирезонанса) через клавиатуру при работе с графиком"""

    global Fp, Fa, Gp, Gs, df, check_key


    if event.key == '1':
        print(">> Параметры по отметке из графика:\n   Fр = %.2f Гц\n   Gp = %.6f См\n" % (event.xdata, event.ydata))
        Fp = event.xdata
        Gp = event.ydata


    elif event.key == '2':
        print(">> Параметры по отметке из графика:\n   Fa = %.2f Гц\n   Gs = %.6f См\n" % (event.xdata, event.ydata))
        Fa = event.xdata
        Gs = event.ydata
        df = Fa - Fp
        check_key = 1


    elif event.key == '3':
        print(">> Параметры по отметке из графика:\n   Fp = %.2f Гц\n   Rp = %.2f Ом\n" % (event.xdata, event.ydata))
        Fp = event.xdata
        Rp = event.ydata


    elif event.key == '4':
        print(">> Параметры по отметке из графика:\n   Fa = %.2f Гц\n   Rs = %.2f Ом\n" % (event.xdata, event.ydata))
        Fa = event.xdata
        Rs = event.ydata



def make_plot(Gp, Gs, Rp, Rs, Z, Cp, Cs):
    """Составление графика"""

    x = list(range(Fstart, Fstop + Step, Step))
    yGp = Gp
    yGs = Gs
    yRp = Rp
    yRs = Rs
    yZ = Z
    yCp = Cp
    yCs = Cs

    figure, ((ax0,ax1),(ax2,ax3)) = plt.subplots(nrows=2, ncols=2, figsize=(12,7))
    ax0.plot(x, yGp, 'b', label='Gp')
    ax0.plot(x, yGs, 'r', label='Gs')
    ax1.plot(x, yRp, 'b', label='Rp')
    ax1.plot(x, yRs, 'r', label='Rs')
    ax2.plot(x, yZ, 'b', label='Z')
    ax3.plot(x, yCp, 'b', label='Cp')
    ax3.plot(x, yCs, 'r', label='Cs')
    ax0.legend()
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax0.set_xlabel("F, Гц")
    ax0.set_ylabel("G, См")
    ax1.set_xlabel("F, Гц")
    ax1.set_ylabel("R, Ом")
    ax2.set_xlabel("F, Гц")
    ax2.set_ylabel("Z, Ом")
    ax3.set_xlabel("F, Гц")
    ax3.set_ylabel("C, Ф")
    ax0.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
    ax0.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
    ax1.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
    ax1.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
    ax2.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
    ax2.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
    ax3.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
    ax3.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
    ax0.minorticks_on()
    ax1.minorticks_on()
    ax2.minorticks_on()
    ax3.minorticks_on()
    plt.tight_layout()
    cid = figure.canvas.mpl_connect('key_press_event', on_key)
    plt.show()


def plast(l, s, b, p, c, df, Fp, Fa, Gp, Gs):
    """Расчет параметров пьезоэлемента формы пластины"""

    global e33, d31, v1, ksv

    e33 = 113 * 10**9 * ((c * b) / (l * s))
    d31 = 2.34 * 10**(-6) * sqrt(e33 * (df / (l**2 * p * Fp**3)))
    v1 = 2 * l * Fp
    ksv = sqrt((1 - (Fp / Fa)**2) * ((Gp - Gs)/(Gp + Gs)))

    print(f"""\n>> E33/E0 = {e33}\n
    d31 = {d31}\n
    V1 = {v1}\n
    Kсв = {ksv}""")


def brus(l, s, b, b1, p, c, df, Fp, Fa, Gp, Gs):
    """Расчет параметров пьезоэлемента формы бруса трапецеидального"""

    global e33, d31, v1, ksv

    e33 = 56.5 * 10**9 * ((c * (b + b1)) / (s * l))
    d31 = 2.34 * 10**(-6) * sqrt(e33 * (df / p * Fp**3 * l**2))
    v1 = 2 * l * Fp
    ksv = sqrt((1 - (Fp / Fa)**2) * ((Gp - Gs)/(Gp + Gs)))

    print(f"""\n>> E33/E0 = {e33}\n
    d31 = {d31}\n
    V1 = {v1}\n
    Kсв = {ksv}""")


def sterzh(l, w, p, c, df, Fp, Fa, Gp, Gs):
    """Расчет параметров пьезоэлемента формы стержня"""
    global e33, d33, v3, ksv

    e33 = 113 * 10**9 * ((c * l) / w)
    d33 = 2.34 * 10**(-6) * sqrt(e33 * (df / (p * Fp**3 * l**2)))
    v3 = 2 * l * Fa
    ksv = sqrt((1 - (Fp / Fa)**2) * ((Gp - Gs)/(Gp + Gs)))

    print(f"""\n>> E33/E0 = {e33}\n
    d33 = {d33}\n
    V3 = {v3}\n
    Kсв = {ksv}""")


def shaiba(l, D, d, p, c, df, Fp, Fa, Gp, Gs):
    """Расчет параметров пьезоэлемента формы шайбы"""

    global e33, d31, v1, ksv

    if (4 * l) / (pi * (D + d)) <= 0.5:

        key = round((round((d/D) / 0.05) * 0.05), 2)

        dict_t = {0.05:1.115,0.10:1.137,0.15:1.145,0.20:1.132,0.25:1.115,0.30:1.100,
                  0.35:1.080,0.40:1.065,0.45:1.051,0.50:1.040,0.55:1.030,0.60:1.021,
                  0.65:1.015,0.70:1.010,0.75:1.008,0.80:1.005,0.85:1.003,0.90:1.001,0.95:1.000}

        dict_ro = {0.05:0.770,0.10:0.810,0.15:0.840,0.20:0.885,0.25:0.905,0.30:0.925,
                   0.35:0.940,0.40:0.950,0.45:0.965,0.50:0.970,0.55:0.980,0.60:0.985,0.65:0.990,0.70:1.000}

        t = dict_t[key]
        ro = dict_ro[key]

    else:
        print(""">> Условие пункта 4 из приложения 3 СЭО.712.004 ТУ не выполняется,
           ниже предлагается ввести поправки t и ro.
           Иначе формулы вычисления скорости звука и пьезомодуля не применимы""")
        t = eval(input(">> t = "))
        ro = eval(input(">> ro = "))

    e33 = 143.9 * 10**9 * ((c * l) / (D**2 - d**2))
    d31 = 2.68 * 10**(-6) * ro * sqrt(e33 * (df / (p * Fp**3 * (D + d)**2)))
    v1 = (1.57 / t) * (D + d) * Fp
    ksv = sqrt((1 - (Fp / Fa)**2) * ((Gp - Gs)/(Gp + Gs)))

    print(f"""\n>> E33/E0 = {e33}\n
    d31 = {d31}\n
    V1 = {v1}\n
    Kсв = {ksv}""")


def disk(l, D, p, c, df, Fp, Fa, Gp, Gs):
    """Расчет параметров пьезоэлемента формы диска"""

    global e33, d31, v1, ksv

    e33 = 143.9 * 10**9 * ((c * l) / D**2)
    d31 = 1.91 * 10**(-6) * sqrt(e33 * (df / (p * Fp**3 * D**2)))
    v1 = 1.46 * D * Fp
    ksv = sqrt((1 - (Fp / Fa)**2) * ((Gp - Gs)/(Gp + Gs)))

    print(f"""\n>> E33/E0 = {e33}\n
    d31 = {d31}\n
    V1 = {v1}\n
    Kсв = {ksv}""")


def trubka(l, D, d, p, c, df, Fp, Fa, Gp, Gs):
    """Расчет параметров пьезоэлемента формы трубки"""

    global e33, d31, v1, ksv

    if (4 * l) / (pi * (D + d)) <= 0.5:

        key = round((round((d/D) / 0.05) * 0.05), 2)

        dict_t = {0.05:1.115,0.10:1.137,0.15:1.145,0.20:1.132,0.25:1.115,0.30:1.100,
                  0.35:1.080,0.40:1.065,0.45:1.051,0.50:1.040,0.55:1.030,0.60:1.021,
                  0.65:1.015,0.70:1.010,0.75:1.008,0.80:1.005,0.85:1.003,0.90:1.001,0.95:1.000}

        t = dict_t[key]

    else:
        print(""">> Условие пункта 4 из приложения 3 СЭО.712.004 ТУ не выполняется,
           ниже предлагается ввести поправку t.
           Иначе формулы вычисления скорости звука и пьезомодуля не применимы""")
        t = eval(input(">> t = "))

    e33 = 17.98 * 10**9 * c * (1 / l) * log(D / d)
    d31 = 2.68 * 10**(-6) * sqrt(e33 * (df / (p * (D + d)**2 * Fp**3)))
    v1 = 1.57 * (1 / t) * (D + d) * Fp
    ksv = sqrt((1 - (Fp / Fa)**2) * ((Gp - Gs)/(Gp + Gs)))

    print(f"""\n>> E33/E0 = {e33}\n
    d31 = {d31}\n
    V1 = {v1}\n
    Kсв = {ksv}""")


def output_antenna(output_file):
    """Вывод расчитанных параметров для антенны в файл .csv"""

    with open(output_file, 'w+') as output:

        if len(list(output.read())) == 0:

            output.write("№, Fp; кГц, Fa; кГц, Rp; Ом, Rs; Ом, Cэл; нФ, tg; %, Z; кОм\n")
            #output.write(f", {Fp}, {Fa}, {Rp}, {Rs}, {c}, {tg}, {z}\n")
            output.write(", %.3f, %.3f, %.2f, %.2f, %.3f, %.2f, %.2f\n" % (Fp/1000, Fa/1000, Rp, Rs, c*10**(9), tg, z/1000))

        else:

            #output.write(f" , {Fp}, {Fa}, {Rp}, {Rs}, {c}, {tg}, {z}\n")
            output.write(", %.3f, %.3f, %.2f, %.2f, %.3f, %.2f, %.2f\n" % (Fp/1000, Fa/1000, Rp, Rs, c*10**(9), tg, z/1000))

    output.close()


def output_sterzh(output_file):
    """Вывод расчитанных параметров для керамики стержня в файл .csv"""

    with open(output_file, 'r+') as output:

        if len(list(output.read())) == 0:

            output.write("№, Fp; кГц, Fa; кГц, Gp; мСм, Gs; мкСм, Cэл; нФ, tg; %, Z; кОм, Eps, C3; м/с, D33 * 10^(-10), Kсв\n")
            #output.write(f", {Fp}, {Fa}, {Gp}, {Gs}, {c}, {tg}, {z}, {e33}, {v3}, {d33}, {ksv}\n")
            output.write(", %.3f, %.3f, %.2f, %.2f, %.3f, %.2f, %.2f, %.1f, %.1f, %.2f, %.3f\n" % (Fp/1000, Fa/1000, Gp*10**3, Gs*10**6, c*10**(9), tg, z/1000, e33, v3, d33*10**10, ksv))

        else:

            #output.write(f", {Fp}, {Fa}, {Gp}, {Gs}, {c}, {tg}, {z}, {e33}, {v3}, {d33}, {ksv}\n")
            output.write(", %.3f, %.3f, %.2f, %.2f, %.3f, %.2f, %.2f, %.1f, %.1f, %.2f, %.3f\n" % (Fp/1000, Fa/1000, Gp*10**3, Gs*10**6, c*10**(9), tg, z/1000, e33, v3, d33*10**10, ksv))

    output.close()


def output_ceramic(output_file):
    """Вывод расчитанных параметров для керамики кроме стержня в файл .csv"""

    with open(output_file, 'r+') as output:

        if len(list(output.read())) == 0:

            output.write("№, Fp; кГц, Fa; кГц, Gp; мСм, Gs; мкСм, Cэл; нФ, tg; %, Z; кОм, Eps, C1; м/с, D31 * 10^(-10), Kсв\n")
            #output.write(f" , {Fp}, {Fa}, {Gp}, {Gs}, {c}, {tg}, {z}, {e33}, {v1}, {d31}, {ksv}\n")
            output.write(", %.3f, %.3f, %.2f, %.2f, %.3f, %.2f, %.2f, %.1f, %.1f, %.2f, %.3f \n" % (Fp/1000, Fa/1000, Gp*10**3, Gs*10**6, c*10**(9), tg, z/1000, e33, v1, d31*10**10, ksv))

        else:

            output.write(", %.3f, %.3f, %.2f, %.2f, %.3f, %.2f, %.2f, %.1f, %.1f, %.2f, %.3f\n" % (Fp/1000, Fa/1000, Gp*10**3, Gs*10**6, c*10**(9), tg, z/1000, e33, v1, d31*10**10, ksv))

    output.close()


def main():

    set_default()

    check_key = 2

    check_plot = eval(input("\n>> Построить график после измерений?(1/0)\n"))

    if Element == 'ceramic':

        if Type == 'plast':
            calc_C()
            calc_all()
            plast(l, s, b, p, c, df, Fp, Fa, Gp, Gs)
            output_ceramic(output_file)
            if check_plot == 1:
                make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)
                if check_key == 1:
                    plast(l, s, b, p, c, df, Fp, Fa, Gp, Gs)


        elif Type == 'brus':
            calc_C()
            calc_all()
            brus(l, s, b, b1, p, c, df, Fp, Fa, Gp, Gs)
            output_ceramic(output_file)
            if check_plot == 1:
                make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)
                if check_key == 1:
                    brus(l, s, b, b1, p, c, df, Fp, Fa, Gp, Gs)


        elif Type == 'sterzh':
            calc_C()
            calc_all()
            sterzh(l, w, p, c, df, Fp, Fa, Gp, Gs)
            output_sterzh(output_file)
            if check_plot == 1:
                make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)
                if check_key == 1:
                    sterzh(l, w, p, c, df, Fp, Fa, Gp, Gs)


        elif Type == 'shaiba':
            ser.timeout = 1.2
            calc_C()
            calc_all()
            shaiba(l, D, d, p, c, df, Fp, Fa, Gp, Gs)
            output_ceramic(output_file)
            if check_plot == 1:
                make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)
                if check_key == 1:
                    shaiba(l, D, d, p, c, df, Fp, Fa, Gp, Gs)


        elif Type == 'disk':
            calc_C()
            calc_all()
            disk(l, D, p, c, df, Fp, Fa, Gp, Gs)
            output_ceramic(output_file)
            if check_plot == 1:
                make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)
                if check_key == 1:
                    disk(l, D, p, c, df, Fp, Fa, Gp, Gs)


        elif Type == 'trubka':
            calc_C()
            calc_all()
            trubka(l, D, d, p, c, df, Fp, Fa, Gp, Gs)
            output_ceramic(output_file)
            if check_plot == 1:
                make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)
                if check_key == 1:
                    trubka(l, D, d, p, c, df, Fp, Fa, Gp, Gs)


        else:
            print(">> Допущена ошибка при введении формы пьезоэлемента")
            exit()


    elif Element == 'antenna':
        calc_C()
        calc_all()
        output_antenna(output_file)
        if check_plot == 1:
            make_plot(Gp_list, Gs_list, Rp_list, Rs_list, Z_list, Cp_list, Cs_list)

    else:
        print(">> Допущена ошибка при введении типа измеряемого объекта (antenna/ceramic)")
        exit()



main()

while True:
    check_loop = eval(input("\n>> Повторить цикл измерений?(1/0)\n"))
    if check_loop == 1:
        main()
    else:
        
        break
