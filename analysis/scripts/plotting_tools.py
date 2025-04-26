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
    "MUC012": "Am Langwieder Bach",
    "MUC060": "Gräfelfinger Str.", # (not including Waldwiesenstr.)
    "MUC362": "Schenkendorfstr.",
    "MUC348": "Schmidbartlanger",
    "MUC494": "Savitstr.",
    "MUC608": "Gyßlinger Becken",
    "MUC600": "Leopoldstr.",
    "MUC112": "Botanischer Garten", # (not including Menzinger Str. )
    "MUC560": "Wintersteinstr.", # Hasenbergl
    "MUC434": "WWT Gut Großlappen",
    "MUC562": "WWT Gut Marienhof",
    "MUC586": "Gesamt",}

start_date = "2020-03-01"