import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import pandas as pd
import geopandas
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.ticker import ScalarFormatter
from datetime import datetime, timedelta

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

dpi = 300 # dpi for google slides

colors = {'Black': '#000000', 'Dark grey': '#595959', 'Medium grey': '#a2a2a2', 'Light grey': '#cccccc', 'Very light grey': '#eeeeee', 'White': '#ffffff', 'Green': '#83af63', 'Dark red': '#8B0000', 'Orange': '#ef8636', 'Blue': '#3b75af', 'Purple': '#874C82', 'Brown': '#8B4513', 'Tan': '#C68B70', 'Teal': '#4c8670', 'Dark green': '#2F4F4F'}
loctype_to_color_dict = { 'Home' : colors['Blue'], 'Recreation' : colors['Dark green'], 'Work' : colors['Medium grey'], 'School': colors['Teal'], 'Shop': colors['Purple'], 'Hospital': colors['Dark grey'], 'ICU': colors['Medium grey']}
ag_to_color_dict = {'0-4': colors['Blue'], '5-15': colors['Dark green'], '16-34': colors['Brown'], '35-59': colors['Teal'], '60-79': colors['Purple'], '80+': colors['Green']}
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


class Log1pNorm(mcolors.Normalize):
    def __init__(self, vmin=None, vmax=None):
        super().__init__(vmin=vmin, vmax=vmax)

    def __call__(self, value, clip=None):
        log_val = np.log1p(value)  # log(x+1)
        log_vmin = np.log1p(self.vmin)
        log_vmax = np.log1p(self.vmax)
        return (log_val - log_vmin) / (log_vmax - log_vmin)

    def inverse(self, value):
        log_vmin = np.log1p(self.vmin)
        log_vmax = np.log1p(self.vmax)
        return np.expm1(value * (log_vmax - log_vmin) + log_vmin)
