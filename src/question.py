# src/question.py
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json
import random
import os

@dataclass
class Question:
    pergunta: str
    opcoes: List[str]
    resposta: int  # índice da opção correta em opcoes

    def to_dict(self) -> Dict[str, Any]:
        return {"pergunta": self.pergunta, "opcoes": self.opcoes, "resposta": self.resposta}

    def shuffled(self, seed: int = None) -> "Question":
        """
        Retorna uma cópia embaralhada das opções e ajusta o índice da resposta.
        Útil se quiser apresentar opções em ordem aleatória.
        """
        if seed is not None:
            random.seed(seed)
        mapping = list(range(len(self.opcoes)))
        random.shuffle(mapping)
        new_options = [self.opcoes[i] for i in mapping]
        new_resposta = mapping.index(self.resposta)
        return Question(self.pergunta, new_options, new_resposta)


# ---------- Funções utilitárias para o arquivo JSON ----------
DATA_PATH = os.path.join("data", "questions.json")

def load_questions(path: str = DATA_PATH, limit: int = None) -> List[Question]:
    """
    Carrega perguntas do JSON e retorna lista de Question.
    Se o arquivo não existir, retorna lista vazia.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return []
    except Exception:
        # se o JSON estiver inválido, tentar retornar lista vazia
        return []

    qs = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if "pergunta" in item and "opcoes" in item and "resposta" in item:
            try:
                q = Question(
                    pergunta=item["pergunta"],
                    opcoes=list(item["opcoes"]),
                    resposta=int(item["resposta"])
                )
                qs.append(q)
            except Exception:
                continue
    if limit:
        return qs[:limit]
    return qs

def save_questions(questions: List[Question], path: str = DATA_PATH):
    """
    Sobrescreve o arquivo JSON com a lista de perguntas fornecida.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = [q.to_dict() for q in questions]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def append_question(question: Question, path: str = DATA_PATH):
    """
    Adiciona uma pergunta ao arquivo JSON (append).
    Cria o arquivo se não existir.
    """
    qs = load_questions(path)
    qs.append(question)
    save_questions(qs, path)

# ---------- Pequena função interativa para facilitar testes ----------
def add_question_interactive():
    """
    Executar este script (python src/question.py) permite adicionar perguntas via terminal.
    """
    print("Adicionar nova pergunta ao data/questions.json")
    p = input("Digite a pergunta: ").strip()
    opts = []
    for i in range(4):
        op = input(f"Opção {i+1} (deixe vazio para parar): ").strip()
        if op == "":
            break
        opts.append(op)
    if len(opts) < 2:
        print("É preciso ao menos 2 opções. Abortando.")
        return
    while True:
        try:
            r = int(input(f"Índice da resposta correta (0 a {len(opts)-1}): ").strip())
            if 0 <= r < len(opts):
                break
        except:
            pass
        print("Valor inválido.")
    q = Question(pergunta=p, opcoes=opts, resposta=r)
    append_question(q)
    print("Pergunta adicionada com sucesso.")
