import json
import os

class RankingManager:
    def __init__(self, file_path="data/ranking.json"):
        self.file_path = file_path
        self.entries = []
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    self.entries = json.load(f)
                except json.JSONDecodeError:
                    self.entries = []
        else:
            self.entries = []

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=4)

    def add_entry(self, name, score, patente):
        self.entries.append({
            "name": name,
            "score": score,
            "patente": patente
        })
        self.entries.sort(key=lambda x: x["score"], reverse=True)
        self.save() 

    def get_all(self):
        return self.entries

    def get_position(self, name, score):
        self.entries.sort(key=lambda x: x["score"], reverse=True)
        for idx, e in enumerate(self.entries, 1):
            if e["name"] == name and e["score"] == score:
                return idx
        return None
