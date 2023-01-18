from sys import argv

Fstart = argv[1]
Fstop= argv[2]
Step= argv[3]
csv_file = argv[4]

no_report = 'no-report' in argv
z_only = 'z-only' in argv

import serial # Библиотека для конекта с COM портом
import struct
import requests # Библиотека для ethernet взаимодействия
from math import *
#import matplotlib.pyplot as plt
#from matplotlib.ticker import AutoMinorLocator

import numpy as np

if not no_report:
  import plotly.graph_objects as go
  from reportlab.pdfbase import pdfmetrics as pdfm
  from reportlab.pdfbase.ttfonts import TTFont

  pdfm.registerFont(TTFont('Ubuntu-BI', '/usr/share/fonts/truetype/ubuntu/Ubuntu-BI.ttf'))
  pdfm.registerFont(TTFont('Ubuntu-B', '/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf'))
  pdfm.registerFont(TTFont('Ubuntu-RI', '/usr/share/fonts/truetype/ubuntu/Ubuntu-RI.ttf'))
  pdfm.registerFont(TTFont('Ubuntu-R', '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf'))
  pdfm.registerFontFamily('Ubuntu',normal='Ubuntu-R',bold='Ubuntu-B',italic='Ubuntu-RI',boldItalic='Ubuntu-BI')

  from reportlab.lib import pagesizes, units, styles, enums, colors
  from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, ImageAndFlowables, Frame, PageTemplate

from datetime import datetime

from io import BytesIO

# from svglib.svglib import svg2rlg


Fstart = eval(Fstart)
Fstop = eval(Fstop)
#Points = eval(Points)
Step = eval(Step)

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
parameters = (0xAA, 72) # Выдача полной измеряемой информации
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
#  print("\n>> Cэл = ",c, " Ф")
#  print("   tg = %.2f %%\n   Z = %.2f Ом\n" % (tg, z))


def change_scheme():
  """Изменение схемы замещения"""

  ser.write(scheme)
  check_scheme = ser.read(2)

  if struct.unpack('>2B', check_scheme) == scheme:
    ser.read(2)


def set_freq(F):
  """Установка частоты"""

  f = int(F).to_bytes(4,'big')
  freq = (0xAA, 67, f[0], f[1], f[2], f[3])
  ser.write(freq)
  ser.read(4)


def calc_all():
  """Измерение всех величин"""

  global Gp,Rp,Fp,Fa,Gp_list,Rp_list,Cp_list,Cs_list,Z_list,Phi_list

  Gp_list = np.array([])

  Rp_list = []

  Cp_list = []
  Cs_list = []
  Z_list = []
  Phi_list = []

  if not z_only:
    change_scheme()

    for i in range(Fstart, Fstop + Step, Step):

      print(f"Параллельная, F={i/1000.}кГц", end='\r', flush=True)

      set_freq(i)

      ser.write(parameters)
      data = struct.unpack('>3B3bhiff', ser.read(20))

      f, z, fi = data[7], data[8], data[9]

      Gp_list = np.append(Gp_list, cos(fi) / abs(z))
      Rp_list.append(abs(z) / cos(fi))
#      Cp_list.append(sin(fi) / (2 * pi * f))
      Cp_list.append(1 / (2. * pi * f * abs(z) * sin(-fi)))


    change_scheme()
    print('')

  for i in range(Fstart, Fstop + Step, Step):

    print(f"Последовательная, F={i/1000.}кГц", end='\r', flush=True)

    set_freq(i)

    ser.write(parameters)
    data = struct.unpack('>3B3bhiff', ser.read(20))

    f, z, fi = data[7], data[8], data[9]

    Z_list.append(z)
    Phi_list.append(fi)


#  Gp = max(Gp_list)
#  Rp = min(Rp_list)
#  Cp = max(Cp_list)

#  Fp_index = np.argmax(Gp_list)
#  axis_Fp = list(range(Fstart, Fstop + Step, Step))
#  Fp = axis_Fp[Fp_index]

#  Fa_index = Cp_list.index(Cp)
#  axis_Fa = list(range(Fstart, Fstop + Step, Step))
#  Fa = axis_Fa[Fa_index]


def selectRangeByLevel( xdata, ydata, max_idx, level ):
  start, stop = -1,-1

#  print('Start level {level}')
  for i in range( max_idx, 0, -1 ):
#    print(f'i {i} x {xdata[i]} y {ydata[i]}')
    if ydata[i-1] <= level:
      start = xdata[i-1] + (level - ydata[i-1]) * (xdata[i] - xdata[i-1]) / (ydata[i] - ydata[i-1])
#      print( f'{xdata[i-1]} + ({level} - {ydata[i-1]}) * ({xdata[i]} - {xdata[i-1]}) / ({ydata[i]} - {ydata[i-1]})')
      break

#  print('Stop level {level}')
  for i in range( max_idx + 1, len(ydata) ):
#    print(f'i {i} x {xdata[i]} y {ydata[i]}')
    if ydata[i] <= level:
      stop = xdata[i-1] + (level - ydata[i-1]) * (xdata[i] - xdata[i-1]) / (ydata[i] - ydata[i-1])
#      print( f'{xdata[i-1]} + ({level} - {ydata[i-1]}) * ({xdata[i]} - {xdata[i-1]}) / ({ydata[i]} - {ydata[i-1]})')
      break

  return start, stop

#print('Test down')
#for i in range( 3, 0, -1 ):
#  print(i)

#print('Test up')
#for i in range( 3+1, 7 ):
#  print(i)

def _header_footer(canvas, doc):
  # Save the state of our canvas so we can draw on it
  canvas.saveState()
  ss = styles.getSampleStyleSheet()
#  ss['Normal'].borderWidth = 1
#  ss['Normal'].borderColor = colors.black


  # Header
#  header = Paragraph('Верхний колонтитул ' * 5, ss['Normal'])
  header = Table(
    [[
      Paragraph(datetime.now().isoformat(timespec='seconds', sep=' '), ss['Normal']),
      Paragraph("блок БПИП АДЛН.365351.004 все каналы (нержавейка)", ss["Normal"])
    ]], style = [
      ('VALIGN', (0,0), (-1,-1), 'TOP'),
      ('ALIGN', (0,0), (0,0), 'LEFT'),
      ('ALIGN', (1,0), (1,0), 'RIGHT') ] )

  w, h = header.wrap(doc.width, doc.topMargin)
  header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

  # Footer
#  footer = Paragraph('Нижний колонтитул ' * 5, ss['Normal'])
#  w, h = footer.wrap(doc.width, doc.bottomMargin)
#  footer.drawOn(canvas, doc.leftMargin, h)

  # Release the canvas
  canvas.restoreState()


def emptyPlotTemplate():
  return go.Figure(
    data = [
      { 'name' : 'mainline', 'type': 'scatter', 'x': [], 'y': [],  'mode': 'lines', 'showlegend': False },
      { 'name' : 'bandwidth', 'type': 'scatter', 'x': [], 'y': [], 'text': [], 'mode': 'text', 'textposition': 'top center', 'textfont_size': 16, 'showlegend': False,
        'error_x': {'type': 'data', 'symmetric': False, 'array': [], 'arrayminus': [], 'width': 10, 'color': 'darkgray' }
      }
    ],

    layout = {
      'title': { 'font': { 'size': 32 } }, 'font': {'size': 24}, 'margin': {'l': 150, 'r': 50, 'b': 150, 't': 100, 'pad': 4 },

      'xaxis': {'zeroline': False, 'gridcolor': 'lightgrey'},
      'yaxis': {'zeroline': False, 'gridcolor': 'lightgrey'},

      'autosize': False, 'width': 160, 'height': 120, 'plot_bgcolor': 'white' }
    )

def emptyMarkersTemplate( _name ):
  return go.Scatter(
    name = _name,
    mode = 'markers+text',
    textposition='top right',
    textfont_size=16,
    showlegend=False,
    marker={'size': 10, 'color': 'darkgray'}
  )

def make_report(plot_name, Gp, Rp, Z, Cp):
  """Составление графика"""

  x_range = [ _ for _ in range(Fstart , Fstop + Step, Step) ]

  # Нормируем Gp
#  Gp = Gp / max(Gp)
  maxG = max(Gp)

  max_g_idx = np.argmax(Gp)
  max_g_freq = x_range[ max_g_idx ]

  range_05 = selectRangeByLevel( x_range, Gp, max_g_idx, .5*maxG )
  range_09 = selectRangeByLevel( x_range, Gp, max_g_idx, .9*maxG )
  mean_05 = np.mean(range_05)
  mean_09 = np.mean(range_09)

  Cp_inv = 1./np.array(Cp)
  k = (max(Cp_inv)-min(Cp_inv))
  sft = min(Cp_inv)

  Cp_inv = (Cp_inv - sft)/k
  maxC = max(Cp_inv)

  max_c_idx = np.argmax(Cp_inv)
  max_c_freq = x_range[ max_c_idx ]

  range_09_inv = selectRangeByLevel( x_range, Cp_inv, max_c_idx, .9*maxC )
  mean_09_inv = np.mean(range_09_inv)

  print( 'Cp: ', Cp_inv )
  print( f'maxC {maxC} {max_c_idx} {max_c_freq}' )
  print( 'Norm: ' )
  print(range_09_inv)

  '''
  fig = go.Figure()

  # Main graphics
  fig.add_trace( go.Scatter(
    x = x_range,
    y = Gp,
    mode = 'lines',
    name = 'Gp', showlegend=False))

  # 0.5 and 0.9 bandwidth indicators
  fig.add_trace( go.Scatter(
    x = [mean_05, mean_09],
    y = [0.5, 0.9],
    text = [ f'{range_05[1]-range_05[0]:.1f} Гц', f'{range_09[1]-range_09[0]:.1f} Гц' ],
    mode = 'text',
    error_x = {'type': 'data', 'symmetric': False, 'array': [range_05[1] - mean_05, range_09[1] - mean_09], 'arrayminus': [mean_05 - range_05[0], mean_09 - range_09[0]], 'width': 10, 'color': 'darkgray' },
    textposition='top center',
    textfont_size=16,
    showlegend=False,
  ))

  # Resonance frequency marker
  fig.add_trace( go.Scatter(
    x = [max_g_freq],
    y = [ Gp[max_g_idx] ],
    text = [ f'{max_g_freq:.1f} Гц' ],
    mode = 'markers+text',
    textposition='top right',
    textfont_size=16,
    showlegend=False,
    marker={'size': 10, 'color': 'darkgray'}
  ))

  fig.update_layout(
    title={'text': 'Проводимость Gp, нормированная', 'font': { 'size': 32 } },
    font={'size': 24},
    margin={'l': 150, 'r': 50, 'b': 150, 't': 100, 'pad': 4 },
    xaxis_title='F, кГц',
    yaxis_title='Gnorm',
    autosize=False,
    width=160,
    height=120,
    plot_bgcolor='white'
  )

  fig.update_xaxes(zeroline=False, gridcolor='lightgrey', nticks=7)
  fig.update_yaxes(zeroline=False, gridcolor='lightgrey', tickvals=[1., 0.9, 0.7, 0.5, 0.3])
  '''

  template = PageTemplate(id='normal', frames=[Frame(10*units.cm, 10*units.cm, 5*units.cm, 5*units.cm, id='normal')], onPage=_header_footer)

  pdf = SimpleDocTemplate( plot_name + '.pdf', pagesize = pagesizes.A4,
    topMargin=0.5*units.cm, leftMargin=0.5*units.cm, rightMargin=0.5*units.cm, bottomMargin=0.5*units.cm, showBoundary=0 )

#  doc = BaseDocTemplate('test.pdf', pagesize=letter)
#  pdf.addPageTemplates([template])
  print(pdf.topMargin, pdf.leftMargin, pdf.rightMargin, pdf.bottomMargin, pdf.width, pdf.height)

  frameT = Frame(pdf.leftMargin, pdf.bottomMargin, pdf.width, pdf.height, id='normal',
    topPadding=14, leftPadding=0, rightPadding=0, bottomPadding=14)				# Use ss['Normal'].leading insted of hardcoded 12 pt.
#  pdf.addPageTemplates([PageTemplate(id='First',frames=frameT, onPage=onFirstPage,pagesize=pdf.pagesize),
#          PageTemplate(id='Later',frames=frameT, onPage=onLaterPages,pagesize=pdf.pagesize)])
  pdf.addPageTemplates([PageTemplate(id='First',frames=frameT, pagesize=pdf.pagesize),
          PageTemplate(id='Later',frames=frameT, onPage=_header_footer, pagesize=pdf.pagesize)])


  doc = []

  ss = styles.getSampleStyleSheet()
#  ss['Normal'].borderWidth = 1
#  ss['Normal'].borderColor = colors.black

  ss.add( styles.ParagraphStyle(name='table-hdr-hcenter', parent=ss['h1'], alignment=enums.TA_CENTER))
  ss.add( styles.ParagraphStyle(name='table-hdr-hright', parent=ss['h1'], alignment=enums.TA_CENTER))

  print(ss)

  doc.append(Table(
    [[
      Image('logo-sw.png', 2.5*units.inch, 1.4*units.inch, hAlign='LEFT'),
      Paragraph(datetime.now().isoformat(timespec='seconds', sep=' '), ss['table-hdr-hcenter']),
      Paragraph("блок БПИП АДЛН.365351.004 все каналы (нержавейка)", ss["table-hdr-hright"])
    ]], style = [
      ('VALIGN', (0,0), (-1,-1), 'TOP'),
      ('BOX', (0,0), (-1,-1), 0.25, colors.black),
      ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black) ] ))


  # G plot
  doc.append(Spacer(1, 12))

  fig = emptyPlotTemplate()
  fig.update_traces(selector={'name': 'mainline'}, x = x_range, y = Gp)
  fig.update_traces(selector={'name': 'bandwidth'}, x = [mean_05, mean_09], y = [.5*maxG, .9*maxG], text = [ f'{range_05[1]-range_05[0]:.1f} Гц', f'{range_09[1]-range_09[0]:.1f} Гц' ],
    error_x={'array': [range_05[1] - mean_05, range_09[1] - mean_09], 'arrayminus': [mean_05 - range_05[0], mean_09 - range_09[0]] })

  fig.add_trace( emptyMarkersTemplate('resonanceMarker') )
  fig.update_traces(selector={'name': 'resonanceMarker'}, x = [mean_09], y = [ Gp[max_g_idx] ], text = [ f'{mean_09:.1f} Гц' ])

  fig.update_layout( title_text = 'Gp', xaxis_title='F, Гц', yaxis_title='Gp, См', yaxis_tickformat='.4s'
    , annotations = [ {'xref': 'paper', 'yref': 'y', 'x': 1.035, 'y': maxG*y_i, 'text': f'{y_i}', 'showarrow': False} for y_i in [1., 0.9, 0.7, 0.5, 0.3] ]
  )

  fig.update_xaxes(nticks=7)
  fig.update_yaxes(tickvals=maxG*np.array([1., 0.9, 0.7, 0.5, 0.3]))

#  fig.write_image("fig1.png", width=1600, height=1200)

  doc.append( Image( BytesIO( fig.to_image(format = 'png', width=1600, height=1200)), 180*units.mm, 180*0.75*units.mm, hAlign='CENTER'))

  doc.append(Spacer(1, 12))
  doc.append(Table(
    [
      [Paragraph( 'Диапазон частот:', ss['Normal']), Paragraph( f'{Fstart} - {Fstop} Гц', ss['Normal']) ],
      [Paragraph( 'Резонанс (по уровню 0.9):', ss['Normal']), Paragraph( f'{mean_09:.0f}', ss['Normal']) ],
      [Paragraph( 'Антирезонанс (по уровню 0.9):', ss['Normal']), Paragraph( f'{mean_09_inv:.0f}', ss['Normal']) ],
      [Paragraph( 'Полоса (по уровню 0.5):', ss['Normal']), Paragraph( f'{range_05[0]:.0f} - {range_05[1]:.0f} Гц, ширина {(range_05[1] - range_05[0]):.0f} Гц', ss['Normal']) ],
      [Paragraph( 'Полоса (по уровню 0.9):', ss['Normal']), Paragraph( f'{range_09[0]:.0f} - {range_09[1]:.0f} Гц, ширина {(range_09[1] - range_09[0]):.0f} Гц', ss['Normal']) ],
    ], style = [
      ('VALIGN', (0,0), (-1,-1), 'TOP'),
      ('BOX', (0,0), (-1,-1), 0.25, colors.black),
      ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black) ] ))

  # Rw plot
  doc.append(Spacer(1, 12))

  fig = emptyPlotTemplate()
  fig.update_traces(selector={'name': 'mainline'}, x = x_range, y = Rp)
  fig.update_traces(selector={'name': 'bandwidth'}, x = [mean_05, mean_09], y = [1/(.5*maxG), 1/(.9*maxG)])

  fig.add_trace( emptyMarkersTemplate('resonanceMarker') )
  fig.update_traces(selector={'name': 'resonanceMarker'}, x = [mean_09], y = [ Rp[max_g_idx] ], text = [ f'{mean_09:.1f} Гц' ], textposition='bottom right')

  fig.update_layout( title_text = 'Rw', xaxis_title='F, Гц', yaxis_title='Rw, Ом', yaxis_tickformat='.4s', yaxis_type='log' )

#  fig.update_yaxes(tickvals=1./(maxG*np.array([0.9, 0.5])))
  fig.update_yaxes(nticks=5)


#  fig.write_image("fig2.png", width=1600, height=1200)

  doc.append( Image( BytesIO( fig.to_image(format = 'png', width=1600, height=1200)), 180*units.mm, 180*0.75*units.mm, hAlign='CENTER'))

  # Cp plot
  doc.append(Spacer(1, 12))

  fig = emptyPlotTemplate()
  fig.update_traces(selector={'name': 'mainline'}, x = x_range, y = Cp )
  fig.update_traces(selector={'name': 'bandwidth'}, x = [mean_09_inv], y = [1./((.9*maxC)*k+sft)], text = [ f'{range_09_inv[1]-range_09_inv[0]:.1f} Гц' ],
    error_x={'array': [ range_09_inv[1] - mean_09_inv], 'arrayminus': [ mean_09_inv - range_09_inv[0] ] })

  fig.add_trace( emptyMarkersTemplate('resonanceMarker') )
  fig.update_traces(selector={'name': 'resonanceMarker'}, x = [mean_09_inv], y = [ Cp[max_c_idx] ], text = [ f'{mean_09_inv:.1f} Гц' ], textposition='bottom right')

  fig.update_layout( title_text = 'Cp', xaxis_title='F, кГц', yaxis_title='Cp, Ф', yaxis_tickformat='.4s' )

#  fig.update_yaxes(tickvals=1./(maxG*np.array([0.9, 0.5])))

#  fig.write_image("fig3.png", width=1600, height=1200)

  doc.append( Image( BytesIO( fig.to_image(format = 'png', width=1600, height=1200)), 180*units.mm, 180*0.75*units.mm, hAlign='CENTER'))

  pdf.build( doc )
#  x = list(range(Fstart , Fstop + Step, Step))

#  figure, ((ax0,ax1),(ax2,ax3)) = plt.subplots(nrows=2, ncols=2, figsize=(12,7))

#  ax0.plot(x, Gp, 'b', label='Gp')

#  ax1.plot(x, Rp, 'b', label='Rp')

#  ax2.plot(x, Z, 'b', label='Z')
#  ax3.plot(x, Cp, 'b', label='Cp')

#  ax0.legend()
#  ax1.legend()
#  ax2.legend()
#  ax3.legend()
#  ax0.set_xlabel("F, Гц")
#  ax0.set_ylabel("G")
#  ax1.set_xlabel("F, Гц")
#  ax1.set_ylabel("R, Ом")
#  ax2.set_xlabel("F, Гц")
#  ax2.set_ylabel("Z, Ом")
#  ax3.set_xlabel("F, Гц")
#  ax3.set_ylabel("C, Ф")
#  ax0.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
#  ax0.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
#  ax1.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
#  ax1.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
#  ax2.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
#  ax2.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
#  ax3.grid(True, which="major", axis='both', color="gray", linewidth=1.0)
#  ax3.grid(True, which="minor", axis='both', color="gray", linewidth=0.5)
#  ax0.minorticks_on()
#  ax1.minorticks_on()
#  ax2.minorticks_on()
#  ax3.minorticks_on()
#  plt.tight_layout()

#  figure.suptitle(plot_name)

#  plt.savefig(plot_name+'.png')
#  plt.show()


def output_antenna(output_file):
  """Вывод расчитанных параметров для антенны в файл .csv"""

  num = 0

  with open(output_file, 'w+') as output:
    #output.write("№, Fp; кГц, Fa; кГц, Rp; Ом, Cэл; нФ, tg; %, Z; кОм\n")
    #output.write(f", {Fp}, {Fa}, {Rp}, {c}, {tg}, {z}\n")
    #output.write(", %.3f, %.3f, %.2f, %.3f, %.2f, %.2f\n" % (Fp/1000, Fa/1000, Rp, c*10**(9), tg, z/1000))

    #output.write(f" , {Fp}, {Fa}, {Rp}, {Rs}, {c}, {tg}, {z}\n")
    #output.write("\n")
    output.write("F,Гц;Gp,См;Rp,Ом;Z,Ом;Phi,Гр;Cp,нФ\n")

    for i in range(Fstart, Fstop + Step, Step):
      output.write("%d;%f;%f;%f;%f;%f\n" % (i, 0.0 if z_only else Gp_list[num], 0.0 if z_only else Rp_list[num], Z_list[num], Phi_list[num], 0.0 if z_only else Cp_list[num]*10**9))
      # response = requests.post('http://port2.aquazond.ru:7321/E7-30', data = {
      #   'Gp_list': Gp_list,
      #   'Cp_list': Cp_list,
      #   'Cs_list': Cs_list,
      #   'Z_list': Z_list,
      #   'Phi_list': Phi_list,
      # }, headers= {'Content-type': 'application/json', 'Accept': 'text/plain'})
      num += 1

    # ТУТ БУДЕТ КОД ОТПРАВКИ ДАННЫХ НА САЙТ
    # global Gp,Rp,Fp,Fa,Gp_list,Rp_list,Cp_list,Cs_list,Z_list,Phi_list
    #response = requests.post('http://port2.aquazond.ru:7321/E7-30', data = json.dumps(output.write()))

  output.close()


set_default()

check_key = 2

if csv_file.endswith('csv'):
  plot_name = '.'.join(csv_file.split('.')[:-1])
else:
  plot_name = csv_file

calc_C()
calc_all()

output_antenna(csv_file)

if not no_report:
  make_report(plot_name, Gp_list, Rp_list, Z_list, Cp_list)

#make_report(plot_name, [], [], [], [])
