import os

import matplotlib.pyplot as plt
import pandas as pd

from . import _load


class SVStats:
    def __init__(self, rundir=None):
        if not rundir:
            if os.path.exists("data"):
                dirs = [
                    dir
                    for dir in os.listdir("data")
                    if os.path.isdir(os.path.join("data", dir))
                ]
                if len(dirs):
                    self.rundir = os.path.join("data", dirs[0])

        else:
            self.rundir = rundir

        self.df_runs = _load.loadRuns(self.rundir)
        self.df_cards = _load.loadCardDatabase()
