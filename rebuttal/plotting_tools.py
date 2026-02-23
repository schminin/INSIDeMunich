import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import pandas as pd
import geopandas
import numpy as np
import matplotlib.colors as mcolors
from matplotlib.ticker import ScalarFormatter
from datetime import datetime, timedelta

def set_fontsize(base_fontsize=15):
    fontsize = base_fontsize
    plt.rcParams.update({
        'font.size': fontsize,
        'axes.titlesize': fontsize * 1,
        'axes.labelsize': fontsize,
        'xtick.labelsize': fontsize * 0.8,
        'ytick.labelsize': fontsize * 0.8,
        'legend.fontsize': fontsize * 0.8,
        'font.family': "Arial"
    })

plt.style.use('default')

cm = 2/2.54            # handy conversion factor → inches per centimetre (doubled, to fit google slides settings)

set_fontsize()

green = "#83AF63"
blue = "#3875AF"
orange="#F28C28"
red = "#880000"
teal = "#4C8670"
purple = "#874C82"
brown = "#8B4513"
tan = "#C68B70"
dark_green = "#2F4F4F"
black = "#000000"
dark_grey = "#595959"
medium_grey = "#a2a2a2"
light_grey = "#cccccc"
very_light_grey = "#eeeeee"
white = "#ffffff"


# Mapping of manhole codes to real-world names
manhole_names = {
    "MUC560": "N_Ua", # Wintersteinstr.", # Hasenbergl
    "MUC348": "N_Ub", # "Schmidbartlanger",
    "MUC012": "N_Uc", # "Am Langwieder Bach",
    "MUC112": "C_U", # Botanischer Garten/Menzinger Str.
    
    "MUC060": "S_Ua", # Gräfelfinger Str. / Waldwiesenstr.
    "MUC612": "S_Ub", # Neue Messstelle 1
    "MUC616": "S_M1", # Neue Messstelle 4
    "MUC600": "S_M2", # "Leopoldstr.",
    
    "MUC608": "S_M3", # "Gyßlinger Becken",
    "MUC362": "S_M4", # "Schenkendorfstr.",
    "MUC614": "E_U", # Neue Messstelle 2
    "MUC494": "E_M", # "Savitstr.",

    "MUC562": "N_D", # "WWT Gut Marienhof",
    "MUC434": "SCE_D1", # "Zulauf Gut Großlappen",
    "MUC596": "SCE_D2", # "WWT Gut Großlappen",    
    "MUC586": "Overall",}

manhole_clear_names = {
    "Wintersteinstr.": "N_Ua", # Wintersteinstr.", # Hasenbergl
    "Schmidbartlangerstr.": "N_Ub", # "Schmidbartlanger",
    "Am\nLangwieder\nBach": "N_Uc", # "Am Langwieder Bach",
    "Botanischer\nGarten": "C_U", # Botanischer Garten/Menzinger Str.
    
    "Gräfelfinger\nStr.": "S_Ua", # Gräfelfinger Str. / Waldwiesenstr.
    "Neue\nMessstelle 1": "S_Ub", # Neue Messstelle 1
    "Neue\nMessstelle 4": "S_M1", # Neue Messstelle 4
    "Leopoldstr.": "S_M2", # "Leopoldstr.",
    \
    "Gyßlinger Becken": "S_M3", # "Gyßlinger Becken",
    "Schenkendorfstr.": "S_M4", # "Schenkendorfstr.",
    "Neue\nMessstelle 2": "E_U", # Neue Messstelle 2
    "Savitstr.": "E_M", # "Savitstr.",

    "WWT Gut Marienhof": "N_D", # "WWT Gut Marienhof",
    "Zulauf\nGut Großlappen": "SCE_D1", # "Zulauf Gut Großlappen",
    "WWT Gut Großlappen": "SCE_D2", # "WWT Gut Großlappen",    
    "Gesamt": "Overall",}

manhole_upstream_ordering = {
    "N_Ua": ["N_Ua"],
    "N_Ub": ["N_Ub"],
    "N_Uc": ["N_Uc"],
    "C_U": ["C_U"],

    "S_Ua": ["S_Ua"],
    "S_Ub": ["S_Ub"],
    "E_U": ["E_U"]}
manhole_upstream_ordering["S_M1"] = ["S_M1"] + manhole_upstream_ordering["S_Ua"] + manhole_upstream_ordering["S_Ub"]
manhole_upstream_ordering["S_M2"] = ["S_M2"] + manhole_upstream_ordering["S_M1"] 
manhole_upstream_ordering["S_M3"] = ["S_M3"] + manhole_upstream_ordering["S_M2"] 
manhole_upstream_ordering["S_M4"] = ["S_M4"] + manhole_upstream_ordering["S_M3"] 
manhole_upstream_ordering["E_M"] = ["E_M"] + manhole_upstream_ordering["E_U"]
manhole_upstream_ordering["SCE_D1"] = ["SCE_D1"] + manhole_upstream_ordering["S_M4"] + manhole_upstream_ordering["E_M"] + manhole_upstream_ordering["C_U"] 
manhole_upstream_ordering["SCE_D2"] = manhole_upstream_ordering["SCE_D1"]
manhole_upstream_ordering["N_D"] = ["N_D"] + ["N_Ua", "N_Ub", "N_Uc"]
manhole_upstream_ordering["Overall"] = manhole_upstream_ordering["SCE_D2"] + manhole_upstream_ordering["SCE_D1"] + manhole_upstream_ordering["N_D"]


start_date = "2020-03-02"

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
