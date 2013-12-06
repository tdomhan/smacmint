Smacmint
========

Smacmint is a [SMAC](http://www.cs.ubc.ca/labs/beta/Projects/SMAC/) wrapper for [spearmint](https://github.com/JasperSnoek/spearmint). 


Usage
-----

For running smacmint, just provide a spearmint configuration file:
```
python smacmint.py braninpy/config.pb
```

By default your function will be evaluated 10000 times, to find a good set of parameters. (See sections Command line parameters, if you want to change this.)

For details on how the config file needs to look like see the [spearmint documentation](https://github.com/JasperSnoek/spearmint).

While SMAC is running, you can see the current performance of your algorithm after "Performance of the Incumbent". Once SMAC is finished you can find the best parameters after "Complete Configuration". Also check out the trajectory file: braninpy/scenario-SMAC-...${DATE}/traj-run-${SEED}.csv

Parameter print format
----------------------

The format for the parameters, when printed and also in the csv file containing the trajectories is the following:
PARAMNAME@ARRAY_INDEX

Or in words: the parameters will appear as the parameter name + the index separated by an @.


Command line parameters
-----------------------

To check out the parameters:
```
python smacmint.py -h
```

The most important is probably `max-finished-jobs`, which specifies how often the script will be executed, e.g. 
```
python smacmint.py --max-finished-jobs 10 braninpy/config.pb
```


