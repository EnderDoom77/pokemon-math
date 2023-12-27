import json
import os
from pokemon import Pokemon
from session.session import Session

def filter_eligible(plist: list[Pokemon]):
    return [p for p in plist if p.image and (p.is_base or (p.is_regional and not (p.is_totem or p.is_gmax or p.is_mega or p.num <= 0)))]

def savename_to_savepath(name: str):
    return f"saves/{path}.json"

def load(savename) -> tuple[list[int], list[int]]:
    '''
    Gets a save filename and returns a list of elo and learning rates stored in the file.
    '''
    with open(savename_to_savepath(savename), "r") as f:
        data = json.load(f)
        elo = data["elo"]
        l_rate = data["l_rate"]
    return (elo, l_rate)

def save(savename, elo: list[int], l_rate: list[int]):
    with open(savename_to_savepath(savename), "w") as f:
        data = {"elo": elo, "l_rate": l_rate}
        json.dump(data, f)

def savefile_exists(savename):
    return os.path.exists(savename_to_savepath(savename))

def get_session_data() -> Session:
    return Session().load()

def save_session_data(data: Session):
    data.save()

def get_default_savefile() -> str:
    return get_session_data().savefile
def change_savefile(session: Session):
    new_savefile = input("save file name: ")
    session.savefile = new_savefile
    save_session_data(session)
    