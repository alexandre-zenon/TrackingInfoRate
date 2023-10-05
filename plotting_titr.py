import argparse
import os
import re
from dataclasses import dataclass
import scipy

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import glob
import numpy as np

import warnings

warnings.filterwarnings("ignore")


@dataclass
class Config81Y:
    n_trials: int = 35
    trials_to_plot: tuple = (6, 35)
    norm_trials = np.arange(6, 9)
    v_lines: tuple = (5.5, 8.5, 26.5)
    train_trials = np.arange(9, 27).tolist()
    post_trials = np.arange(27, 36).tolist()
    output_folder: str = 'figures_81Y'
    condition: tuple = ('Uncertainty', ['Low', 'Med', 'High'])


@dataclass
class Config83Y:
    n_trials: int = 36
    trials_to_plot: tuple = (1, 36)
    norm_trials = np.arange(4)
    v_lines: tuple = (4.5, 28.5)
    train_trials = np.arange(5, 29).tolist()
    post_trials = np.arange(29, 37).tolist()
    output_folder: str = 'figures_83Y'
    condition: tuple = ('Stimulation', ['20Hz', '80Hz', 'Sham'])


@dataclass
class Config81Y_titr():
    n_trials: int = 36
    trials_to_plot: tuple = (1, 36)
    norm_trials = np.arange(4)
    v_lines: tuple = (4.5, 28.5)
    train_trials = np.arange(5, 29).tolist()
    post_trials = np.arange(29, 37).tolist()
    output_folder: str = 'figures_81Y_titr'
    condition: tuple = ('Stimulation', ['20Hz', '80Hz', 'Sham'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--folder", type=str, default='./')
    parser.add_argument("-n", "--name", type=str, default="figure.png")
    parser.add_argument("-p", "--plot", type=str, default="line_plot")
    parser.add_argument('-norm', '--normalization', type=bool, default=False)
    args = parser.parse_args()

    if args.folder[-3:] == '81Y':
        config = Config81Y()
    elif args.folder[-3:] == '83Y':
        config = Config83Y()
    else:
        config = Config81Y_titr()

    files = glob.glob(f"{args.folder}/o*.csv")
    df = pd.DataFrame()
    for csv in files:
        file_name = re.split('/', string=csv)[-1]
        block = int(file_name[-5:-4])

        if len(file_name) == 22:
            participant = int(file_name[10:11])
        else:
            participant = int(file_name[10:12])

        # Wrap condition
        condition = scipy.io.loadmat(
            f"{args.folder}/{file_name[:-4]}_conditions.mat")[
            'noise_reinf_type_alltrials']

        tmp_df = pd.read_csv(csv)
        tmp_df['Participant'] = participant
        tmp_df['Block'] = block
        try:
            tmp_df['Reinforcement'] = condition[:, 1].tolist()
        except:
            breakpoint()
        tmp_df['Reinforcement'][tmp_df['Reinforcement'] == 0] = 'OFF'
        tmp_df['Reinforcement'][tmp_df['Reinforcement'] == 1] = 'ON'

        tmp_df['Uncertainty'] = condition[:, 0].tolist()
        tmp_df['Uncertainty'][tmp_df['Uncertainty'] == 0] = '0 %'
        tmp_df['Uncertainty'][tmp_df['Uncertainty'] == 1] = '10 %'
        tmp_df['Uncertainty'][tmp_df['Uncertainty'] == 2] = '20 %'
        tmp_df['Uncertainty'][tmp_df['Uncertainty'] == 3] = '40 %'
        tmp_df['Uncertainty'][tmp_df['Uncertainty'] == 4] = '60 %'
        tmp_df['Uncertainty'][tmp_df['Uncertainty'] == 5] = '80 %'

        # tmp_df['NormTargetFeedback'] = (tmp_df['TargetFeedback'] /
        #                                 tmp_df['TargetFeedback'].iloc[
        #                                     config.norm_trials].mean() * 100)
        # tmp_df['NormTargetFeedforward'] = (tmp_df['TargetFeedforward'] /
        #                                    tmp_df['TargetFeedforward'].iloc[
        #                                        config.norm_trials].mean() * 100)
        # tmp_df['NormTargetTotalInfo'] = (tmp_df['TargetTotalInfo'] /
        #                                  tmp_df['TargetTotalInfo'].iloc[
        #                                      config.norm_trials].mean() * 100)

        df = pd.concat((df, tmp_df))

    if args.plot == 'line_plot':
        uncertainty_plot(df, name=args.name, config=config,
                         normalization=args.normalization)
    elif args.plot == 'pre_post':
        pre_post(df, name=args.name, config=config)
    return


def pre_post(df, config, name):
    df_pre = df[(df['TrialNumber']).isin([1, 2, 3])]
    df_post = df[(df['TrialNumber']).isin([40, 41, 42])]

    # Train
    # breakpoint()
    df_pre = df_pre[['TargetFeedback', 'TargetFeedforward',
                     'TargetTotalInfo',
                     'Participant']].groupby(['Participant']).mean()
    df_pre = df_pre.reset_index()
    df_pre['Trials'] = 'Pre'
    df_post = df_post[['TargetFeedback', 'TargetFeedforward',
                       'TargetTotalInfo',
                       'Participant']].groupby('Participant').mean()
    df_post = df_post.reset_index()
    df_post['Trials'] = 'Post'

    df = pd.concat([df_pre, df_post])

    with plt.style.context('seaborn-v0_8-paper'):
        sns.set_context('talk')
        fig, ax = plt.subplots(1, 3, figsize=(12, 12))

        sns.boxplot(df,
                    y="TargetFeedback", x="Trials",
                    ax=ax[0])
        sns.boxplot(df,
                    y="TargetFeedforward", x="Trials",
                    ax=ax[1])
        sns.boxplot(df,
                    y="TargetTotalInfo", x="Trials",
                    ax=ax[2])
        # ax[0, 0].set_title('Training')
        plt.savefig(f"./{config.output_folder}/boxplot/{name}")


def uncertainty_plot(df, config, name):
    df = df[(df['TrialNumber']).isin(np.arange(4, 39).tolist())]

    # Train
    df_pre = df[['TargetFeedback', 'TargetFeedforward',
                 'TargetTotalInfo',
                 'Participant', 'Uncertainty']].groupby(['Participant']).mean()
    df_pre = df_pre.reset_index()
    # breakpoint()



    with plt.style.context('seaborn-v0_8-paper'):
        sns.set_context('talk')
        fig, ax = plt.subplots(1, 3, figsize=(12, 12))

        sns.boxplot(df,
                    y="TargetFeedback", x="Trials",
                    ax=ax[0])
        sns.boxplot(df,
                    y="TargetFeedforward", x="Trials",
                    ax=ax[1])
        sns.boxplot(df,
                    y="TargetTotalInfo", x="Trials",
                    ax=ax[2])
        # ax[0, 0].set_title('Training')
        plt.savefig(f"./{config.output_folder}/boxplot/{name}")
        return


if __name__ == '__main__':
    main()
