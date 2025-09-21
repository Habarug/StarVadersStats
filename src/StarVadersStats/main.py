import os

import matplotlib.pyplot as plt
import pandas as pd
from thefuzz.process import extractOne

from . import _load


class SVStats:
    def __init__(self, rundir=None):
        if not rundir:
            if not os.path.exists("data"):
                os.mkdir("data")

            dirs = [
                dir
                for dir in os.listdir("data")
                if os.path.isdir(os.path.join("data", dir))
            ]
            if len(dirs):
                self.rundir = os.path.join("data", dirs[0])
            else:
                raise ValueError(
                    "No runs found in data folder. Please add 'history' folder, or supply a path"
                )

        else:
            self.rundir = rundir

        self._load = _load.Load(self.rundir)
        self.df_runs = self._load.get_df_runs()
        self._df_cards = self._load.get_df_cards()
        self._df_artifacts = self._load.get_df_artifacts()

    ##############
    # region PLOTS
    ##############

    def plot_runSuccess(self, pilot=None):
        fig, ax = plt.subplots()

        if not pilot:
            df = self.df_runs
        else:
            pilot = extractOne(pilot, self._load.pilotDict)[0]
            df = self.df_runs[self.df_runs["Pilot"] == pilot]

        sct = ax.scatter(df.index, df["Difficulty"], c=df["Success"], marker="o")
        cbar = plt.colorbar(sct, ax=ax)
        cbar.set_ticks([0, 1, 2, 3])
        cbar.set_ticklabels(["Failure", "False victory", "Act 4 death", "True victory"])

        ax.set_yticks(df["Difficulty"].unique())
        ax.set_yticklabels(
            [
                self._load.difficultyDict[int(i.get_position()[1])]
                if (int(i.get_position()[1]) in self._load.difficultyDict)
                else None
                for i in ax.get_yticklabels()
            ]
        )

        ax.grid()
        ax.set_ylabel("Difficulty")
        ax.set_xlabel("Run")

        fig.set_size_inches(6, 3)

        return fig, ax

    #################################
    # region PROPERTIES AND SHORTCUTS
    #################################

    @property
    def carddb(self):
        return self._load.carddb

    @property
    def artifactdb(self):
        return self._load.artifactdb

    @property
    def df_cards(self):
        return self._df_cards[
            self.carddb[
                (self.carddb["Rarity"] != "Starter")
                & (self.carddb["Rarity"] != "Created")
                & (self.carddb["Rarity"] != "Junk")
            ]["Card"]
        ]

    @property
    def df_artifacts(self):
        return self._df_artifacts[
            self.artifactdb[
                (self.artifactdb["Rarity"] != "Starter")
                & (self.artifactdb["Rarity"] != "N/A")
            ]["Artifact"]
        ]

    @property
    def pilots(self):
        """Returns pilots in correct order, but only includes the ones you have actually used."""
        return [
            pilot
            for pilot in self._load.pilotDict.values()
            if pilot in self.df_runs["Pilot"].unique()
        ]

    @property
    def df_victories(self):
        return self.df_runs[self.df_runs["Success"] > 0]

    @property
    def df_truevictories(self):
        return self.df_runs[self.df_runs["Success"] == 3]
