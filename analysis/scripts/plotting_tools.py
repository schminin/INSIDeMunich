import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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