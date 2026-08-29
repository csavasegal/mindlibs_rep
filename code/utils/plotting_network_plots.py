import os 
import pandas as pd 
from statsmodels.stats.multitest import multipletests
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

    
UTIL_DIR = os.path.dirname(os.path.abspath(__file__))

def load_mapping():
    file_path = os.path.join(UTIL_DIR, "7N_to_17N_complete_mapping.csv")
    return pd.read_csv(file_path)

mapping_df = load_mapping()

def plot_17N_effect_distribution_horizontal(network_df, node_df, min_val_manual,max_val_manual,x_offset=.2, effect="reappraisal_semanticdist_miniLM_L6", 
                                           output_folder='../../plots', ascending=True, sort_by_effect=False, 
                                           show_bars=True, plot_stars = True, show_error_bars=False):
    """
    Create horizontal plot for 17-Network parcellation with flexible visualization options
    
    Parameters:
    -----------
    network_df : DataFrame
        Network-level results with 17N network labels
    node_df : DataFrame
        Node-level results
    effect : str
        Effect name to plot
    output_folder : str
        Where to save plots
    sort_by_effect : bool
        If True, sort networks by effect size. If False, sort by network family grouping.
    show_bars : bool
        If True, show bars with small dots overlay (Option 3).
        If False, show boxplots with large network-level dots (Option 4), sorted by effect.
    show_error_bars : bool
        If True and show_bars=True, add error bars showing standard error or confidence intervals.
    """
    
    from matplotlib.lines import Line2D  # Import at the top
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Load network mappings
    # mapping_df = pd.read_csv('7N_to_17N_complete_mapping.csv')


    # Create 17N network indices
    network_17N_indices = {}
    for network in mapping_df['Network_17N'].unique():
        nodes = mapping_df[mapping_df['Network_17N'] == network]['Node_Number'].tolist()
        network_17N_indices[network] = sorted(nodes)
    
    # 17N network order for plotting (grouped by parent network)
    network_order = [
        'VisCent', 'VisPeri',                          # Visual
        'SomMotA', 'SomMotB',                          # Somatomotor
        'LimbicA', 'LimbicB',                          # Limbic
        'TempPar',                                      # TempPar
        # 'DorsAttnA', 'DorsAttnB',                      # Dorsal Attention
        # 'SalVentAttnA', 'SalVentAttnB',                # Salience/Ventral Attention
        #'ContA', 'ContB', 'ContC',                     # Control
        #'DefaultA', 'DefaultB', 'DefaultC'             # Default
        "DAN-A", "DAN-B", 
        "VAN-A", "VAN-B", 
        "FPN-A","FPN-B","FPN-C",
        "DMN-A", "DMN-B", "DMN-C"
    ]
    
    network_df['network'] = network_df['network'].replace({'ContA':'FPN-A','ContB':'FPN-B','ContC':'FPN-C','DefaultA':'DMN-A','DefaultB':'DMN-B','DefaultC':'DMN-C','SalVentAttnA':'VAN-A','SalVentAttnB':'VAN-B', 'DorsAttnA':'DAN-A','DorsAttnB':'DAN-B'})
    print(np.unique(list(network_df['network'])))
    print('renamed them!')

    # Get color scheme
    colors_17N = create_17N_color_scheme()
    
    # Create network lookup for each node
    node_to_network = {}
    for network, nodes in network_17N_indices.items():
        for node in nodes:
            node_to_network[node] = network
    
    # Map nodes to networks
    node_df = node_df.copy()
    node_df['network'] = node_df['node'].map(node_to_network)
    node_df = node_df.dropna(subset=['network'])
    
    print(f"\nCreating horizontal 17N distribution plot for: {effect}")
    print(f"Mode: Bar graph only")
    
    estimate_col = f"{effect}_estimate"
    
    # Get network-level results for this effect
    network_effect_data = network_df[network_df['effect'] == effect].copy()
    
    # Prepare node-level data
    plot_data = node_df[['node', 'network', estimate_col]].copy()
    plot_data.columns = ['node', 'network', 'estimate']
    plot_data = plot_data.dropna()
    plot_data['network'] = plot_data['network'].replace({'ContA':'FPN-A','ContB':'FPN-B','ContC':'FPN-C', 'DefaultA':'DMN-A', 'DefaultB':'DMN-B', 'DefaultC':'DMN-C',
                                                        'DorsAttnA':'DAN-A', 'DorsAttnB':'DAN-B', 'SalVentAttnA':'VAN-A', 'SalVentAttnB':'VAN-B'})
    network_effect_data['network'] = network_effect_data['network'].replace({'ContA':'FPN-A','ContB':'FPN-B','ContC':'FPN-C','DefaultA':'DMN-A', 'DefaultB':'DMN-B', 'DefaultC':'DMN-C',
                                                        'DorsAttnA':'DAN-A', 'DorsAttnB':'DAN-B', 'SalVentAttnA':'VAN-A', 'SalVentAttnB':'VAN-B'})

                                                                        
    
    # If showing boxplots, always sort by effect
    if not show_bars:
        sort_by_effect = True
    
    # Determine network order based on sorting option
    if sort_by_effect:
        # Sort by network-level effect size
        network_means = network_effect_data.set_index('network')['estimate'].to_dict()
        networks_present = [net for net in network_order if net in plot_data['network'].unique()]
        networks_present_sorted = sorted(networks_present, key=lambda x: network_means.get(x, 0), reverse=ascending)
        print(f"Sorting by effect size")
    else:
        # Use original network family grouping order
        plot_data['network'] = pd.Categorical(plot_data['network'], categories=network_order, ordered=True)
        plot_data = plot_data.sort_values('network',ascending=ascending)
        networks_present_sorted = [net for net in network_order if net in plot_data['network'].unique()]
        print(f"Sorting by network family grouping")
    

    # Create figure
    fig, ax = plt.subplots(figsize=(3, 4))
    
    n_networks = len(networks_present_sorted)
    
    # Reverse order for bottom-to-top display
    networks_present_reversed = networks_present_sorted[::-1]
    
    if show_bars:
        # BAR GRAPH ONLY - NO DOTS, NO ERROR BARS
        
        # Prepare data for bars
        bar_data = []
        for network in networks_present_reversed:
            network_beta = network_effect_data[network_effect_data['network'] == network]['estimate'].values
            if len(network_beta) > 0:
                bar_data.append(network_beta[0])
            else:
                bar_data.append(0)
        
        # Create horizontal bars (network-level effects)
        bars = ax.barh(range(n_networks), bar_data,
                       color=[colors_17N.get(net, '#808080') for net in networks_present_reversed],
                       alpha=0.7, edgecolor='black', linewidth=1, height=0.6, zorder=1)
        
        # Calculate flexible axis limits based on actual data
        max_val = max(bar_data)
        min_val = min(bar_data)
        data_range = max_val - min_val
        
        # Add 10% padding on each side
        padding = data_range * 0.40
        xlim_min = min_val - padding
        xlim_max = max_val + padding
        
        # Determine star position dynamically (5% beyond the max extent)
        if abs(max_val) > abs(min_val):
            star_position = max_val + (data_range * 0.1)  # Right side
            star_align = 'left'
        else:
            # star_position = min_val - (data_range * 0.1)  # Left side
            star_position = np.abs(min_val) + (data_range * 0.1)  # Right side FORCE THEM TO BE ON THE RIGHT
            star_align = 'right'
        
        # Add stars for FDR-significant networks - ALIGNED
        for i, network in enumerate(networks_present_reversed):
            network_fdr = network_effect_data[network_effect_data['network'] == network]['p_fdr'].values
            if len(network_fdr) > 0:
                q_value = network_fdr[0]
                
                if q_value < 0.001:
                    stars = '***'
                elif q_value < 0.01:
                    stars = '**'
                elif q_value < 0.05:
                    stars = '*'
                else:
                    stars = ''
                
                if stars and plot_stars:
                    # All stars at the same x position
                    ax.text(star_position, i + x_offset, stars, fontsize=20, fontweight='bold',
                           ha=star_align, va='center', color='black', zorder=5)
        
        # Set flexible x-axis limits
        ax.set_xlim(xlim_min, xlim_max)
        
        legend_elements = [
            Line2D([0], [0], color='gray', linewidth=10, alpha=0.7,
                   label='Network β'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label=''),  # Spacer
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='FDR significance:'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='   * q < 0.05'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='   ** q < 0.01'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='   *** q < 0.001')
        ]
    else:
        # BOXPLOT VERSION (keeping original code for when show_bars=False)
        # Create boxplot
        bp = ax.boxplot([plot_data[plot_data['network'] == net]['estimate'].values 
                         for net in networks_present_reversed],
                        positions=range(n_networks),
                        vert=False,
                        widths=0.6,
                        patch_artist=True,
                        showfliers=False)
        
        # Add individual node dots
        for i, network in enumerate(networks_present_reversed):
            node_estimates = plot_data[plot_data['network'] == network]['estimate'].values
            y_positions = np.random.normal(i, 0.04, size=len(node_estimates))
            ax.scatter(node_estimates, y_positions, alpha=0.4, s=30,
                       color=colors_17N.get(network, '#808080'), zorder=2)
        
        # Color the boxes by network
        for patch, network in zip(bp['boxes'], networks_present_reversed):
            patch.set_facecolor(colors_17N.get(network, '#808080'))
            patch.set_alpha(0.6)
            patch.set_edgecolor('black')
        
        # Add network-level beta coefficients as big black dots
        for i, network in enumerate(networks_present_reversed):
            network_beta = network_effect_data[network_effect_data['network'] == network]['estimate'].values
            if len(network_beta) > 0:
                beta = network_beta[0]
                network_sig = network_effect_data[network_effect_data['network'] == network]['significant'].values[0]
                
                marker_size = 350 if network_sig else 250
                edge_width = 3 if network_sig else 0
                ax.scatter(beta, i, s=marker_size, color='black', marker='o',
                          edgecolors='white' if network_sig else 'none',
                          linewidths=edge_width, zorder=5, alpha=0.95)
        
        # Calculate max extent for aligned star position
        all_estimates = plot_data['estimate'].values
        max_extent = all_estimates.max()
        min_extent = all_estimates.min()
        
        # Determine which side to place stars (where most variation is)
        if abs(max_extent) > abs(min_extent):
            star_position = max_extent + 0.5  # Right side
            star_align = 'left'
        else:
            star_position = min_extent - 0.5  # Left side
            star_align = 'right'
        
        # Add stars for FDR-significant networks - ALIGNED
        for i, network in enumerate(networks_present_reversed):
            network_fdr = network_effect_data[network_effect_data['network'] == network]['p_fdr'].values
            if len(network_fdr) > 0:
                q_value = network_fdr[0]
                
                if q_value < 0.001:
                    stars = '***'
                elif q_value < 0.01:
                    stars = '**'
                elif q_value < 0.05:
                    stars = '*'
                else:
                    stars = ''
                
                if stars:
                    # All stars at the same x position
                    ax.text(star_position, i, stars, fontsize=20, fontweight='bold',
                           ha=star_align, va='center', color='black', zorder=5)
        
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='black',
                   markeredgecolor='white', markersize=13, linewidth=3,
                   label='Network β (significant)'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='black',
                   markersize=10, linewidth=0, alpha=0.95,
                   label='Network β (n.s.)'),
            Line2D([0], [0], color='gray', linewidth=10, alpha=0.6,
                   label='Node distribution (box)'),
            Line2D([0], [0], color='black', linewidth=2,
                   label='Median node β'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label=''),  # Spacer
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='FDR significance:'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='   * q < 0.05'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='   ** q < 0.01'),
            Line2D([0], [0], marker='', color='w', markersize=0, linewidth=0,
                   label='   *** q < 0.001')
        ]
    
    # Add STRONG vertical line at zero
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2.5, alpha=0.8, zorder=4)
    
    # Customize plot
    ax.set_yticks(range(n_networks))
    
    # Create y-axis labels with node count
    y_labels = []
    for network in networks_present_reversed:
        n_nodes = len(plot_data[plot_data['network'] == network])
        y_labels.append(f"{network}")
    
    ax.set_yticklabels(y_labels, fontweight='bold', fontsize=10)
    
    # Color y-axis labels
    for label, network in zip(ax.get_yticklabels(), networks_present_reversed):
        label.set_color(colors_17N.get(network, '#808080'))
    
    # Only draw family grouping lines if showing bars AND NOT sorting by effect
    if show_bars and not sort_by_effect:
        # Add thick colored lines to the RIGHT of y-axis labels to group subnetworks by parent network
        # base_colors = {
        #     'Vis': '#781286',           # Purple
        #     'SomMot': '#4682b4',        # Blue  
        #     'Limbic': '#dcf8a4',        # Light yellow-green
        #     'TempPar': 'blue',          # Blue
        #     'DorsAttn': '#00760e',      # Green
        #     'SalVentAttn': '#c43afb',   # Violet
        #     'Cont': '#e69422',          # Orange
        #     'Default': '#cd3e4e'        # Red
        # }
        base_colors = {
        'Vis': '#781286',           # Purple
        'SomMot': '#4682b4',        # Blue  
        'DorsAttn': '#00760e',      # Green
        'SalVentAttn': '#ee10e7',#'#c43afb',   # Violet
        'Limbic': '#dcf8a4',        # Light yellow-green
        'Cont': '#e69422',          # Orange
        'TempPar': '#4538ec',          # Blue
        'Default': '#d81614'#'#d65f67'        # Red
         }
        
        # Define network families (which subnetworks belong to which parent)
        network_families = {
            'Vis': ['VisCent', 'VisPeri'],
            'SomMot': ['SomMotA', 'SomMotB'],
            'Limbic': ['LimbicA', 'LimbicB'],
            'TempPar': ['TempPar'],
            'DorsAttn': ['DAN-A', 'DAN-B'],
            'SalVentAttn': ['VAN-A', 'VAN-B'],
            #'Cont': ['ContA', 'ContB', 'ContC'],
             'Cont': ['FPN-A', 'FPN-B', 'FPN-C'],
            'Default': ['DMN-A', 'DMN-B', 'DMN-C'],
        }
        
        # Draw thick lines for each network family on the right side of the y-axis
        for family, members in network_families.items():
            # Find which members are present in the plot (in reversed order)
            present_members = [net for net in members if net in networks_present_reversed]
            
            if len(present_members) > 0:
                # Get the y-positions of these networks
                y_positions = [networks_present_reversed.index(net) for net in present_members]
                y_start = min(y_positions) - 0.35
                y_end = max(y_positions) + 0.35
                
                # Draw the thick line on the RIGHT side (outside the y-axis)
                line = ax.plot([0, 0], [y_start, y_end],
                       color=base_colors[family], 
                       linewidth=8, 
                       solid_capstyle='round',
                       transform=ax.get_yaxis_transform(),
                       clip_on=False,
                       zorder=10)
    
    ax.set_xlabel('β', fontsize=13, fontweight='bold')
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, zorder=0)
    ax.set_axisbelow(True)
    
    # Add legend
    show_legend = False  # ← set to True if you want to display it

    if show_legend:
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), framealpha=0.9, fontsize=9)


#     ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9, fontsize=9)
    # Note: xlim is now set dynamically within the show_bars block above
    plt.xlim(min_val_manual, max_val_manual)  # REMOVED - now flexible
    #plt.xlim(min_val_manual,max_val_manual)
    #plt.tight_layout()
    #fig.set_size_inches(3, 4)
    fig.set_size_inches(4, 3)

    fig.subplots_adjust(left=0.28, right=0.90, top=0.97, bottom=0.15)
    
    # Save
    sanitized_effect = effect.replace(" ", "_").replace("-", "_").replace(".", "_")
    mode_suffix = "_bars" if show_bars else "_boxplots"
    sort_suffix = "_sorted" if sort_by_effect else ""
    plt.savefig(os.path.join(output_folder, f"network_distribution_17N_horizontal_{sanitized_effect}{mode_suffix}{sort_suffix}.png"), 
               dpi=300, bbox_inches=None) #bbox_inches='tight')
    plt.show()
    
    # Print summary statistics
    print(f"\n=== {effect} Summary (17N) ===")
    for network in networks_present_sorted:
        network_data = plot_data[plot_data['network'] == network]['estimate']
        network_beta = network_effect_data[network_effect_data['network'] == network]['estimate'].values
        network_fdr = network_effect_data[network_effect_data['network'] == network]['p_fdr'].values
        
        if len(network_beta) > 0 and len(network_fdr) > 0:
            q_value = network_fdr[0]
            if q_value < 0.001:
                sig_label = '***'
            elif q_value < 0.01:
                sig_label = '**'
            elif q_value < 0.05:
                sig_label = '*'
            else:
                sig_label = ''
                
            print(f"\n{network}:")
            print(f"  Network Beta: {network_beta[0]:.4f} {sig_label}")
            print(f"  q-value: {q_value:.4e}")
            print(f"  Node count: {len(network_data)}")
            print(f"  Node mean: {network_data.mean():.4f}")
            print(f"  Node median: {network_data.median():.4f}")
            print(f"  Node std: {network_data.std():.4f}")
            print(f"  Node range: [{network_data.min():.4f}, {network_data.max():.4f}]")
    
    print(f"\n✓ Horizontal 17N distribution plot saved to {output_folder}")
    
    
def get_effect_names(result_df):
    """
    Extract all effect names from the dataframe columns
    """
    estimate_cols = [c for c in result_df.columns if c.endswith('_estimate') and not c.startswith('_')]
    effect_names = [c.replace('_estimate', '') for c in estimate_cols]
    return effect_names

def compare_network_effects(result_df, effects=None, output_folder='plots', plot=False):
    """
    Compare multiple effects across networks
    
    Parameters:
    -----------
    result_df : pd.DataFrame
        DataFrame with network results
    effects : list or None
        List of effect names to compare. If None, uses all available effects.
    output_folder : str
        Folder to save plots
    plot : bool
        If True, also draw the faceted summary figure showing one panel per
        effect in `effects`. Off by default: callers that just need the
        returned table (e.g. plot_17N_effect_distribution_horizontal) would
        otherwise get an unsaved figure of every fixed effect in result_df.
    """
    
    os.makedirs(output_folder, exist_ok=True)
    
    # If no effects specified, get all available effects
    if effects is None:
        effects = get_effect_names(result_df)
        print(f"Comparing all available effects: {effects}")
    
    # Prepare data for multiple effects
    all_data = []
    
    for effect in effects:
        estimate_col = f"{effect}_estimate"
        p_col = f"{effect}_p_value"
        
        if estimate_col not in result_df.columns or p_col not in result_df.columns:
            print(f"Warning: Effect '{effect}' not found, skipping...")
            continue
        
        temp_data = result_df[['network', estimate_col, p_col]].copy()
        temp_data.columns = ['network', 'estimate', 'p_value']
        
        # FDR correction
        _, temp_data['p_fdr'], _, _ = multipletests(temp_data['p_value'], method='fdr_bh')
        temp_data['significant'] = temp_data['p_fdr'] < 0.05
        temp_data['effect'] = effect
        
        all_data.append(temp_data)
    
    if not all_data:
        print("No valid effects found to compare")
        return None
    
    # Combine all effects
    combined_data = pd.concat(all_data, ignore_index=True)
    
    if plot:
        # Create faceted plot
        n_effects = len(all_data)
        fig, axes = plt.subplots(1, n_effects, figsize=(6 * n_effects, 6), sharey=True)
    
        if n_effects == 1:
            axes = [axes]
    
        for idx, effect in enumerate([d['effect'].iloc[0] for d in all_data]):
            ax = axes[idx]
            effect_data = combined_data[combined_data['effect'] == effect].sort_values('estimate')

            # Create bars
            bars = ax.barh(effect_data['network'], effect_data['estimate'],
                          color=[yeo_colors.get(net, '#808080') for net in effect_data['network']],
                          alpha=0.8, edgecolor='black', linewidth=0.5)
        
            # Add asterisks for significant results
            for _, row in effect_data.iterrows():
                if row['significant']:
                    x_pos = row['estimate'] + 0.02 #(0.02 if row['estimate'] > 0 else -0.02)
                    ax.text(x_pos, row['network'], '*',
                           fontsize=20, fontweight='bold', 
                           ha='left' if row['estimate'] > 0 else 'right',
                           va='center')
        
            ax.axvline(x=0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
            ax.set_xlabel('Effect Size', fontsize=11, fontweight='bold')
            # Shorten title if too long
            title = effect if len(effect) < 30 else effect[:27] + "..."
            ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
            ax.grid(axis='x', alpha=0.3)
        
            if idx == 0:
                ax.set_ylabel('Network', fontsize=11, fontweight='bold')
    
        plt.suptitle('Network Effect Sizes Across Multiple Predictors\n* indicates FDR < 0.05', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
    #     plt.savefig(os.path.join(output_folder, 'faceted_network_effects.png'), 
    #                dpi=300, bbox_inches='tight')
    #     plt.close()

    
    return combined_data
def create_17N_color_scheme():
    """
    Create color scheme for 17N networks based on parent 7N network colors.
    Each subnetwork gets a different shade of its parent network color.
    """
    
    # Base 7N colors
    # base_colors = {
    #     'Vis': '#38007a',           # Purple
    #     'SomMot': '#4682b4',        # Blue  
    #     'DorsAttn': '#00760e',      # Green
    #     'SalVentAttn': '#d600b8',   # Violet
    #     'Limbic': '#dcf8a4',        # Light yellow-green
    #     'Cont': '#e69422',          # Orange
    #     'TempPar': 'blue',          # Blue
    #     'Default': '#db0200'#'#d65f67'        # Red
    # }
    base_colors = {
        'Vis': '#781286',           # Purple
        'SomMot': '#4682b4',        # Blue  
        'DorsAttn': '#00760e',      # Green
        'SalVentAttn': '#ee10e7',#'#c43afb',   # Violet
        'Limbic': '#dcf8a4',        # Light yellow-green
        'Cont': '#e69422',          # Orange
        'TempPar': '#4538ec',          # Blue
        'Default': '#d81614'#'#d65f67'        # Red
    }
    
    
    def lighten_color(color, amount=0.2):
        """Lighten a color by mixing with white"""
        c = mcolors.to_rgb(color)
        white = np.array([1, 1, 1])
        return mcolors.to_hex((1 - amount) * np.array(c) + amount * white)
    
    def darken_color(color, amount=0.25):
        """Darken a color by mixing with black"""
        c = mcolors.to_rgb(color)
        black = np.array([0, 0, 0])
        return mcolors.to_hex((1 - amount) * np.array(c) + amount * black)
    
    # Create shades for each 17N subnetwork
    colors_17N = {
        # Visual network - Purple shades
        'VisCent': darken_color(base_colors['Vis'], 0.3),  #darken_color(base_colors['Vis'], 0.2),    # Darker purple
        'VisPeri': lighten_color(base_colors['Vis'], 0.2),   # Lighter purple
        
        # Somatomotor - Blue shades
        'SomMotA': darken_color(base_colors['SomMot'], 0.3),#darken_color(base_colors['SomMot'], 0.2),  # Darker blue
        'SomMotB': lighten_color(base_colors['SomMot'], 0.2), # Lighter blue
        
        # Dorsal Attention - Green shades
        'DAN-A': darken_color(base_colors['DorsAttn'], 0.3), #darken_color(base_colors['DorsAttn'], 0.2),  # Darker green
        'DAN-B': lighten_color(base_colors['DorsAttn'], 0.2), # Lighter green
        
        # Salience/Ventral Attention - Violet shades
        'VAN-A': darken_color(base_colors['SalVentAttn'], 0.4),#darken_color(base_colors['SalVentAttn'], 0.2),  # Darker violet
        'VAN-B': lighten_color(base_colors['SalVentAttn'], 0.1),#lighten_color(base_colors['SalVentAttn'], 0.2), # Lighter violet
        
        # Control - Orange shades
        'FPN-A': darken_color(base_colors['Cont'], 0.4),#, #base_colors['Cont'],                        # Medium orange
        'FPN-B': darken_color(base_colors['Cont'], 0.2), #darken_color(base_colors['Cont'], 0.25),   # Darkest orange
        'FPN-C': base_colors['Cont'],#lighten_color(base_colors['Cont'], 0.2),   # Lightest orange
        
        # Default - Red shades (including what was Limbic)
        'DMN-A': darken_color(base_colors['Default'], 0.3),#darken_color(base_colors['Default'], 0.4),    # Darkest red
        'DMN-B': lighten_color(base_colors['Default'], 0.1),#base_colors['Default'],     # Dark red
        'DMN-C': lighten_color(base_colors['Default'], 0.4),#lighten_color(base_colors['Default'], 0.2),    # Light red
        'LimbicA': darken_color(base_colors['Limbic'], 0.2),
        'LimbicB': darken_color(base_colors['Limbic'], 0.4),
        
        'TempPar': base_colors['TempPar']       }
    
    return colors_17N


# Define Yeo 7-network colors
yeo_colors = {
    "Vis": "#38007a",           # Purple
    "SomMot": "#4682B4",         # Blue
    "DorsAttn": "#00A131",       # Green
    "SalVentAttn": "#d600b8",    # Fuchsia
    "Limbic": "#DCE8A2",         # Cream
    "Cont": "#E69422",           # Orange
    "Default": "#CD3E4E"         # Red
}

def plot_17N_effect_distribution_vertical(
    network_df,
    node_df,
    min_val_manual,max_val_manual,
    x_offset=0.6,
    effect="reappraisal_semanticdist_miniLM_L6",
    output_folder='plots',
    ascending=True,
    sort_by_effect=False,
    show_bars=True):
    """
    Create VERTICAL bar plot for 17-Network parcellation (rotated version of horizontal function)

    Parameters:
    -----------
    network_df : DataFrame
        Network-level results with 17N network labels
    node_df : DataFrame
        Node-level results
    effect : str
        Effect name to plot
    output_folder : str
        Where to save plots
    sort_by_effect : bool
        If True, sort networks by effect size. If False, sort by network family grouping.
    show_bars : bool
        If True, show bars with small dots overlay (Option 3).
        If False, show boxplots with large network-level dots (Option 4), sorted by effect.
    show_error_bars : bool
        (Not used yet)
    """
    from matplotlib.lines import Line2D
    os.makedirs(output_folder, exist_ok=True)

    # Load mapping
    # mapping_df = pd.read_csv('7N_to_17N_complete_mapping.csv')

    # Build network-to-node index
    network_17N_indices = {
        network: sorted(mapping_df[mapping_df['Network_17N'] == network]['Node_Number'].tolist())
        for network in mapping_df['Network_17N'].unique()
    }

    # Canonical order (17N)
#     network_order = [
#         'VisCent', 'VisPeri', 'SomMotA', 'SomMotB',
#         'LimbicA', 'LimbicB', 'TempPar',
#         'DorsAttnA', 'DorsAttnB',
#         'SalVentAttnA', 'SalVentAttnB',
#         'ContA', 'ContB', 'ContC',
#         'DefaultA', 'DefaultB', 'DefaultC'
#     ]

    network_order = [
        'DefaultC', 'DefaultB', 'DefaultA',
        'ContC', 'ContB', 'ContA', 
        'SalVentAttnB','SalVentAttnA', 
        'DorsAttnB','DorsAttnA', 
        'TempPar', 'LimbicB', 'LimbicA', 
        'SomMotB', 'SomMotA', 'VisPeri','VisCent'
         
    ]
    #network_df['network'] = network_df['network'].replace({'ContA':'FPN-A','ContB':'FPN-B','ContC':'FPN-C'})

    colors_17N = create_17N_color_scheme()

    # Map each node → network
    node_to_network = {node: network for network, nodes in network_17N_indices.items() for node in nodes}
    node_df = node_df.copy()
    node_df['network'] = node_df['node'].map(node_to_network)
    node_df = node_df.dropna(subset=['network'])

    print(f"\nCreating vertical 17N distribution plot for: {effect}")

    estimate_col = f"{effect}_estimate"
    network_effect_data = network_df[network_df['effect'] == effect].copy()
    plot_data = node_df[['node', 'network', estimate_col]].copy()
    plot_data.columns = ['node', 'network', 'estimate']
    plot_data = plot_data.dropna()

    if not show_bars:
        sort_by_effect = True

    if sort_by_effect:
        network_means = network_effect_data.set_index('network')['estimate'].to_dict()
        networks_present = [net for net in network_order if net in plot_data['network'].unique()]
        networks_present_sorted = sorted(networks_present, key=lambda x: network_means.get(x, 0), reverse=ascending)
        print("Sorting by effect size")
    else:
        plot_data['network'] = pd.Categorical(plot_data['network'], categories=network_order, ordered=True)
        plot_data = plot_data.sort_values('network', ascending=ascending)
        networks_present_sorted = [net for net in network_order if net in plot_data['network'].unique()]
        print("Sorting by network family grouping")

    n_networks = len(networks_present_sorted)
    networks_present_reversed = networks_present_sorted[::-1]  # same logic for consistent family order

    fig, ax = plt.subplots(figsize=(4, 2.5))

    # --- BAR PLOT ---
    if show_bars:
        bar_data = []
        for network in networks_present_reversed:
            vals = network_effect_data[network_effect_data['network'] == network]['estimate'].values
            bar_data.append(vals[0] if len(vals) > 0 else 0)

        bars = ax.bar(
            range(n_networks),
            bar_data,
            color=[colors_17N.get(net, '#808080') for net in networks_present_reversed],
            alpha=0.7,
            edgecolor='black',
            linewidth=1,
            width=0.6,
            zorder=1
        )

        max_val = max(bar_data)
        min_val = min(bar_data)
        data_range = max_val - min_val
        padding = data_range * 0.01
        ylim_min = min_val - padding
        ylim_max = max_val + padding

        # Dynamic star position
        if abs(max_val) > abs(min_val):
            star_position = max_val + (data_range * 0.05)
            star_align = 'center'
        else:
            star_position = min_val - (data_range * 0.05)
            star_align = 'center'

        # Add stars
        for i, network in enumerate(networks_present_reversed):
            q_vals = network_effect_data[network_effect_data['network'] == network]['p_fdr'].values
            if len(q_vals) > 0:
                q = q_vals[0]
                if q < 0.001:
                    stars = '***'
                elif q < 0.01:
                    stars = '**'
                elif q < 0.05:
                    stars = '*'
                else:
                    stars = ''

                if stars:
                    ax.text(
                        i + x_offset,      # shift horizontally by axis offset
                        1.02,              # position vertically in AXIS coords
                        stars,
                        transform=ax.get_xaxis_transform(),
                        fontsize=18, fontweight='bold',
                        ha='center', va='bottom',
                        color='black',
                        rotation=90,
                        zorder=5,
                        clip_on=False
                    )


        ax.set_ylim(ylim_min, ylim_max)

        legend_elements = [
            Line2D([0], [0], color='gray', linewidth=10, alpha=0.7, label='Network β'),
            Line2D([0], [0], color='w', label=''),
            Line2D([0], [0], color='w', label='FDR significance:'),
            Line2D([0], [0], color='w', label='   * q < 0.05'),
            Line2D([0], [0], color='w', label='   ** q < 0.01'),
            Line2D([0], [0], color='w', label='   *** q < 0.001')
        ]
    else:
        # --- Boxplot Version (rotated) ---
        bp = ax.boxplot(
            [plot_data[plot_data['network'] == net]['estimate'].values for net in networks_present_reversed],
            positions=range(n_networks),
            vert=True,
            widths=0.6,
            patch_artist=True,
            showfliers=False
        )
        for patch, net in zip(bp['boxes'], networks_present_reversed):
            patch.set_facecolor(colors_17N.get(net, '#808080'))
            patch.set_alpha(0.6)
            patch.set_edgecolor('black')

        for i, net in enumerate(networks_present_reversed):
            vals = plot_data[plot_data['network'] == net]['estimate'].values
            x_positions = np.random.normal(i, 0.04, size=len(vals))
            ax.scatter(x_positions, vals, alpha=0.4, s=30, color=colors_17N.get(net, '#808080'), zorder=2)

        legend_elements = [
            Line2D([0], [0], color='gray', linewidth=10, alpha=0.6, label='Node distribution (box)'),
            Line2D([0], [0], marker='o', color='black', label='Network β'),
            Line2D([0], [0], color='w', label='FDR significance: * q < 0.05, ** q < 0.01, *** q < 0.001')
        ]

    # --- BASELINE + LABELS ---
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2.5, alpha=0.8, zorder=4)

    ax.set_xticks(range(n_networks))
    y_labels = []
    for net in networks_present_reversed:
        n_nodes = len(plot_data[plot_data['network'] == net])
#         y_labels.append(f"{net} (N={n_nodes})")
        y_labels.append(f"{net}")

    ax.set_xticklabels(y_labels, fontweight='bold', fontsize=10, rotation=90, ha='center')

    for label, net in zip(ax.get_xticklabels(), networks_present_reversed):
        label.set_color(colors_17N.get(net, '#808080'))

    # --- Draw family grouping bars along x-axis (bottom) ---
    if show_bars and not sort_by_effect:
        base_colors = {
            'Vis': '#38007a', 'SomMot': '#4682b4', 'Limbic': '#dcf8a4', 'TempPar': 'blue',
            'DorsAttn': '#00760e', 'SalVentAttn': '#d600b8', 'Cont': '#e69422', 'Default': '#cd3e4e'
        }
        families = {
            'Vis': ['VisCent', 'VisPeri'],
            'SomMot': ['SomMotA', 'SomMotB'],
            'Limbic': ['LimbicA', 'LimbicB'],
            'TempPar': ['TempPar'],
            'DorsAttn': ['DorsAttnA', 'DorsAttnB'],
            'SalVentAttn': ['SalVentAttnA', 'SalVentAttnB'],
            'Cont': ['ContA', 'ContB', 'ContC'],
            'Default': ['DefaultA', 'DefaultB', 'DefaultC']
        }

        for family, members in families.items():
            present = [net for net in members if net in networks_present_reversed]
            if len(present) > 0:
                x_positions = [networks_present_reversed.index(net) for net in present]
                x_start = min(x_positions) - 0.35
                x_end = max(x_positions) + 0.35
                ax.plot([x_start, x_end], [0, 0],
                        color=base_colors[family],
                        linewidth=8,
                        solid_capstyle='round',
                        transform=ax.get_xaxis_transform(),
                        clip_on=False,
                        zorder=10)

    # --- Labels ---
    ax.set_ylabel('β', fontsize=13, fontweight='bold')
    #ax.set_xlabel('17-Networks', fontsize=12, fontweight='bold')

    ax.grid(axis='y', alpha=0.3, zorder=0)
    ax.set_axisbelow(True)
    
    show_legend = False  # ← set to True if you want to display it

    if show_legend:
        ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9, fontsize=9)


    #ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9, fontsize=9)
    plt.ylim(min_val_manual,max_val_manual)
    plt.tight_layout()
    sanitized_effect = effect.replace(" ", "_").replace("-", "_").replace(".", "_")
    plt.savefig(os.path.join(output_folder, f"network_distribution_17N_vertical_{sanitized_effect}.png"),
                dpi=300, bbox_inches='tight')
    plt.show()

    print(f"✓ Vertical 17N distribution plot saved to {output_folder}")
