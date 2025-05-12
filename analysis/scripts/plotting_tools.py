import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def set_fontsize(base_fontsize=15):
    fontsize = base_fontsize
    plt.rcParams.update({
        'font.size': fontsize,
        'axes.titlesize': fontsize * 1.2,
        'axes.labelsize': fontsize,
        'xtick.labelsize': fontsize * 0.8,
        'ytick.labelsize': fontsize * 0.8,
        'legend.fontsize': fontsize * 0.9
    })

set_fontsize()

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

start_date = "2020-03-02"