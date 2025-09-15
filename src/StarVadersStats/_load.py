import json
import os
from datetime import datetime as dt

import pandas as pd
import wikitextparser as wtp

curDir = os.path.dirname(__file__)

pilotDict = {
    "0": "Roxy",
    "1": "Zeke",
    "3": "Noel",
    "100": "Shun",
    "101": "Hali",
    "102": "Kaia",
    "200": "Iris",
    "201": "Xenn",
    "202": "Garu",
    "203": "Sura",
}

classDict = {
    "0": "Gunner",
    "1": "Stinger",
    "2": "Keeper",
}


class Load:
    def __init__(self, rootDir):
        self.rootDir = rootDir

        self.carddb = loadCardDatabase()
        self.artifactdb = loadArtifactDatabase()

        self.runs = loadRuns(self.rootDir)

    def get_df_runs(self):
        runs = self.runs
        if not len(runs):
            raise Warning("No runs found, return empty Dataframe")
            return pd.DataFrame(), pd.DataFrame()
        return pd.DataFrame(
            {
                "runID": [run["rundata"]["runID"] for _, run in runs.items()],
                "Time": [_get_datetime(dir) for dir in runs],
                "PilotName": [
                    _get_pilotname(run["playerdata"]["PilotName"])
                    for _, run in runs.items()
                ],
                "ClassName": [
                    _get_classname(run["playerdata"]["ClassName"])
                    for _, run in runs.items()
                ],
                "Difficulty": [
                    run["challengedata"]["Difficulty"] for _, run in runs.items()
                ],
                "Success": [
                    3
                    if run["rundata"]["isTrueVictory"]
                    else 2
                    if run["rundata"]["actNumber"] == 4
                    else 1
                    if run["rundata"]["isVictory"]
                    else 0
                    for _, run in runs.items()
                ],
                "Packs": [run["rundata"]["Packs"] for _, run in runs.items()],
                "nCards": [
                    len(run["playerdata"]["deckCardDataList"])
                    for _, run in runs.items()
                ],
                "nArtifacts": [
                    len(run["playerdata"]["artifactList"]) for _, run in runs.items()
                ],
                "TotalStars": [
                    run["playerdata"]["totalStarsEarned"] for _, run in runs.items()
                ],
                "Doom": [run["playerdata"]["doomAmount"] for _, run in runs.items()],
                "TotalDoom": [
                    run["rundata"]["TotalDoomCount"] for _, run in runs.items()
                ],
                "InvadersDefeated": [
                    run["rundata"]["InvadersDefeatedCount"] for _, run in runs.items()
                ],
                "MaxCombo": [run["rundata"]["MaxCombo"] for _, run in runs.items()],
                "FinalRoom": [
                    f"{run['rundata']['actNumber']}.{run['rundata']['dayNumber']}"
                    for _, run in runs.items()
                ],
                "Seed": [run["rundata"]["seed"] for _, run in runs.items()],
            }
        )

    def get_df_cards(self):
        carddb = self.carddb[
            (self.carddb["Rarity"] != "Junk") & (self.carddb["Rarity"] != "Created")
        ]

        df_cards = pd.DataFrame(columns=carddb["Card"])
        return df_cards


def loadRuns(rootDir):
    runs = {}

    for directory in os.listdir(rootDir):
        rundir = os.path.join(rootDir, directory)

        if not all(
            file in os.listdir(rundir)
            for file in ["rundata.json", "playerdata.json", "challengedata.json"]
        ):
            raise Warning(
                f"Directory {directory} does not contain the required files, skipping"
            )
            continue

        runs[directory] = {}

        with open(os.path.join(rundir, "rundata.json"), "r") as f:
            runs[directory]["rundata"] = json.load(f)

        with open(os.path.join(rundir, "playerdata.json"), "r") as f:
            runs[directory]["playerdata"] = json.load(f)

        with open(os.path.join(rundir, "challengedata.json"), "r") as f:
            runs[directory]["challengedata"] = json.load(f)

    return runs


def loadCardDatabase():
    with open(os.path.join(curDir, "resources", "cardTable.txt"), "r") as f:
        cardTable = wtp.parse(f.read()).tables[0].data()

    return pd.DataFrame(
        {
            "Card": [_get_link_text(row[0]) for row in cardTable[1:]],
            "ID": [row[2] for row in cardTable[1:]],
            "Class": [_get_link_text(row[3].split(" ", 1)[0]) for row in cardTable[1:]],
            "Pack": [
                _get_link_text(row[3].split(" ", 1)[1])
                if (len(row[3].split(" ")) > 1)
                else None
                for row in cardTable[1:]
            ],
            "Rarity": [row[4] for row in cardTable[1:]],
            "Type": [row[5] for row in cardTable[1:]],
            "Cost": [row[6] for row in cardTable[1:]],
        }
    )


def loadArtifactDatabase():
    with open(os.path.join(curDir, "resources", "artifactTable.txt"), "r") as f:
        artifactTable = wtp.parse(f.read()).tables[0].data()

    return pd.DataFrame(
        {
            "Artifact": [_get_link_text(row[0]) for row in artifactTable[1:]],
            "ID": [row[1] for row in artifactTable[1:]],
            "Class": [
                _get_link_text(row[2].split(" ", 1)[0]) for row in artifactTable[1:]
            ],
            "Pack": [
                _get_link_text(row[2].split(" ", 1)[1])
                if (len(row[2].split(" ")) > 1)
                else None
                for row in artifactTable[1:]
            ],
            "Rarity": [row[3] for row in artifactTable[1:]],
        }
    )


#################
# region UTILITIES
#################


def _get_link_text(string):
    wikitext = wtp.parse(string)
    if not len(wikitext.wikilinks):
        return string
    if wikitext.wikilinks[0].text:
        return wikitext.wikilinks[0].text
    return wikitext.wikilinks[0].title


def _get_pilotname(i):
    if str(i) in pilotDict:
        return pilotDict[str(i)]
    else:
        return str(i)


def _get_classname(i):
    if str(i) in classDict:
        return classDict[str(i)]
    else:
        return str(i)


def _get_datetime(dir):
    return dt.strptime(dir[3:18], "%Y_%m_%d_%H_%M")
