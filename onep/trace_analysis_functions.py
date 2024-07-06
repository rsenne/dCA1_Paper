# import libraries
import numpy as np
import scipy
import seaborn as sns
import matplotlib.pyplot as plt

__all__ = ["bci", "tci", "eta_significance", "raster_plot", "plot_whole_eta", 'eta_individual_cells', 'eta_averaged',
           'eta_individual_cells_ci', 'plot_rep_cells']

def plot_rep_cells(data):
    # Plot all cells for desired animal, session
    fig, axs = plt.subplots(40,1, sharex='col', figsize=(10,8))
    for i in range(40):
        axs[i].plot(np.array(data[i,:]), color='black')
        # axs[i].axis('off')
    # plt.plot(np.array(z_traces[19,:]), color='black')
    plt.box(False)
    plt.xticks(visible=False)
    plt.yticks(visible=False)
    plt.grid(False)

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

def plot_whole_eta(data, ci='bci', sig_duration=8, axs=None):
    # Plot entire session - average trace + ci for data provided

    if ci == 'tci':
        c_int = tci(data)
    elif ci == 'bci':
        c_int = bci(data, num_samples=1000)
    else:
        raise ValueError("Confidence interval options are 'tci' or 'bci'")

    # find significant indices
    start_indices = eta_significance(c_int[0, :], sig_duration=8)

    #if axs is not provided
    if axs is None:
        fig, axs = plt.subplots()

    # create figure
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

def eta_individual_cells(data, timestamps, events=None, window=10, ax=None, **kwargs):
    # Event-triggered average for all cells plotted individually for data provided
    # No significance or CI plotted

    # Window in seconds times 30 indices per second and half the window period to visualize before
    number_of_indices = int(window * 1.5 * 10)

    def event_interpolation(data, events_):
        interp = scipy.interpolate.interp1d(timestamps, data, kind='cubic', bounds_error=False, fill_value="extrapolate")
        within_eta_ = np.zeros((len(events_), number_of_indices))
        for i, event in enumerate(events_):
            time_period = np.linspace(event - (window / 2), event + window, number_of_indices)
            time_period = np.clip(time_period, timestamps.min(), timestamps.max())
            within_eta_[i] = interp(time_period)
        return np.average(within_eta_, axis=0)

    across_eta_ = np.zeros((len(data), number_of_indices))

    # If there's only one set of events, repeat it for each curve
    if events is not None and len(events) == 1:
        events = events * len(data)

    for j, curve in enumerate(data):
        if events is not None:
            across_eta_[j] = event_interpolation(curve, events[j])
        else:
            across_eta_[j] = event_interpolation(curve, [timestamps.mean()])  # or handle as needed

    return across_eta_
    # # Make a figure
    # if ax is None:
    #     fig, ax = plt.subplots(len(across_eta_), 1, sharex='col', figsize=(4, 60))
    #
    # time = np.linspace(-window / 2, window, number_of_indices)

    # for i in range(len(data)):
    #     ax[i].plot(time, np.array(across_eta_[i, :]))
    #     ax[i].grid(False)
    #     ax[i].spines['top'].set_visible(False)
    #     ax[i].spines['right'].set_visible(False)
    #     ax[i].axvline(0, linestyle='--', color='black')
    #     ax[i].set_ylabel(r'$\frac{dF}{F}$ (%)')
    # plt.subplots_adjust(wspace=0.05)
    # plt.xlabel('Time(s)')
    #
    # if ax is None:
    #     return fig, ax, across_eta_, time
    # else:
    #     return ax, across_eta_, time


# Example usage:
# ax, across_eta_, time = eta_individual_cells(data=concat_a, timestamps=timestamps_a, events=[[120,180,240,300],], window=10)

def eta_averaged(data, timestamps, events=None, window=10, ci='bci', sig_duration=8, ax=None, **kwargs):
    # Event-triggered average for all cells plotted together for data provided
    # window in seconds times 30 indices per second and half the window period to visualize before
    number_of_indices = int(window * 1.5 * 10)

    def event_interpolation(data, events_):
        interp = scipy.interpolate.interp1d(timestamps, data, kind='cubic')
        within_eta_ = np.zeros((len(events_), number_of_indices))
        for i, event in enumerate(events_):
            time_period = np.linspace(event - (window / 2), event + window, number_of_indices)
            within_eta_[i] = interp(time_period)
        return np.average(within_eta_, axis=0)

    across_eta_ = np.zeros((len(data), number_of_indices))

    # If there's only one event, repeat it for each curve
    if len(events) == 1:
        events = events * len(data)

    for j, curve in enumerate(data):
        across_eta_[j] = event_interpolation(curve, events[j])

    average_trace = np.average(across_eta_, axis=0)

    # choose t-confidence interval or bootstrapped
    if ci == 'tci':
        c_int = tci(across_eta_)
    elif ci == 'bci':
        c_int = bci(across_eta_, num_samples=1000)
    else:
        raise ValueError("Confidence interval options are 'tci' or 'bci'")

    # find significant indices
    start_indices = eta_significance(c_int[0, :], sig_duration=10)  # change to be dependent on the sampling rate

    # make a figure
    if ax is None:
        fig, ax = plt.subplots()
    time = np.linspace(-window / 2, window, number_of_indices)
    ax.plot(time, average_trace, **kwargs)
    ax.fill_between(time, c_int[0, :], c_int[1, :], alpha=0.3)

    # plot the significant deflections
    y_height = ax.get_ylim()[1] * 0.97
    for start_index in start_indices:
        end_index = start_index + sig_duration
        ax.hlines(y=y_height, xmin=time[start_index], xmax=time[end_index], colors='r')

    if ax is None:
        return fig, ax, across_eta_, time
    else:
        return ax, across_eta_, time

def eta_individual_cells_ci(data, timestamps, events=None, window=10, ci='tci', sig_duration=8, ax=None, **kwargs):
    # Event-triggered average for all cells plotted individually for data provided
    # With CI for each small cell's plot

    # window in seconds times 30 indices per second and half the window period to visualize before
    number_of_indices = int(window * 1.5 * 15)

    interp = scipy.interpolate.interp1d(timestamps, data, kind='cubic')
    within_eta_ = np.zeros((len(events), number_of_indices))
    for i, event_ in enumerate(events):
        time_period = np.linspace(event_ - (window / 14), event_ + window, number_of_indices)
        within_eta_[i] = interp(time_period)

    across_eta_ = np.average(within_eta_, axis=0)

    # choose t-confidence interval or bootstrapped
    if ci == 'tci':
        c_int = tci(within_eta_)
    elif ci == 'bci':
        c_int = bci(within_eta_, num_samples=1000)
    else:
        raise ValueError("Confidence interval options are 'tci' or 'bci'")

    time = np.linspace(-window / 14, window, number_of_indices)

    # make a figure
    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(time, across_eta_, **kwargs)
    ax.fill_between(time, c_int[0, :], c_int[1, :], alpha=0.3)

    # find significant indices
    start_indices = eta_significance(c_int[0, :], sig_duration) # change to be dependent on the sampling rate

    if len(start_indices) != 0:
        sig = True
    else:
        sig = False

    # plot the significant deflections
    y_height = ax.get_ylim()[1] * 0.97
    for start_index in start_indices:
        end_index = start_index + sig_duration
        ax.hlines(y=y_height, xmin=time[start_index], xmax=time[end_index], colors='r')

    return ax, across_eta_, sig, time

