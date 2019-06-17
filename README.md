# GR Tensorboard - a collection of plugins for tensorboard

<!-- This document was last reviewed on Nov 1, 2018. It should be
reviewed occasionally to make sure it stays up-to-date. -->

How to build and run
====================
I have provided a script build_and_run_pip_package.sh which should be run in the directory above this with a virtual environment activated. It assumes that the directory with all the gr tensorboard code is called *gr_tensorboard* (clearly because I like to make things more difficult). This script will run bazel to build all the assets and then build the pip wheel, exporting the assets and then installing the wheel to your virtual environment. It will finally call grtensorboard with some default command line arguments. 

Bazel versions
==============
I had found difficulty in determining a suitable version of bazel with which to build grtensorboard and have settled with bazel 0.21.0 (obtained through binary search between broken versions). Bazel build command used is located in build_pip_package.sh and is ```bazel build --incompatible_remove_native_http_archive=false --incompatible_package_name_is_a_function=false :gr_tensorboard```. You may find a more up to date version of bazel to build tensorboard. If so then do feel free to use the up to date version.

What plugins already exist 
==========================
Currently, I have developed (and am continuing to develop) two plugins:
1. Runsenabler - a tool to select which runs are exposed to tensorboard during runtime
2. Paramplot - a tool to plot metrics against parameter configurations for each run

RunsEnabler
===========
![RunsEnabler Dashboard](/images/runsenabler.png)

## Overview
There are two columns, each with a regex for search / filtering: 

### Left column
1. The regex at the top is called the *group regex* and groups the runs by regex match
2. Left column displays regex matches of runs (which match the left regex called the *group regex*), each group being togglable by a checkbox
   * Toggling the checkbox for a run group will enable or disable all the runs in that particular group (these are the runs which match *group regex* with the matching substring being the group key)
3. There are buttons to enable and disable *all* run groups (and hence all runs which match the *group regex*)
4. There is a checkbox below the regex text input which if enabled will enable newly created runs iff the new runs match the regex (useful so that tensorboard can automatically pick up and enable newly created runs)

### Right column
1. The regex at the top will filter the runs displayed whose corresponding run groups in the left column have been enabled
2. runs which *do not* match the regex will still maintain their current state (either ENABLED or DISABLED) 
3. Enable and disable all runs buttons exist to respectively enable or disable all the visible runs 
4. Checkboxes next to each run allow the user to enable or disable each run individually

### Reloading
Refreshing the Runsenabler (by clicking the *reload* icon in the tensorboard dashboard while viewing the runsenabler tab) will cause any runs which are enabled in the frontend to load data into *EventAccumulators* in the backend. Therefore, the *EventMultiplexer* which controls all the *EventAccumulators* will only consist of accumulators which are enabled in the frontend.

By default, no runs will be enabled so you will have to select them in the runsenabler and you can provide a regex to initialise the runeenabler to save typing that out.

ParamPlot
=========
![ParamPlot Dashboard](/images/paramplot.png)

## Overview
The dashboard consists of categories of plots which are filtered by regexes and a side bar which selects the aggregation method for the data returned for each metric (which may have multiple values per run)

### Plot categories
1. An *ADD CATEGORY* button for creating a new set of plots as well as a corresponding *DELETE CATEGORY* button
2. Each category has two regexes, one to filter the metrics (or *tags* in tensorboard parlance) which are plotted on the vertical axes of the plots, and the other to filter the parameter names which are plotted on the horizontal axes. 
3. Each chart has several modes: 
   * Plotting by **parameter name** - One series per parameter value (parameter name specified in the drop down menu) with each value representing the average metric value for that paremeter and x-axis value
   * Plotting by **All** - Plot one series for the entire chart - metric value is the average over all the metric values for that particular x-axis value
   * Plotting by **None** - Plot a series for each parameter combination (representing keeping all parameters constant apart from the x-axis parameter)
   * Chart functionality is like that of the *Scalars* plugin

### Metric Aggregation method
Per *tag*, there is a drop down specifying the aggregation method for the data to be plotted. This is applied universally for each metric being viewed in the paramplot dashboard

### Data
Paramplot denotes a valid run by a run directory which:
1. Contains a valid set of events files which contain scalar data (readable by the Scalars plugin)
2. Contains exactly one ```runparams.json``` file which is a dictionary mapping from *parameter_name* to *parameter_value*. For now only numerical values have been supported. Some investigation might be required to assess using other parameter values e.g. string values such as to specify the optimisation method used or learning rate schedule to name a few. 
