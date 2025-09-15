import os

import matplotlib.pyplot as plt
import pandas as pd

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

    @property
    def df_cards(self):
        return self._df_cards[
            self._load.carddb[
                (self._load.carddb["Rarity"] != "Starter")
                & (self._load.carddb["Rarity"] != "Created")
                & (self._load.carddb["Rarity"] != "Junk")
            ]["Card"]
        ]

    @property
    def df_artifacts(self):
        return self._df_artifacts[
            self._load.artifactdb[
                (self._load.artifactdb["Rarity"] != "Starter")
                & (self._load.artifactdb["Rarity"] != "N/A")
            ]["Artifact"]
        ]
