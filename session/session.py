import json
import os

class Session:
    def __init__(self):
        self.savefile = "default"
        self.filepath = "session/session.json"

    def load(self) -> "Session":
        if not os.path.exists(self.filepath):
            self.save()
        
        with open(self.filepath, "r") as f:
            state_dict = json.load(f)

        print(state_dict)
        self.savefile = state_dict["savefile"]

        return self

    def save(self) -> "Session":
        state_dict = {
            "savefile": self.savefile
        }
        with open(self.filepath, "w") as f:
            json.dump(state_dict, f)

        return self