import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import pandas as pd
import geopandas
import numpy as np

matplotlib.pyplot.style.use('default')
fontsize = 15
matplotlib.rcParams.update({
	'font.size': fontsize,
'axes.titlesize': fontsize * 1.2,
 	'axes.labelsize': fontsize,
 	'xtick.labelsize': fontsize * 0.8,
 	'ytick.labelsize': fontsize * 0.8,
	'legend.fontsize': fontsize * 0.8,
	'font.family': 'Arial'
})

# Settings for Figure a)
width_a_in_in = 4.1 # Figure width in inch
height_a_in_in = 2.6 # Figure height in inch
axes_width_a = 0.1 # Width of the axes and the ticks
length_tick_lines_a = 1 # Length of the tick lines
dpi = 96 # dpi for google slides


colors = {'Black': '#000000', 'Dark grey': '#595959', 'Medium grey': '#a2a2a2', 'Light grey': '#cccccc', 'Very light grey': '#eeeeee', 'White': '#ffffff', 'Dark red': '#980000', 'Red': '#d41e1e', 'Orange': '#ef8636', 'Muted orange': '#efa94b', 'Yellow': '#ffe575', 'Brown': '#996633', 'Dark green': '#83af63', 'Light green': '#bfd767', 'Cadet blue': '#74a1a3', 'Dark blue': '#1c4587', 'Blue': '#3b75af', 'Light blue': '#cfe2f3'}
loctype_to_color_dict = { 'Home' : colors['Brown'], 'Recreation' : colors['Light green'], 'Work' : colors['Blue'], 'School': colors['Orange'], 'Shop': colors['Dark red'], 'Hospital': colors['Dark grey'], 'ICU': colors['Medium grey']}
ag_to_color_dict = {'0-4': colors['Brown'], '5-15': colors['Light green'], '16-34': colors['Blue'], '35-59': colors['Orange'], '60-79': colors['Dark red'], '80+': colors['Dark grey']}
idx_to_loctype_dict = { 0: 'Home', 1: 'School', 3: 'Recreation', 2: 'Work', 4: 'Shop', 5: 'Hospital', 6: 'ICU', 10: "Cemetery"}
age_groups = ['0-4', '5-15', '16-34', '35-59', '60-79', '80+']
idx_to_age_group = {0: '0-4', 1: '5-15', 2: '16-34', 3: '35-59', 4: '60-79', 5: '80+'}
cmap = 'viridis_r'

def get_time_point(weekday, time):
    return weekday * 24 + time

def age_to_age_group(age):
    if (age <= 4):
        return '0-4'
    elif (age <= 15):
        return '5-15'
    elif (age <= 34):
        return '16-34'
    elif (age <= 59):
        return '35-59'
    elif (age <= 79):
        return '60-79'
    elif (age > 79):
        return '80+'
    else:
        print(f'Error: Age {age} cannot be mapped to age group')
        return ('NaN')
    
def lighten_color(color, amount):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])

ww_data_shp_file = 'Verschnitt_DLR_TAN_Rep.shp'
person_file = 'persons_final_corr.csv'
