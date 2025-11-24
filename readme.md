# 💰 Show do Milhão (Pygame Edition)

Este é um jogo de quiz no estilo "Show do Milhão", desenvolvido em Python utilizando a biblioteca Pygame. O jogo apresenta um menu principal, diferentes níveis de dificuldade, um sistema de perguntas carregadas de um arquivo JSON e um ranking persistente.

## ✨ Funcionalidades

* **Menu Principal:** Navegue entre "Iniciar Jogo", "Dificuldade", "Ranking" e "Sair".
* **Dificuldades:** Escolha entre Fácil, Médio e Difícil. Isso afeta o número de vidas e o tempo para responder.
* **Sistema de Vidas:** O jogador tem um número limitado de vidas (definido pela dificuldade).
* **Timer:** Cada pergunta tem um limite de tempo.
* **Perguntas Externas:** As perguntas e respostas são carregadas dinamicamente do arquivo `data/questions.json`.
* **Ranking Persistente:** Os resultados são salvos em `data/ranking.json` e podem ser visualizados na tela de Ranking.
* **Efeitos Sonoros:** O jogo inclui música de menu e efeitos sonoros para acertos, erros e telas de transição.

## 🛠️ Instalação

Para rodar este projeto, você precisará do Python 3 e da biblioteca Pygame.

1.  **Clone o repositório** (ou baixe os arquivos para uma pasta).

2.  **Instale as dependências:**
    Navegue até a pasta do projeto pelo terminal e instale o `pygame` usando o `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Verifique a Estrutura de Pastas:**
    O jogo espera uma estrutura de pastas específica para encontrar os *assets* (fontes, imagens, sons) e os dados (perguntas, ranking). Certifique-se de que seu projeto está organizado da seguinte forma:

    ```
    .
    ├── main.py
    ├── requirements.txt
    ├── data/
    │   ├── questions.json
    │   └── ranking.json
    ├── src/
    │   ├── game.py
    │   ├── menu.py
    │   ├── quiz_manager.py
    │   ├── question.py
    │   ├── cutscene.py
    │   ├── ranking_manager.py
    │   └── ranking_screen.py
    └── assets/
        ├── fonts/
        │   └── Montserrat.ttf
        ├── images/
        │   └── fundomenu.png
        └── sounds/
            ├── intro.mp3
            ├── boasorte.mp3
            ├── certaresposta.mp3
            ├── errou.mp3
            ├── certeza.mp3
            ├── pergunta.mp3
            └── tempoacabou.mp3
    ```
    > **Nota:** O jogo falhará se não encontrar os arquivos nas pastas `assets/` e `data/`.

## 🚀 Como Executar

Para iniciar o jogo, basta executar o arquivo `main.py` na raiz do projeto:

```bash
python main.py
```

### 🎮 Controles

* **Setas (Cima/Baixo):** Navegar pelas opções no menu e nas perguntas.
* **Setas (Esquerda/Direita):** Mudar a dificuldade no menu.
* **ENTER:** Selecionar uma opção ou confirmar uma resposta.
* **ESC:** Cancelar a confirmação de uma resposta.

## 📝 Adicionando Novas Perguntas

Você pode adicionar novas perguntas ao jogo de duas maneiras:

1.  **Editando o JSON diretamente:**
    Abra o arquivo `data/questions.json` e adicione um novo objeto ao array, seguindo o formato:
    ```json
    {
      "pergunta": "Qual é a sua pergunta?",
      "opcoes": ["Opção A", "Opção B", "Opção C", "Opção D"],
      "resposta": 0
    }
    ```
    *Atenção:* `"resposta"` é o **índice** da opção correta na lista `"opcoes"` (começando em 0).

2.  **Usando o script interativo:**
    Você pode executar o script `question.py` para adicionar uma pergunta via terminal:
    ```bash
    python src/question.py
    ```
    O script irá guiá-lo para inserir a pergunta, as opções e a resposta correta.