### Information-theoretic Analysis of tracking data
This script takes tracking data as input and computes feedback, feedforward and total information from recorded behaviour, in accordance with Lam & Zénon, 2021. 

Input data are csv files "[filename].csv", with the samples in rows and the variables in columns. 

By default, the script takes 30 trials and 3 variables: 1 output and 2 intputs. 

Output data are also csv files, names "output_[filename].csv", with one column per output variable and one row per trial. These files will be saved in an output/ directory within the working directory (needs to be created beforehand).

A figure of the average results is plotted at the end. 

To run the code in terminal :
```
python ITscript.py
```
if all your data files are in "data/". 
Otherwise:
```
python ITscript.py -p "yourdir/"
```
to provide a directory "yourdir" within which all files will be read and analysed. 
You can also use
```
python ITscript.py -f "exampleData.csv"
```
to provide a single filename. 
To change the number of trials and/or samples and/or number of variables, you can use these options:
```
python ITscript.py -tr 40 -sa 500 -in 2
```
Finally,
```
python ITscript.py -pl True
```
will also plot a figure of the results of each file. The figure window has to be closed for the code to continue running.

A. Zénon, August 2023