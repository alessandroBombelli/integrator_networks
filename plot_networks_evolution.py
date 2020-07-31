# -*- coding: utf-8 -*-
"""
Created on Sat Jul 11 07:39:58 2020

@author: abombelli
"""

import numpy as np
import requests
from bs4 import BeautifulSoup
import lxml.html as lh
from lxml import etree
import pandas as pd
import os
import openpyxl
import re
import time
import igraph as ig
import random
from collections import Counter
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from matplotlib.lines import Line2D

plt.close('all')

cwd = os.getcwd()

#wb          = openpyxl.load_workbook(os.path.join(cwd,'FedEx_evolution_network.xlsx'))
#sheet       = wb['Sheet_name_1']
#eta         = sheet.max_row

df_FedEx    = pd.read_excel(os.path.join(cwd,'FedEx_evolution_network.xlsx'),header=None)
df_UPS      = pd.read_excel(os.path.join(cwd,'UPS_evolution_network.xlsx'),header=None)
df_DHL      = pd.read_excel(os.path.join(cwd,'DHL_evolution_network.xlsx'),header=None)
df_Cathay   = pd.read_excel(os.path.join(cwd,'Cathay_evolution_network.xlsx'),header=None)
df_Cargolux = pd.read_excel(os.path.join(cwd,'Cargolux_evolution_network.xlsx'),header=None)
df_AFKLMP   = pd.read_excel(os.path.join(cwd,'AFKLMP_evolution_network.xlsx'),header=None)

obs = [['November_19','November_20','November_21'],
       ['December_03','December_04','December_05'],
       ['December_16','December_17','December_18'],
       ['December_30','December_31','January_01'],
       ['January_13','January_14','January_15'],
       ['January_27','January_28','January_29'],
       ['February_14','February_15','February_16'],
       ['March_02','March_03','March_04'],
       ['April_06','April_07','April_08'],
       ['April_27','April_28','April_29'],
       ['May_11','May_12','May_13'],
       ['May_26','May_27','May_28'],
       ['June_18','June_19','June_20']]

date_set_string = ['19-11-2019','03-12-2019','16-12-2019','30-12-2019',
                   '13-01-2020','27-01-2020','14-02-2020','02-03-2020',
                   '06-04-2020','27-04-2020','11-05-2020','26-05-2020',
                   '18-06-2020']

date_set_datetime = []
for date in date_set_string:
    date_set_datetime.append(datetime.datetime.strptime(date, '%d-%m-%Y'))
    
################################################
### Defining important dates related to COVID-19
################################################
dates    = ['31-December-2019','11-January-2020','31-January-2020',
            '11-March-2020','11-May-2020']
date_str = []
for i in range(0,int(len(dates))):
    date_str.append([dates[i],i+1])

date_str = np.array(date_str)    
date_str[:,0].astype(str)
date_str[:,1].astype(int)
df_dates = pd.DataFrame(date_str,columns=['Date','Date_idx'])
df_dates['Date'] =pd.to_datetime(df_dates.Date)
df_dates['Date_idx'] = pd.to_numeric(df_dates['Date_idx'])
df_dates_sorted = df_dates.sort_values(by='Date')
df_dates_sorted = df_dates.reset_index(drop=True)    

# Just for plotting purposes    
offset           = [1,1,1,-6,3]
font_number_date = 16
this_markersize  = 6 
    
cmap = plt.cm.get_cmap('PuOr')
# All Markers (for plotting purposes) 
all_markers = list(Line2D.markers.keys())

# Determine max. value for plotting purposes
max_AFT_FedEx    = np.max(df_FedEx.loc[137][1:].astype(float))
max_AFT_UPS      = np.max(df_UPS.loc[124][1:].astype(float))
max_AFT_DHL      = np.max(df_DHL.loc[213][1:].astype(float))
max_AFT_Cathay   = np.max(df_Cathay.loc[99][1:].astype(float))
max_AFT_Cargolux = np.max(df_Cargolux.loc[112][1:].astype(float))
max_AFT_KLM      = np.max(df_AFKLMP.loc[281][1:].astype(float))
max_AFT_MP       = np.max(df_AFKLMP.loc[292][1:].astype(float)-
                          df_AFKLMP.loc[281][1:].astype(float))
max_AFT_AFKLMP   = np.max(df_AFKLMP.loc[292][1:].astype(float))
max_value        = np.max([max_AFT_FedEx,max_AFT_UPS,
                           max_AFT_DHL,max_AFT_Cathay,
                           max_AFT_Cargolux,max_AFT_AFKLMP])

fig, ax = plt.subplots()
ax.plot(date_set_datetime,df_FedEx.loc[137][1:].astype(float),
                  marker=all_markers[0],markersize=4,linestyle='-',linewidth=1.5,
                  label='FedEx',color=cmap(max_AFT_FedEx/max_value))
ax.plot(date_set_datetime,df_UPS.loc[124][1:].astype(float),
                  marker=all_markers[1],markersize=4,linestyle='-',linewidth=1.5,
                  label='UPS',color=cmap(max_AFT_UPS/max_value))
ax.plot(date_set_datetime,df_DHL.loc[213][1:].astype(float),
                  marker=all_markers[2],markersize=4,linestyle='-',linewidth=1.5,
                  label='DHL',color=cmap(max_AFT_DHL/max_value))
ax.plot(date_set_datetime,df_Cathay.loc[99][1:].astype(float),
                  marker=all_markers[3],markersize=4,linestyle='-',linewidth=1.5,
                  label='Cathay',color=cmap(max_AFT_Cathay/max_value))
ax.plot(date_set_datetime,df_Cargolux.loc[112][1:].astype(float),
                  marker=all_markers[4],markersize=4,linestyle='-',linewidth=1.5,
                  label='Cargolux',color=cmap(max_AFT_Cargolux/max_value))
ax.plot(date_set_datetime,df_AFKLMP.loc[281][1:].astype(float),
                  marker=all_markers[5],markersize=4,linestyle='-',linewidth=1.5,
                  label='KLM',color=cmap(max_AFT_KLM/max_value))
ax.plot(date_set_datetime,df_AFKLMP.loc[292][1:].astype(float)-df_AFKLMP.loc[281][1:].astype(float),
                  marker=all_markers[6],markersize=4,linestyle='-',linewidth=1.5,
                  label='MP',color=cmap(max_AFT_MP/max_value))
ax.plot(date_set_datetime,df_AFKLMP.loc[292][1:].astype(float),
                  marker=all_markers[7],markersize=4,linestyle='-',linewidth=1.5,
                  label='KLMP',color=cmap(max_AFT_AFKLMP/max_value))  
# upper_bound = 450000
# for i in range(0,int(len(df_dates_sorted))):
#     plt.plot([df_dates_sorted['Date'][i],df_dates_sorted['Date'][i]],
#              [0,upper_bound],linestyle='-',linewidth=1.5,color='k')
#     plt.text(df_dates_sorted['Date'][i]+datetime.timedelta(days=offset[i]),upper_bound,
#              df_dates_sorted['Date_idx'][i],fontsize=font_number_date)        
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
ax.grid(True)
ax.tick_params(axis='x', which='major', labelsize=8)
axis_font   = {'fontname':'Arial', 'size':'14'}
axis_font_2 = {'fontname':'Arial', 'size':'8'}
ax.set_xlabel('Date',**axis_font)
ax.set_ylabel('AFT [tonnes]',**axis_font)



fig.autofmt_xdate()
#ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05),
#          ncol=1, fancybox=True, shadow=True)
ax.legend(loc=[0.3,0.75],frameon=False, labelspacing=.5,
          ncol=3, fancybox=True, shadow=True)
#plt.legend(loc='upper right',prop={'size': 10})

# These are in unitless percentages of the figure size. (0,0 is bottom left)
left, bottom, width, height = [0.57, 0.43, 0.3, 0.18]
ax1 = fig.add_axes([left, bottom, width, height])
ax1.plot(date_set_datetime,df_AFKLMP.loc[281][1:].astype(float),
                  marker=all_markers[5],markersize=4,linestyle='-',linewidth=1.5,
                  label='KLM',color=cmap(max_AFT_KLM/max_value))
ax1.plot(date_set_datetime,df_AFKLMP.loc[292][1:].astype(float)-df_AFKLMP.loc[281][1:].astype(float),
                  marker=all_markers[6],markersize=4,linestyle='-',linewidth=1.5,
                  label='MP',color=cmap(max_AFT_MP/max_value))
ax1.plot(date_set_datetime,df_AFKLMP.loc[292][1:].astype(float),
                  marker=all_markers[7],markersize=4,linestyle='-',linewidth=1.5,
                  label='KLMP',color=cmap(max_AFT_AFKLMP/max_value)) 
#ax1.grid(True)
ax1.tick_params(axis='x', which='major', labelsize=6, rotation=20)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=60))
ax1.set_ylabel('AFT [tonnes]',**axis_font_2)


plt.show()
plt.savefig(os.path.join(cwd,'Figures','networks_evolution_AFT.png'),dpi=600,bbox_inches='tight', 
              transparent=True,
              pad_inches=0.1)

markersize_this_plot = 6

fig, ax = plt.subplots()
plt.plot(date_set_datetime,df_FedEx.loc[134][1:].astype(float)/113.0*100,
                  marker=all_markers[0],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='FedEx',color=cmap(max_AFT_FedEx/max_value))
plt.plot(date_set_datetime,df_UPS.loc[121][1:].astype(float)/105.0*100,
                  marker=all_markers[1],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='UPS',color=cmap(max_AFT_UPS/max_value))
plt.plot(date_set_datetime,df_DHL.loc[210][1:].astype(float)/188.0*100,
                  marker=all_markers[2],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='DHL',color=cmap(max_AFT_DHL/max_value))
plt.plot(date_set_datetime,df_Cathay.loc[96][1:].astype(float)/55.0*100,
                  marker=all_markers[3],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cathay',color=cmap(max_AFT_Cathay/max_value))
plt.plot(date_set_datetime,df_Cargolux.loc[109][1:].astype(float)/90.0*100,
                  marker=all_markers[4],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cargolux',color=cmap(max_AFT_Cargolux/max_value))
# plt.plot(date_set_datetime,df_AFKLMP.loc[278][1:].astype(float),
#                   marker=all_markers[5],markersize=4,linestyle='-',linewidth=1.5,
#                   label='KLM',color=cmap(max_AFT_KLM/max_value))
# plt.plot(date_set_datetime,df_AFKLMP.loc[289][1:].astype(float)-df_AFKLMP.loc[278][1:].astype(float),
#                   marker=all_markers[6],markersize=4,linestyle='-',linewidth=1.5,
#                   label='MP',color=cmap(max_AFT_MP/max_value))
plt.plot(date_set_datetime,df_AFKLMP.loc[289][1:].astype(float)/126.0*100,
                  marker=all_markers[7],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='KLMP',color=cmap(max_AFT_AFKLMP/max_value))          
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
ax.grid(True)
ax.tick_params(axis='x', which='major', labelsize=8)
axis_font  = {'fontname':'Arial', 'size':'14'}
ax.set_xlabel('Date',**axis_font)
ax.set_ylabel(r'$\frac{|\mathcal{G}_c|}{\max(|\mathcal{G}_c)|}$ [%]',**axis_font)
fig.autofmt_xdate()
#ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05),
#          ncol=1, fancybox=True, shadow=True)
ax.legend(loc='best',frameon=False, labelspacing=.5,
          ncol=3, fancybox=True, shadow=True)
#plt.legend(loc='upper right',prop={'size': 10})
plt.show()
plt.savefig(os.path.join(cwd,'Figures','networks_evolution_Gc.png'),dpi=600,bbox_inches='tight', 
              transparent=True,
              pad_inches=0.1)


fig, ax = plt.subplots()
plt.plot(date_set_datetime,df_FedEx.loc[129][1:].astype(float),
                  marker=all_markers[0],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='FedEx',color=cmap(max_AFT_FedEx/max_value))
plt.plot(date_set_datetime,df_UPS.loc[116][1:].astype(float),
                  marker=all_markers[1],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='UPS',color=cmap(max_AFT_UPS/max_value))
plt.plot(date_set_datetime,df_DHL.loc[205][1:].astype(float),
                  marker=all_markers[2],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='DHL',color=cmap(max_AFT_DHL/max_value))
plt.plot(date_set_datetime,df_Cathay.loc[91][1:].astype(float),
                  marker=all_markers[3],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cathay',color=cmap(max_AFT_Cathay/max_value))
plt.plot(date_set_datetime,df_Cargolux.loc[104][1:].astype(float),
                  marker=all_markers[4],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cargolux',color=cmap(max_AFT_Cargolux/max_value))
plt.plot(date_set_datetime,df_AFKLMP.loc[284][1:].astype(float)/126.0*100,
                  marker=all_markers[7],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='KLMP',color=cmap(max_AFT_AFKLMP/max_value))          
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
ax.grid(True)
ax.tick_params(axis='x', which='major', labelsize=8)
axis_font  = {'fontname':'Arial', 'size':'14'}
ax.set_xlabel('Date',**axis_font)
ax.set_ylabel(r'|$\mathcal{E}$|',**axis_font)
fig.autofmt_xdate()
#ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05),
#          ncol=1, fancybox=True, shadow=True)
ax.legend(loc='best',frameon=False, labelspacing=.5,
          ncol=3, fancybox=True, shadow=True)
#plt.legend(loc='upper right',prop={'size': 10})
plt.show()
plt.savefig(os.path.join(cwd,'Figures','networks_evolution_edges.png'),dpi=600,bbox_inches='tight', 
              transparent=True,
              pad_inches=0.1)

fig, ax = plt.subplots()
plt.plot(date_set_datetime,df_FedEx.loc[130][1:].astype(float),
                  marker=all_markers[0],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='FedEx',color=cmap(max_AFT_FedEx/max_value))
plt.plot(date_set_datetime,df_UPS.loc[117][1:].astype(float),
                  marker=all_markers[1],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='UPS',color=cmap(max_AFT_UPS/max_value))
plt.plot(date_set_datetime,df_DHL.loc[206][1:].astype(float),
                  marker=all_markers[2],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='DHL',color=cmap(max_AFT_DHL/max_value))
plt.plot(date_set_datetime,df_Cathay.loc[92][1:].astype(float),
                  marker=all_markers[3],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cathay',color=cmap(max_AFT_Cathay/max_value))
plt.plot(date_set_datetime,df_Cargolux.loc[105][1:].astype(float),
                  marker=all_markers[4],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cargolux',color=cmap(max_AFT_Cargolux/max_value))
plt.plot(date_set_datetime,df_AFKLMP.loc[285][1:].astype(float)/126.0*100,
                  marker=all_markers[7],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='KLMP',color=cmap(max_AFT_AFKLMP/max_value))          
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
ax.grid(True)
ax.tick_params(axis='x', which='major', labelsize=8)
axis_font  = {'fontname':'Arial', 'size':'14'}
ax.set_xlabel('Date',**axis_font)
ax.set_ylabel(r'$\langle k \rangle$',**axis_font)
fig.autofmt_xdate()
#ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05),
#          ncol=1, fancybox=True, shadow=True)
ax.legend(loc='best',frameon=False, labelspacing=.5,
          ncol=3, fancybox=True, shadow=True)
#plt.legend(loc='upper right',prop={'size': 10})
plt.show()
plt.savefig(os.path.join(cwd,'Figures','networks_evolution_k.png'),dpi=600,bbox_inches='tight', 
              transparent=True,
              pad_inches=0.1)

fig, ax = plt.subplots()
plt.plot(date_set_datetime,df_FedEx.loc[135][1:].astype(float),
                  marker=all_markers[0],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='FedEx',color=cmap(max_AFT_FedEx/max_value))
plt.plot(date_set_datetime,df_UPS.loc[122][1:].astype(float),
                  marker=all_markers[1],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='UPS',color=cmap(max_AFT_UPS/max_value))
plt.plot(date_set_datetime,df_DHL.loc[211][1:].astype(float),
                  marker=all_markers[2],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='DHL',color=cmap(max_AFT_DHL/max_value))
plt.plot(date_set_datetime,df_Cathay.loc[97][1:].astype(float),
                  marker=all_markers[3],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cathay',color=cmap(max_AFT_Cathay/max_value))
plt.plot(date_set_datetime,df_Cargolux.loc[110][1:].astype(float),
                  marker=all_markers[4],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='Cargolux',color=cmap(max_AFT_Cargolux/max_value))
plt.plot(date_set_datetime,df_AFKLMP.loc[290][1:].astype(float)/126.0*100,
                  marker=all_markers[7],markersize=markersize_this_plot,linestyle='-',linewidth=1.5,
                  label='KLMP',color=cmap(max_AFT_AFKLMP/max_value))          
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%B-%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=15))
ax.grid(True)
ax.tick_params(axis='x', which='major', labelsize=8)
axis_font  = {'fontname':'Arial', 'size':'14'}
ax.set_xlabel('Date',**axis_font)
ax.set_ylabel(r'$\langle L \rangle$',**axis_font)
fig.autofmt_xdate()
#ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05),
#          ncol=1, fancybox=True, shadow=True)
ax.legend(loc=[0.1,0.25],frameon=False, labelspacing=.5,
          ncol=3, fancybox=True, shadow=True)
#plt.legend(loc='upper right',prop={'size': 10})
plt.show()
plt.savefig(os.path.join(cwd,'Figures','networks_evolution_L.png'),dpi=600,bbox_inches='tight', 
              transparent=True,
              pad_inches=0.1)