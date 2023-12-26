import json
import os

class Session:
    def __init__(self):
        self.savefile = "default"

    def load(self) -> "Session":
        if not os.path.exists("session.json"):
            self.save()
        
        with open("session/session.json", "r") as f:
            state_dict = json.load(f)

        self.savefile = state_dict["savefile"]

        return self

    def save(self) -> "Session":
        state_dict = {
            "savefile": self.savefile
        }
        with open("session/session.json", "w") as f:
            json.dump(state_dict, f)

        return self