from plotting_settings import *
from datetime import datetime, timedelta

"""
This function plots a set of heatmaps at given time points showing the number of agents per age group per wastewater area divided by the total number of agents in the area (mean accross all simulations).
The considered age groups in years are: 0-4, 5-15, 16-34, 35-59, 60-79, 80+
@param shape_wastewater_areas Shape file of wastewater areas.
@param num_agents_per_area_file Table with the number of agents per wastewater area and time point. The table should have the following columns: t, area, AgeGroup, NumAgents
@param timepoints List with time points that should be plotted.
@param timepoint_names List with subplot titles.
@param save_file File the figure should be saved to.
@param width_in_in, height_in_in The saved figure has size width_in_in x height_in_in.
@param cmap Used colormap.
@param considered_sims Simulations whose mean should be plottet.
@return Set of heat maps saved as map_num_agents_{age}_{date}_{time_point_names[index]}.png
"""    
def plot_population_movement_per_agegroup(shape_wastewater_areas, num_agents_per_area_file_ag, time_points, time_point_names, save_file, width_in_in, height_in_in, cmap, considered_sims = []):
    # Figsize in inches
    figsize = (width_in_in, height_in_in)
    # Read wastewater shape file
    ww_shape = geopandas.read_file(shape_wastewater_areas)
    # Read simulation output
    output = pd.read_csv(num_agents_per_area_file_ag, sep=',')
    if(len(considered_sims) > 0):
        output = output[output.Sim.isin(considered_sims)]
    output['rel_num'] = output.NumAgents / output.groupby(['Sim', 't', 'area']).NumAgents.transform('sum')

    # Precompute mean relative numbers per (t, AgeGroup, area)
    grouped = output.groupby(['t', 'AgeGroup', 'area'])['rel_num'].mean().reset_index()

    # Pivot to create one row per area, with multi-indexed columns
    pivot_df = grouped.pivot_table(index='area', columns=['t', 'AgeGroup'], values='rel_num')

    # Flatten multi-indexed columns
    pivot_df.columns = [f"{t}_{age}" for t, age in pivot_df.columns]

    # Reindex to ensure all areas in ww_shape are included
    pivot_df = pivot_df.reindex(ww_shape['ID_TAN']).fillna(0).reset_index(drop=True)

    # Concatenate in a single operation (preserves GeoDataFrame structure)
    ww_shape = pd.concat([ww_shape.reset_index(drop=True), pivot_df], axis=1)
    
    for age in age_groups:
        all_values = ww_shape[[f"{t}_{age}" for t in time_points]].values.flatten()
        for index, t in enumerate(time_points):
            fig, ax = plt.subplots(figsize=figsize)
            fig.suptitle(f'Age group {age}', y = 0.92)
            date = (datetime(2020, 3, 2) + timedelta(hours=int(t))).strftime('%d %b')
            ax.set_title(f'{date}')
            ax.set_axis_off()

            vmin = all_values.min()
            vmax = all_values.max()
            ww_shape.plot(column=f"{t}_{age}", ax=ax, cmap = cmap, edgecolor='black', vmin=vmin, vmax=vmax, lw=0.3)
            plt.tight_layout()
            fig.savefig(save_file + f'/map_num_agents_{age}_{date}_{time_point_names[index]}.png', dpi=dpi)
            
        # Plot joint colorbar
        # Create ScalarMappable for colorbar
        sm = matplotlib.cm.ScalarMappable(cmap=cmap, norm=matplotlib.colors.Normalize(vmin=vmin, vmax=vmax))
        sm._A = []

        fig, ax = plt.subplots(figsize = figsize)
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical')
        cbar.set_label('Relative number of individuals')
        cbar.outline.set_linewidth(axes_width_a)
        ax.set_axis_off()
        plt.tight_layout()
        fig.savefig(save_file + f'/map_num_agents_{age}_cbar.png', dpi=dpi)

"""
This function generates a line plot with the relative number of infected agents over time and the relative number of agents per age group over time for a given wastewater area.
@param num_agents_per_area_file Table with the number of agents per wastewater area and time point. The table should have the following columns: t, area, AgeGroup, NumAgents
@param num_infected_per_area_file Table with the number of infected agents and the number of new infections per wastewater area and time point for every simulation. The table should have the following columns: Sim, t, area, NumInfected, NewInfections, NumAgents
@param ww_areas Considered wastewater areas.
@param considered_age_groups Considered age groups.
@param save_file File the figure should be saved to.
@param width_in_in, height_in_in The saved figure has size width_in_in x height_in_in.
@param colors_incidence Colors for incidence per wastewater area.
@param color_dict_age_groups Color for every age group for every wastewater area.
@param considered_sims Simulations whose mean should be plottet.
@return Line plot saved as infected_num_agents_per_ag_area_{ww_area}.png.png
"""
def plot_infected_vs_agents_per_ag(num_agents_per_area_file_ag, num_infected_per_area_file, ww_areas, considered_age_groups, save_file, width_in_in, height_in_in, colors_incidence, color_dict_age_groups, considered_sims = []):
    # Read simulation output
    output_num_agents = pd.read_csv(num_agents_per_area_file_ag, sep=',')
    output_num_agents = output_num_agents[output_num_agents.area.isin(ww_areas)]
    if(len(considered_sims) > 0):
        output_num_agents = output_num_agents[output_num_agents.Sim.isin(considered_sims)]
    # Create columns with relative values
    output_num_agents['rel_num'] = output_num_agents.NumAgents / output_num_agents.groupby(['Sim', 't', 'area']).NumAgents.transform('sum')
    output_infected = pd.read_csv(num_infected_per_area_file, sep=',')
    output_infected = output_infected[output_infected.area.isin(ww_areas)]
    if(len(considered_sims) > 0):
        output_infected = output_infected[output_infected.Sim.isin(considered_sims)]
    output_infected['Incidence'] = output_infected.NumInfected / output_infected.NumAgents
    
    # Figsize in inches
    figsize = (width_in_in, height_in_in)
    fig, ax = plt.subplots(figsize = figsize)
    ax2 = ax.twinx()
    ax.set_ylabel('Relative number of infected')
    ax2.set_ylabel('Relative number of individuals')
    xticks = np.arange(0, len(output_infected.t.unique()), 14*24)
    ax.set_xticks(xticks)
    # Convert xlabels to dates starting from March 2
    start_date = datetime(2020, 3, 2)
    labels = [(start_date + timedelta(hours=int(i))).strftime('%d %b') for i in xticks]
    # Set the labels
    ax.set_xticklabels(labels, rotation=30)
    legend = {}
    for index, area in enumerate(ww_areas):
        # Plot incidence
        summary = output_infected[output_infected.area == area].groupby('t')['Incidence'].agg([
            ('mean', 'mean'),
            ('p5', lambda x: x.quantile(0.05)),
            ('p95', lambda x: x.quantile(0.95))])
        label = f'Incidence area {area}'
        color = colors_incidence[index]
        legend[label] = color
        ax.plot(summary.index, summary['mean'], label=label, color = color)
        ax.fill_between(summary.index, summary['p5'], summary['p95'], alpha=0.2, color = color)
    # Plot relative number of agents per age group
    for age in considered_age_groups:
        for index, area in enumerate(ww_areas):
            ag_df = output_num_agents[(output_num_agents.AgeGroup == age) & (output_num_agents.area == area)]
            summary = ag_df.groupby('t')['rel_num'].agg([
            ('mean', 'mean'),
            ('p5', lambda x: x.quantile(0.05)),
            ('p95', lambda x: x.quantile(0.95))])
            label = f'Age group {age} area {area}'
            color = color_dict_age_groups[age][index]
            legend[label] = color
            ax2.plot(summary.index, summary['mean'], label=label, color = color)
            ax2.fill_between(summary.index, summary['p5'], summary['p95'], alpha=0.2, color = color)
    save_str = "areas_"
    for area in ww_areas:
        save_str += f'{area}'
    save_str += "ag_"
    for age in considered_age_groups:
        save_str += f'{age}'
    plt.tight_layout()
    fig.savefig(f'{save_file}/infected_num_agents_per_ag_area_{save_str}.png', dpi=dpi)
    
    #Figure with legend only
    patchList = []
    for key in legend:
        data_key = patches.Patch(color=legend[key], label=key)
        patchList.append(data_key)

    fig = plt.figure(figsize=figsize)
    legend = fig.legend(handles=patchList, loc='center left', bbox_to_anchor=(0, 0.5), ncol = 1)
    #legend.get_frame().set_linewidth(axes_width_a)
    fig.savefig(f'{save_file}/legend_area_{save_str}.png', dpi=dpi)

save_file = ''
num_agents_per_area_file_ag = 'num_agents_area_ag.txt'
file_num_infections_area = 'num_agents_infections_area.txt'
time_points = [get_time_point(0, 0)]
timepoint_names = ['12am']
cmap = 'viridis_r'
considered_sims = []
     
plot_population_movement_per_agegroup(ww_data_shp_file, num_agents_per_area_file_ag, time_points, timepoint_names, save_file, 3, 3, cmap, considered_sims)
plt.close()

ww_areas = [1, 58]
considered_ages = ['5-15']
colors_incidence = ['orange', 'red']
color_dict_age_groups = {'5-15': ['blue', 'green']}
plot_infected_vs_agents_per_ag(num_agents_per_area_file_ag, file_num_infections_area, ww_areas, considered_ages, save_file, 7, 5, colors_incidence, color_dict_age_groups)
