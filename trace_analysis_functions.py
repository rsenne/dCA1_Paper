def bci(data, num_samples, cl=0.95):
    """
    Calculate the confidence interval for each time point in the data using bootstrap method.

    data: 2D numpy array, rows represent samples and columns represent time points.
    num_samples: Number of bootstrap samples.
    cl: Confidence level.

    Returns a 2D numpy array containing the lower and upper bound of the confidence interval for each timepoint.
    """
    n, t = data.shape
    ci = np.zeros((2, t))
    rng = np.random.default_rng()

    bootstrap_array = np.zeros(shape=(num_samples, t))

    for i in range(t):
        # Generate bootstrap samples for the current time point
        rints = rng.integers(0, n, num_samples)
        bootstrap_array[:, i] = data[rints, i]

        sig = 1 - cl
        ci[0, :] = np.percentile(bootstrap_array, q=(sig / 2) * 100, axis=0)
        ci[1, :] = np.percentile(bootstrap_array, q=(1 - (sig / 2)) * 100, axis=0)
    return ci

def tci(array, cl=0.95):
    """_summary_

    Args:
        array (_type_): _description_
        cl (float, optional): _description_. Defaults to 0.95.

    Returns:
        _type_: _description_
        """
    n = array.shape[0]
    crit_t = scipy.stats.t.ppf(cl, df=n - 1)
    c_int = np.zeros(shape=(2, array.shape[1]))
    c_int[0, :] = np.mean(array, axis=0) - (crit_t * scipy.stats.sem(array, axis=0))
    c_int[1, :] = np.mean(array, axis=0) + (crit_t * scipy.stats.sem(array, axis=0))
    return c_int


def eta_significance(ci, sig_duration):

        # find deflections from baseline
        deflections = ci > 0

        # create a sliding window for convolution
        window = np.ones(sig_duration)

        # convolve with boolean array
        true_deflects = np.convolve(deflections, window, 'valid')

        # find start indices where convolution equals to significant_duration
        start_indices = np.where(true_deflects == sig_duration)[0]
        return start_indices


def plot_whole_eta(data, ci='bci', sig_duration=8):

    #choose confidence interval type
    if ci == 'tci':
        c_int = tci(data)
    elif ci == 'bci':
        c_int = bci(data, num_samples=1000)
    else:
        raise ValueError("Confidence interval options are 'tci' or 'bci'")

    # find significant indices
    start_indices = eta_significance(c_int[0, :], sig_duration=8)

    # create figure
    fig, axs = plt.subplots()
    axs.plot(data.mean(axis=0))
    axs.fill_between(range(c_int.shape[1]), c_int[0, :], c_int[1, :], alpha=0.3)
    axs.set_xlabel('Time (seconds)')
    axs.set_ylabel(r'$\frac{dF}{F}$ (%)')
    axs.grid(False)
    axs.spines['top'].set_visible(False)
    axs.spines['right'].set_visible(False)
    # plot the significant deflections
    y_height = axs.get_ylim()[1] * 0.97
    for start_index in start_indices:
        end_index = start_index + sig_duration
        axs.hlines(y=y_height, xmin=start_index, xmax=end_index, colors='r')
    return axs

def raster_plot(raster_array, xtick_range=None, xtick_freq=None):
    """Raster plot: Generate a raster plot of Z-scored fiber photometry traces.
    Args: task (str): String that represents the task e.g. FC, Recall, Ext etc.Should be identical to what was
    passed in fiberPhotometryCurve.
    treatment (str): String that represents the treatment e.g. eYFP, ChR2, Shock etc. Should be identical to what
    was passed in fiberPhotometryCurve.
    region (str): String to grab region trace of choice e.g. Region0G, Region1R, etc.
    xtick_range (int, optional): Length in time of session. Defaults to None.
    xtick_freq (int, optional): How many labels in [0, xtick_range]; end points inclusive. Defaults to None.
    Returns: matplotlib figure: a matplotlib figure object matplotlib axis: a matplotlib axis object
    """
    fig, ax = plt.subplots()
    sns.heatmap(raster_array, cbar=True, cbar_kws={"label": r"$\frac{dF}{F}$"}, center=0, yticklabels=False, ax=ax, cmap='icefire')
    ax.set_xlabel('Time (s)')
    if xtick_range and xtick_freq is not None:
        ax.set_xticks(np.linspace(0, raster_array.shape[1], xtick_freq),
                          labels=np.linspace(0, xtick_range, xtick_freq))
    return fig, ax
#%%
#Plot FC raster
#raster_plot(concat_cxta, xtick_range=360, xtick_freq=13)