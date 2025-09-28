import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate
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

    def plot_finalRoom(self, pilot=None):
        if not pilot:
            df = self.df_runs
        else:
            pilot = extractOne(pilot, self._load.pilotDict)[0]
            df = self.df_runs[self.df_runs["Pilot"] == pilot]

        fig, ax = plt.subplots()

        cmap = plt.get_cmap("Set2_r", lut=max(self._load.difficultyDict) + 1)
        cbar = plt.colorbar(
            mpl.cm.ScalarMappable(norm="linear", cmap=cmap),
            ax=ax,
        )

        diffs = ["Other"] + [
            diff for key, diff in self._load.difficultyDict.items() if key > 0
        ]
        cbar.set_ticks([1 / len(diffs) * (i + 0.5) for i in range(len(diffs))])
        cbar.set_ticklabels(diffs)

        rooms = []
        idxs = [0]
        df_deaths = df[(df["Success"] == 2) | (df["Success"] == 0)]

        for act in np.sort(self.df_runs["FinalRoom"].round().unique()):
            rMax = self.df_runs[
                (self.df_runs["FinalRoom"] > act)
                & (self.df_runs["FinalRoom"] < act + 1)
            ]["FinalRoom"].max()

            roomsAct = act + 0.1 + np.arange(round((rMax - act) * 10)) * 0.1
            rooms.extend(roomsAct)

            for room in roomsAct:
                df_room = df_deaths[df_deaths["FinalRoom"] == room]

                bottom = 0
                for diff in np.sort(df_room["Difficulty"].unique()):
                    n_diff = sum(df_room["Difficulty"] == diff)
                    ax.bar(
                        idxs[-1],
                        n_diff,
                        bottom=bottom,
                        color=cmap(max(0, diff)),
                        edgecolor="black",
                    )
                    bottom += n_diff
                idxs.append(idxs[-1] + 1)
            rooms.append(None)
            idxs.append(idxs[-1] + 1)

        ax.set_xticks(range(len(rooms)))
        ax.set_xticklabels([f"{room:.1f}" if room else None for room in rooms])
        ax.set_ylabel("Number of deaths")
        ax.set_xlabel("Act.Day")
        ax.grid(axis="y")
        ax.set_axisbelow(True)
        ax.set_xlim([ax.get_xticks()[0] - 0.5, ax.get_xticks()[-1] - 0.5])
        fig.set_size_inches(9, 3)

        return fig, ax

    ###############
    # region PRINTS
    ###############

    def print_pilot_table(self):
        table = []
        headers = [
            "Pilot",
            "Runs",
            "Victories",
            "True victories",
            "Max difficulty (true)",
            "Favorite card",
            "Favorite artifact",
        ]
        for pilot in self.pilots:
            df_pilot = self.df_runs[self.df_runs["Pilot"] == pilot]
            n = len(df_pilot)
            n_wins = len(df_pilot[df_pilot["Success"] >= 1])
            n_truewins = len(df_pilot[df_pilot["Success"] == 3])

            row = [pilot]
            row.append(n)
            row.append(f"{n_wins} ({n_wins / n * 100:.0f}%)")
            row.append(f"{n_truewins} ({n_truewins / n * 100:.0f}%)")

            row.append(
                self._load.difficultyDict[
                    df_pilot[df_pilot["Success"] == 3]["Difficulty"].max()
                ]
            )

            cards = self.df_cards[self.df_runs["Pilot"] == pilot].sum()
            row.append(
                f"{cards.idxmax()} ({cards.max()}, {cards.max() / n * 100:.0f}%)"
            )

            artifacts = self.df_artifacts[self.df_runs["Pilot"] == pilot].sum()
            row.append(
                f"{artifacts.idxmax()} ({artifacts.max()}, {artifacts.max() / n * 100:.0f}%)"
            )
            table.append(row)

        print(tabulate(table, headers=headers))

    ###################
    # region PROPERTIES
    ###################

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


def quickplot():
    svs = SVStats()

    svs.print_pilot_table()
    fig, ax = svs.plot_runSuccess()
    fig.show()

    fig, ax = svs.plot_finalRoom()
    fig.show()
