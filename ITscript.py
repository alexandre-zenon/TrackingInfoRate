# Import classes
import matplotlib.pyplot as plt
import information_transfer as it
import numpy as np
import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", type=str, default='')
parser.add_argument("-p", "--path", type=str, default='data/')
parser.add_argument("-pl", "--plot", type=bool, default=False)
parser.add_argument("-tr", "--trials", type=int, default=30)
parser.add_argument("-sa", "--samples", type=int, default=418)
parser.add_argument("-in", "--inputs", type=int, default=3)
parser.add_argument("-to", "--targetorder", type=int, default=4)
parser.add_argument("-colo", "--colourorder", type=int, default=0)
parser.add_argument("-curso", "--cursororder", type=int, default=3)
args = parser.parse_args()

# functions for dealing with nans
def nan_helper(y):
    return np.isnan(y), lambda z: z.nonzero()[0]

def interpolate_nans(y):
    nans, x = nan_helper(y)
    y[nans] = np.interp(x(nans), x(~nans), y[~nans])
    return y

# load data
def load_data(path,filename):
    csv = np.genfromtxt (path+filename, delimiter=",")
    if (args.inputs==3):
        cursor = csv[1:args.samples,0:args.trials]
        colour = csv[1:args.samples,args.trials:args.trials*2]
        target = csv[1:args.samples,args.trials*2:args.trials*3]
    if (args.inputs==2):
        cursor = csv[1:args.samples, 0:args.trials]
        target = csv[1:args.samples, args.trials:args.trials * 2]
        colour = target*np.nan

    # remove nans
    allTrials = list(range(args.trials))
    nanTrials = np.where(np.all(np.isnan(cursor), axis=0))#trials with only nans
    cursor = np.delete(cursor,nanTrials,1)
    colour = np.delete(colour,nanTrials,1)
    target = np.delete(target,nanTrials,1)
    for tr in nanTrials[0]:
        allTrials.pop(tr)
    for idx, tr in enumerate(cursor.T):
        tr = interpolate_nans(tr)
        cursor[:,idx] = tr
    return cursor, colour, target, allTrials

# compute FB, FF and total info
def compute_info_transfer(path=None,filename=None):
    if filename is None:
        if (args.path):
            df = pd.DataFrame()
            directory = os.fsencode(args.path)
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.endswith(".csv"):
                    df = pd.concat((df,compute_info_transfer(args.path,filename)))
            dfmean = df.groupby(level=0).mean()
            # plotting average
            if True:
                t = dfmean.TrialNumber  # adding 6 to trial number because of the 6 training trials
                fig = plt.figure()
                plt.subplot(1, 2, 1)
                plt.plot(t, dfmean.TargetFeedback, 'b', t, dfmean.ColourFeedback, 'g', t, dfmean.BothFeedback, 'r')
                plt.title("Average result: Feedback info")
                plt.xlabel("Trial number")
                plt.ylabel("FB")
                plt.legend(['Target','Colour','Both'])
                plt.subplot(1, 2, 2)
                plt.plot(t, dfmean.TargetFeedforward, 'b', t, dfmean.ColourFeedforward, 'g', t, dfmean.BothFeedforward, 'r')
                plt.title("Average result: Feedforward info")
                plt.xlabel("Trial number")
                plt.ylabel("FF")
                plt.legend(['Target', 'Colour', 'Both'])
                plt.show()

    else:
        cursor, colour, target, allTrials = load_data(path,filename)
        # only target
        targetFB = []
        targetINFO = []
        order = [args.targetorder, args.cursororder]
        for col in range(cursor.shape[1]):
            targetFB.append(it.compute_FB([target[:,col]],cursor[:,col],order,VMD))
            targetINFO.append(it.compute_total_info([target[:, col]], cursor[:, col], order, VMD))
        targetFF = np.array(targetINFO)-np.array(targetFB)
            #only colour
        if (~np.isnan(colour).all()):
            colourFB = []
            colourINFO = []
            order = [args.colourorder, args.cursororder]
            for col in range(colour.shape[1]):
                colourFB.append(it.compute_FB([colour[:,col]],cursor[:,col],order,VMD))
                colourINFO.append(it.compute_total_info([colour[:, col]], cursor[:, col], order, VMD))
            colourFF = np.array(colourINFO)-np.array(colourFB)
                #both cursor and colour
            bothFB = []
            bothINFO = []
            order = [args.targetorder, args.colourorder, args.cursororder]
            for col in range(cursor.shape[1]):
                bothFB.append(it.compute_FB([target[:,col],colour[:,col]],cursor[:,col],order,VMD))
                bothINFO.append(it.compute_total_info([target[:,col],colour[:, col]], cursor[:, col], order, VMD))
            bothFF = np.array(bothINFO)-np.array(bothFB)

            # saving
            zipped = list(zip(allTrials, targetFB, targetFF, targetINFO, colourFB, colourFF, colourINFO, bothFB, bothFF, bothINFO))
            df = pd.DataFrame(zipped, columns=['TrialNumber','TargetFeedback', 'TargetFeedforward', 'TargetTotalInfo',
                                               'ColourFeedback', 'ColourFeedforward', 'ColourTotalInfo',
                                               'BothFeedback', 'BothFeedforward', 'BothTotalInfo'])
            df.to_csv('output/' + 'output_' + filename, index=False)

            #plotting
            if args.plot:
                t = np.array(allTrials)+6 # adding 6 to trial number because of the 6 training trials
                fig = plt.figure()
                plt.subplot(1, 2, 1)
                plt.plot(t,targetFB,'b',t,colourFB,'g',t,bothFB,'r')
                plt.title("Feedback info")
                plt.xlabel("Trial number")
                plt.ylabel("FB")
                plt.subplot(1, 2, 2)
                plt.plot(t,targetFF,'b',t,colourFF,'g',t,bothFF,'r')
                plt.title("Feedforward info")
                plt.xlabel("Trial number")
                plt.ylabel("FF")
                plt.show()
        else:
            # saving
            zipped = list(zip(allTrials, targetFB, targetFF, targetINFO))
            df = pd.DataFrame(zipped, columns=['TrialNumber', 'TargetFeedback', 'TargetFeedforward', 'TargetTotalInfo'])
            df.to_csv('output/' + 'output_' + filename, index=False)

            # plotting
            if args.plot:
                t = np.array(allTrials)  # adding 6 to trial number because of the 6 training trials
                fig = plt.figure()
                plt.subplot(1, 2, 1)
                plt.plot(t, targetFB, 'b')
                plt.title("Feedback info")
                plt.xlabel("Trial number")
                plt.ylabel("FB")
                plt.subplot(1, 2, 2)
                plt.plot(t, targetFF, 'b')
                plt.title("Feedforward info")
                plt.xlabel("Trial number")
                plt.ylabel("FF")
                plt.show()

        return df

VMD=15
if args.filename:
    compute_info_transfer(args.path,args.filename)
else:
    compute_info_transfer()