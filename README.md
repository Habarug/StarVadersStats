## StarVadersStats

Just a small package to plot stuff from your StarVaders run history.

## Pre-requisites
- [Python](https://www.python.org/)


## Setup
- Optional, but recommended: Create and activate virtual environment:

```
python -m venv .venv

#Windows
.venv\Scripts\activate
#MacOS and linux
source .venv/bin/activate
```

- Install StarVadersStats and dependencies:

```
pip install -e .
```

- Copy the ```history``` directory from your StarVaders save data into the ```data``` directory.
    - Path to save data for Windows:

    ```
    C:\USER\AppData\LocalLow\Pengonauts\StarVaders\saves
    ```
    - Path to save data for Flatpak Steam install on Linux:
    ```
    ~/.var/app/com.valvesoftware.Steam/.steam/steam/steamapps/compatdata/2097570/pfx/drive_c/users/steamuser/AppData/LocalLow/Pengonauts/StarVaders/saves/
    ```

## Running

- Import and instantiate SVStats

```python
from StarVadersStats import SVStats
svs = SVStats(
    #Optionally supply path to history directly
    #Required if data/history not present in current directory
    rundir = None
)
```

- Plot run success:
```python
fig, ax = svs.plot_runSuccess(
    pilot=None #Optionally filter to specific pilot
)
```
![runSuccess](figs/runSuccess.png)

- Plot final room for failed runs:
```python
fig, ax = svs.plot_finalRoom(
    pilot=None #Optionally filter to specific pilot
)
```
![finalRoom](figs/finalRoom.png)

- Print overview table:
```python
svs.print_pilot_table()
```
![pilotTable](figs/pilotTable.png)