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
@param considered_sims Simulations whose mean should be plottet
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

    # Considered age groups
    age_groups = ['0-4', '5-15', '16-34', '35-59', '60-79', '80+']

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

save_file = ''
num_agents_per_area_file_ag = 'num_agents_area_ag.txt'
time_points = [get_time_point(0, 0)]
timepoint_names = ['12am']
cmap = 'viridis_r'
considered_sims = []
     
plot_population_movement_per_agegroup(ww_data_shp_file, num_agents_per_area_file_ag, time_points, timepoint_names, save_file, 3, 3, cmap, considered_sims)
plt.close()
