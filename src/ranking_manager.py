import json
import os
from datetime import datetime

RANKING_PATH = "data/ranking.json"
MAX_ENTRIES = 100

class RankingManager:
    def __init__(self, path=RANKING_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data[:MAX_ENTRIES], f, ensure_ascii=False, indent=2)

    def add_entry(self, nome, score, patente):
        entry = {
            "nome": nome,
            "score": int(score),
            "patente": patente,
            "date": datetime.now().isoformat()
        }
        self.data.append(entry)
        # ordena decrescente por score
        self.data.sort(key=lambda e: e["score"], reverse=True)
        self._save()

    def get_top(self, limit=10):
        return self.data[:limit]

    def get_position(self, nome, score):
        # retorna posição 1-based do primeiro que bate (nome+score) ou None
        for i, e in enumerate(self.data, start=1):
            if e["nome"] == nome and e["score"] == score:
                return i
        return None
