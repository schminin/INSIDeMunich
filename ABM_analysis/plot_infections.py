import sys
from plotting_settings import *
import h5py
import pandas as pd
import numpy as np
import geopandas
from datetime import datetime, timedelta
from scipy.stats import pearsonr
import matplotlib.colors as mcolors

"""
This function creates two kinds of plots: 
1) A set of stacked line plots - one for every 2-week time frame - showing the mean number of new infections per location type. The legend is saved as separate image.
2) A set of plots showing the number of infected agents for the (location) types Total, Home, Work, School and Recreation for the whole simulation time frame. Shown is the mean as solid line and the 90% as shaded area.
@param num_sim Number of simulations.
@param save_file Folder the plots are saved to.
@param file_num_infections_loctype Table with the number of infected agents and the number of new infections per LocationType and time point for every simulation. The table should have the following columns: Sim, t, locType, NumInfected, NewInfections, NumAgents
@param width_new_infected, height_new_infected The saved figures for new infections have size width_new_infected x height_new_infected.
@param width_num_infected, height_num_infected The saved figures for the number of infected have size width_num_infected x height_num_infected.
@return The set of stacked line plots saved as new_infections_weeks_{week}and{week+1}.png and the plots with number of infected agents per (location) type saved as infected_{type}.png.
"""    
def plot_infections(num_sim, save_file, file_num_infections_loctype, width_new_infected, height_new_infected, width_num_infected, height_num_infected):  
    # Load data
    output = pd.read_csv(file_num_infections_loctype)

    # Determine number of time points using only the first simulation
    num_time_points = output.loc[output.Sim == 1, 't'].nunique()

    # Define categories
    categories = ['Total', 'Home', 'Work', 'School', 'Shop', 'Recreation']

    # Initialize result dictionaries
    infection_matrices = {
        f'{cat}_{kind}': np.zeros((num_sim, num_time_points))
        for cat in categories
        for kind in ['new_inf', 'infected']
    }

    # Map locType indices to category names and filter relevant rows
    output['Category'] = output['locType'].map(idx_to_loctype_dict)
    output = output[output['Category'].isin(categories)]

    # Process each simulation
    for sim in range(1, num_sim + 1):
        print(f'{sim} / {num_sim}')    
        sim_output = output[output.Sim == sim]

        # Pivot to get time x category matrices
        pivot_new_inf = sim_output.pivot_table(
            index='t', columns='Category', values='NewInfections', fill_value=0
        )
        pivot_infected = sim_output.pivot_table(
            index='t', columns='Category', values='NumInfected', fill_value=0
        )

        # Ensure all categories are present
        for cat in categories[1:]:  # exclude 'Total'
            if cat not in pivot_new_inf.columns:
                pivot_new_inf[cat] = 0
                pivot_infected[cat] = 0

        # Reorder and convert to numpy arrays
        pivot_new_inf = pivot_new_inf[categories[1:]].to_numpy()
        pivot_infected = pivot_infected[categories[1:]].to_numpy()

        # Compute totals
        total_new_inf = pivot_new_inf.sum(axis=1)
        total_infected = pivot_infected.sum(axis=1)

        # Insert into infection_matrices
        infection_matrices['Total_new_inf'][sim - 1] = total_new_inf
        infection_matrices['Total_infected'][sim - 1] = total_infected

        for i, cat in enumerate(categories[1:]):
            infection_matrices[f'{cat}_new_inf'][sim - 1] = pivot_new_inf[:, i]
            infection_matrices[f'{cat}_infected'][sim - 1] = pivot_infected[:, i]

    color_map = {
        'Total': 'black', 'Home': loctype_to_color_dict['Home'], 'Recreation': loctype_to_color_dict['Recreation'],
        'Work': loctype_to_color_dict['Work'], 'School': loctype_to_color_dict['School'], 'Shop': loctype_to_color_dict['Shop']
    }

    # Plot new infections mean with one plot every two weeks
    step_size = 24 * 14
    week = 1
    t_lockdown = 24 * 19
    # Figsize in inches
    figsize = (width_new_infected, height_new_infected)
    for t in range(1, num_time_points, step_size):
        fig, ax = plt.subplots(figsize=figsize)
        # We want to exclude t=0
        if(t == 1):
            step_size = 24 * 14 - 1
        # The last time period can be shorter than two weeks
        elif t > num_time_points - step_size:
            step_size = num_time_points - t
        else:
            step_size = 24 * 14
        # Bottom values for stacked line plot
        bottom = np.zeros(step_size)
        for cat in categories:
            # Total number of new infections is not plotted
            if cat == 'Total':
                continue
            label = cat
            # Get submatrix for the considered two weeks
            matrix = infection_matrices[f'{cat}_new_inf'][:, t:t+step_size]
            # Get mean values
            mean_vals = matrix.mean(axis=0)
            # Percentiles are not plotted
            p5 = np.quantile(matrix, 0.05, axis=0)
            p95 = np.quantile(matrix, 0.95, axis=0)
            x = np.arange(t, t + step_size)
            ax.fill_between(x, bottom, bottom + mean_vals, color=color_map[label], lw=axes_width_a * 0)
            bottom += mean_vals
        if(t_lockdown >= t and t_lockdown < t + step_size):
            ax.axvline(x=t_lockdown, color=colors['Red'], linestyle='--')
        
        # x-ticks positions
        xticks = np.arange(t, t + step_size, 2*24)
        ax.set_xticks(xticks)
        # Convert xlabels to dates starting from March 1
        start_date = datetime(2020, 3, 2)
        labels = [(start_date + timedelta(hours=int(i))).strftime('%d %b') for i in xticks]
        # Set the labels
        ax.set_xticklabels(labels, rotation=30)
        ax.set_ylabel('New infections [#]')
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        fig.suptitle(f'Week {week} and {week+1}', y=0.97)
        fig.savefig(f'{save_file}/new_infections_weeks_{week}and{week+1}.png', dpi=dpi)
        # Increase week
        week += 2

    #Figure with legend only
    patchList = []
    for key in categories:
        if key == 'Total':
                continue
        data_key = patches.Patch(color=color_map[key], label=key)
        patchList.append(data_key)

    fig = plt.figure(figsize=(figsize[0]*2, figsize[1]/1.5))
    legend = fig.legend(handles=patchList, loc='center left', bbox_to_anchor=(0, 0.5), ncol = 5)
    fig.savefig(f'{save_file}/legend.png', dpi=dpi)
    
    # Plot num infected per loc type
    # Figsize in inches
    figsize = (width_num_infected, height_num_infected)
    # Create one subplot for every location type
    for index, cat in enumerate(categories):
        fig, ax = plt.subplots(figsize=figsize)
        label = cat
        matrix = infection_matrices[f'{cat}_infected']
        # Calculate mean values and percentiles
        mean_vals = matrix.mean(axis=0)
        p5 = np.quantile(matrix, 0.05, axis=0)
        p95 = np.quantile(matrix, 0.95, axis=0)
        x = np.arange(num_time_points)
        ax.plot(x, mean_vals, color=color_map[label], label=label)
        ax.fill_between(x, p5, p95, alpha=0.25, color=color_map[label])
        ax.axvline(x=t_lockdown, color=colors['Red'], linestyle='--')
        # x-ticks positions
        xticks = np.arange(0, num_time_points, 14*24)
        ax.set_xticks(xticks)
        # Convert xlabels to dates starting from March 2
        start_date = datetime(2020, 3, 2)
        labels = [(start_date + timedelta(hours=int(i))).strftime('%d %b') for i in xticks]
        # Set the labels
        ax.set_xticklabels(labels, rotation=30)
        ax.set_ylabel('Infected [#]')
        plt.tight_layout()
        fig.savefig(f'{save_file}/infected_{cat}.png', dpi=dpi)
        
        #Figure with legend only
        patchList = []
        for key in categories:
            data_key = patches.Patch(color=color_map[key], label=key)
            patchList.append(data_key)

        fig = plt.figure(figsize=(figsize[0]*2, figsize[1]/1.5))
        legend = fig.legend(handles=patchList, loc='center left', bbox_to_anchor=(0, 0.5), ncol = 6)
        fig.savefig(f'{save_file}/legend_w_total.png', dpi=dpi)

"""
This function plots a set of heatmaps at given time points showing the number of infected agents per wastewater area divided by the total number of agents in the area (mean accross all simulations).
@param shape_wastewater_areas Shape file of wastewater areas.
@param num_infected_per_area_file Table with the number of infected agents and the number of new infections per wastewater area and time point for every simulation. The table should have the following columns: Sim, t, area, NumInfected, NewInfections, NumAgents
@param time_points Time points for which the heat maps should be created.
@param save_file Folder the heat maps should be saved to.
@param width_in_in, height_in_in The saved figure has size width_in_in x height_in_in.
@param considered_sims Simulations whose mean should be plottet
@return Set of heat maps saved as infections_heatmap_{date}.png.
"""    
def plot_num_infections_heatmap(shape_wastewater_areas, num_infected_per_area_file, time_points, save_file, width_in_in, height_in_in, considered_sims = []):
    # Read wastewater shape file
    ww_shape = geopandas.read_file(shape_wastewater_areas)
    # Add column for every time point
    for t in time_points:
        ww_shape[str(t)] = 0.0
    # Read simulation output
    output = pd.read_csv(num_infected_per_area_file, sep=',')
    if(len(considered_sims) > 0):
        output = output[output.Sim.isin(considered_sims)]
    
    for t in time_points:
        for area in ww_shape['ID_TAN'].unique():
            # Get subdf for current area and time point
            sub_df = output[(output.area == area) & (output.t == t)].copy()
            sub_df['Incidence'] = sub_df.NumInfected / sub_df.NumAgents
            ww_shape.loc[ww_shape.index[ww_shape['ID_TAN'] == area], str(t)] = sub_df.Incidence.mean()
            
    # Figsize in inches
    figsize = (width_in_in, height_in_in)        
    # Get min and max value for colorbar
    all_values = ww_shape[[str(t) for t in time_points]].values.flatten()
    vmin = all_values.min()
    vmax = all_values.max()
    for index, t in enumerate(time_points):
        fig, ax = plt.subplots(figsize = figsize)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_axis_off()
        date = (datetime(2020, 3, 2) + timedelta(hours=int(t))).strftime('%d %b')
        ax.set_title(f'{date}')
        ww_shape.plot(column=str(t), ax=ax, cmap = cmap, edgecolor='black', vmin=vmin, vmax=vmax, lw=0.3)           
        plt.tight_layout()
        fig.savefig(save_file + f'/infections_heatmap_{date}_{int(t) % 24}.png', dpi=dpi)
    # Plot joint colorbar
    # Create ScalarMappable for colorbar
    sm = matplotlib.cm.ScalarMappable(cmap=cmap, norm=matplotlib.colors.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []

    # Add a colorbar axis
    fig, ax = plt.subplots(figsize = figsize)
    cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
    cbar.set_label('Relative prevalence')
    cbar.outline.set_linewidth(axes_width_a)  # default is usually 1.0 or more
    #cbar.ax.tick_params(width = axes_width_a, length = length_tick_lines_a, which = 'both')
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(save_file + f'/infections_heatmap_cbar.png', dpi=dpi)


def plot_relative_infections_per_hh_size_and_ag(num_infections_hh_size_ag, save_file, width_in_in, height_in_in):
    num_hh_sizes = 7
    num_age_groups = 6
    # Read output file
    output = pd.read_csv(num_infections_hh_size_ag, sep=',')
    
    unique_sims = output['Sim'].unique()
    unique_t = output['t'].unique()
    num_sims = len(unique_sims)
    num_timesteps = len(unique_t)

    # Create a mapping from Sim to index (0-based row in matrix)
    sim_to_idx = {sim: idx for idx, sim in enumerate(unique_sims)}

    # Create empty matrices
    infection_matrices = {
        f'rel_infected_hhsize_{hh_size}': np.zeros((num_sims, num_timesteps))
        for hh_size in range(1, num_hh_sizes + 1)
    }
    infection_matrices.update({
        f'rel_infected_ag_{ag}': np.zeros((num_sims, num_timesteps))
        for ag in range(num_age_groups)
    })

    # Index the DataFrame for faster access
    output.set_index(['Sim', 't'], inplace=True)

    # Fill matrices
    for (sim, t), row in output.iterrows():
        sim_idx = sim_to_idx[sim]
        print(f'{sim_idx} / {num_sims}')
        t_idx = int(t)  # assuming t starts from 0 and increments by 1
        
        for hh_size in range(1, num_hh_sizes + 1):
            num_inf = row[f'NumInfected{hh_size}HH']
            num_agents = row[f'NumAgents{hh_size}HH']
            if num_agents > 0:
                infection_matrices[f'rel_infected_hhsize_{hh_size}'][sim_idx, t_idx] = num_inf / num_agents

        for ag in range(num_age_groups):
            num_inf = row[f'NumInfectedAg{ag}']
            num_agents = row[f'NumAgentsAg{ag}']
            if num_agents > 0:
                infection_matrices[f'rel_infected_ag_{ag}'][sim_idx, t_idx] = num_inf / num_agents
    
    used_colors = [colors['Dark grey'], colors['Dark red'], colors['Orange'], colors['Brown'], colors['Dark green'], colors['Cadet blue'], colors['Dark blue']]
    t_lockdown = 24 * 19
    figsize = (width_in_in, height_in_in)
    # Plot relative infected per household size            
    fig, ax = plt.subplots(figsize=figsize)
    legend = {}
    for hh_size in range(1, num_hh_sizes + 1):
        label = f'Household size {hh_size}'
        legend[label] = used_colors[hh_size - 1]
        matrix = infection_matrices[f'rel_infected_hhsize_{hh_size}']
        # Calculate mean values and percentiles
        mean_vals = matrix.mean(axis=0)
        p5 = np.quantile(matrix, 0.05, axis=0)
        p95 = np.quantile(matrix, 0.95, axis=0)
        x = np.arange(num_timesteps)
        ax.plot(x, mean_vals, color=used_colors[hh_size - 1], label=label)
        ax.fill_between(x, p5, p95, alpha=0.15, color=used_colors[hh_size - 1])
        ax.axvline(x=t_lockdown, color=colors['Red'], linestyle='--')
        # x-ticks positions
        xticks = np.arange(0, num_timesteps, 14*24)
        ax.set_xticks(xticks)
        # Convert xlabels to dates starting from March 2
        start_date = datetime(2020, 3, 2)
        labels = [(start_date + timedelta(hours=int(i))).strftime('%d %b') for i in xticks]
        # Set the labels
        ax.set_xticklabels(labels, rotation=30)
        ax.set_ylabel('Relative prevalence')
        plt.tight_layout()
        fig.savefig(f'{save_file}/infected_per_hh_size.png', dpi=dpi)
        
    #Figure with legend only
    patchList = []
    for key in legend:
        data_key = patches.Patch(color=legend[key], label=key)
        patchList.append(data_key)

    fig = plt.figure(figsize=figsize)
    legend = fig.legend(handles=patchList, loc='center left', bbox_to_anchor=(0, 0.5), ncol = 1)
    fig.savefig(f'{save_file}/legend_households.png', dpi=dpi)
    
    # Plot relative infected per age group
    fig, ax = plt.subplots(figsize=figsize)
    legend = {}
    for ag in range(num_age_groups):
        label = f'Age goup {idx_to_age_group[ag]}'
        legend[label] = used_colors[ag]
        matrix = infection_matrices[f'rel_infected_ag_{ag}']
        # Calculate mean values and percentiles
        mean_vals = matrix.mean(axis=0)
        p5 = np.quantile(matrix, 0.05, axis=0)
        p95 = np.quantile(matrix, 0.95, axis=0)
        x = np.arange(num_timesteps)
        ax.plot(x, mean_vals, color=used_colors[ag], label=label)
        ax.fill_between(x, p5, p95, alpha=0.15, color=used_colors[ag])
        ax.axvline(x=t_lockdown, color=colors['Red'], linestyle='--')
        # x-ticks positions
        xticks = np.arange(0, num_timesteps, 14*24)
        ax.set_xticks(xticks)
        # Convert xlabels to dates starting from March 2
        start_date = datetime(2020, 3, 2)
        labels = [(start_date + timedelta(hours=int(i))).strftime('%d %b') for i in xticks]
        # Set the labels
        ax.set_xticklabels(labels, rotation=30)
        ax.set_ylabel('Relative prevalence')
        plt.tight_layout()
        fig.savefig(f'{save_file}/infected_per_ag.png', dpi=dpi)
        
    #Figure with legend only
    patchList = []
    for key in legend:
        data_key = patches.Patch(color=legend[key], label=key)
        patchList.append(data_key)

    fig = plt.figure(figsize=figsize)
    legend = fig.legend(handles=patchList, loc='center left', bbox_to_anchor=(0, 0.5), ncol = 1)
    #legend.get_frame().set_linewidth(axes_width_a)
    fig.savefig(f'{save_file}/legend_ag.png', dpi=dpi)

def scatter_plot_new_infections_locs(num_infections_area, csv_num_locs_area, save_file, width_in_in, height_in_in):
    print('1')
    df_output = pd.read_csv(num_infections_area, sep=',')
    print('2')
    df_loc_per_area = pd.read_csv(csv_num_locs_area, sep=',')
    print('3')
    
    num_hh_sizes = 7
    loc_types = loctype_to_color_dict.keys()
    num_sims = len(df_output.Sim.unique())
    
    # Get number total number of new infections per area
    # Group by 'area' and 'Sim', then sum 'NewInfections'
    grouped = df_output.groupby(['area', 'Sim'])['NewInfections'].sum().unstack(fill_value=0)

    # Convert to the desired dict format
    new_infections = grouped.to_dict(orient='index')

    # If you specifically want lists, not Series:
    new_infections = {area: grouped.loc[area].tolist() for area in grouped.index}

    print('4')
    figsize = (width_in_in, height_in_in)      
    # Plot new infections per relative number of locations per location type
    for type in loc_types:
        X = []
        Y = []
        for index, row in df_loc_per_area.iterrows():
            X.append(row[type] / row.Total)
            Y.append(np.mean(new_infections[row.Area]))
        fig, ax = plt.subplots(figsize = figsize)
        pearson_corr, p_value = pearsonr(X, Y)
        ax.scatter(X, Y, color=loctype_to_color_dict[type], label = f'corr = {pearson_corr}')
        ax.set_ylabel('Mean number of\ncumulative new infections')
        ax.set_xlabel(f'Relative number of {type} locations')
        ax.legend()
        plt.tight_layout()
        fig.savefig(f'{save_file}/corr_{type}.png', dpi=dpi)
        
    # Plot new infections per relative number of locations per location type
    for hh_size in range(1, num_hh_sizes + 1):
        X = []
        Y = []
        for index, row in df_loc_per_area.iterrows():
            X.append(row[f'{hh_size}-Person HH'] / row.Total)
            Y.append(np.mean(new_infections[row.Area]))
        fig, ax = plt.subplots(figsize = figsize)
        pearson_corr, p_value = pearsonr(X, Y)
        ax.scatter(X, Y, color=loctype_to_color_dict[type], label = f'corr = {pearson_corr}', lw=axes_width_a * 3)
        ax.set_ylabel('Mean number of\ncumulative new infections', labelpad=ylabelpad)
        ax.set_xlabel(f'Relative number of {hh_size}-person households', labelpad=xlabelpad)
        ax.legend()
        plt.tight_layout()
        fig.savefig(f'{save_file}/corr_{hh_size}_P_HH.png', dpi=dpi)

num_sims = 100
save_file = ''
file_num_infections_loctype = 'num_agents_infections_loctype_pop8.txt'
file_num_infections_area = 'num_agents_infections_area_pop8.txt'
file_num_infections_hh_size_ag = 'num_agents_infections_hh_size_ag_pop8.txt'
csv_num_locs = 'locs_per_ww_areas.csv'
plot_infections(num_sims, save_file, file_num_infections_loctype, 4.5, 3.5, 4.5, 3.5)
plt.close()
time_points = [0, 24*14, 24*30, 24*60]
considered_sims = []
plot_num_infections_heatmap(ww_data_shp_file, file_num_infections_area, time_points, save_file, 3, 3, considered_sims)
plt.close()
plot_relative_infections_per_hh_size_and_ag(file_num_infections_hh_size_ag, save_file, 7, 5)
plt.close()
