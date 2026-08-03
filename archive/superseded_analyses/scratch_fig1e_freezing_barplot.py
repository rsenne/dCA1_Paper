def plot_freezing(df):
    colors = ["#66C1A6", "#FC8C62"]
    sns.set_style("ticks")
    fig,ax = plt.subplots(figsize=(4,3))
    sns.set_palette(sns.color_palette(colors))

    sns.barplot(x='Session', y='Freezing', hue='Group', data=df, ci=68,
    capsize=.2, errwidth=1,  alpha=0.8)

    def width_changer(ax, new_val):
        for patch in ax.patches :
            cur_width = patch.get_width()
            diff = cur_width - new_val
            patch.set_width(new_val)
            patch.set_x(patch.get_x() + diff * .5)

    width_changer(ax, .4)

    sns.stripplot(x='Session', y='Freezing', hue='Group', data=df,
              size=4, linewidth=0.3, edgecolor='black', dodge=True, jitter=False)

    # remove extra legend handles
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], title='Group', loc='upper right')
    ax.set_xlabel("")
    ax.set_ylabel("Freezing %")
    ax.set_ylim(0,70)
    sns.despine()
    plt.savefig('/Users/suthardr/Desktop/dCA1_Analysis/All_freezing_average.svg')
    plt.show()
    return fig, ax

def plot_freezing_across_time(df):
    # font = {'family' : 'Arial',
    #     'weight' : 'bold',
    #     'size'   : 10}
    # mpl.rc('font',**font)
    colors = ["#66C1A6", "#FC8C62"]
    sns.set_style("ticks")

    fig,ax = plt.subplots(figsize=(4,3))
    sns.set_palette(sns.color_palette(colors))

    sns.pointplot(x='bin', y='Freezing', hue='Group', data=df, errorbar='se')
    sns.stripplot(x='bin', y='Freezing', hue='Group', data=df, jitter=False, size=4, linewidth=0.3, edgecolor='black')

    # remove extra legend handles
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[:2], labels[:2], title='Group', loc='upper left')
    plt.xticks(rotation=45)
    ax.set_xlabel("Time(s)")
    ax.set_ylabel("Freezing %")
    ax.set_ylim(0,80)
    sns.despine()
    plt.savefig('/Users/suthardr/Desktop/dCA1_Analysis/All_freezing_day5_acrosstime.svg')
    plt.show()
    return fig, ax