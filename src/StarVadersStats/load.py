import json
import os

import pandas as pd
import wikitextparser as wtp

curDir = os.path.dirname(__file__)


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

        with open(os.path.join(rundir, "rundata.json")) as f:
            runs[directory]["rundata"] = json.load(f)

        with open(os.path.join(rundir, "playerdata.json")) as f:
            runs[directory]["playerdata"] = json.load(f)

        with open(os.path.join(rundir, "challengedata.json")) as f:
            runs[directory]["challengedata"] = json.load(f)

    if len(runs):
        return pd.DataFrame(
            {
                "runID": [run["rundata"]["runID"] for _, run in runs.items()],
                "PilotName": [
                    run["playerdata"]["PilotName"] for _, run in runs.items()
                ],
                "Difficulty": [
                    run["challengedata"]["Difficulty"] for _, run in runs.items()
                ],
                "Success": [
                    2
                    if run["rundata"]["isTrueVictory"]
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
                "Seed": [run["rundata"]["seed"] for _, run in runs.items()],
            }
        )
    else:
        raise Warning("No runs found, return empty Dataframe")
        return pd.DataFrame()


def loadCardDatabase():
    def _get_link_text(string):
        wikitext = wtp.parse(string)
        if not len(wikitext.wikilinks):
            return string
        if wikitext.wikilinks[0].text:
            return wikitext.wikilinks[0].text
        return wikitext.wikilinks[0].title

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
