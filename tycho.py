# Primeira implementação de 'tycho.py'. 
# Sua única função essencialmente é ler do arquivo gerado pelo 'thoth.py' para criar uma word cloud das 200 palavras mais frequentemente usadas no servidor selecionado.
#
# [mvfm]
#
# Criado : 11/11/2025  ||  Última vez alterado : 11/11/2025

import json
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import sys
import os

def limpaTexto(texto):
    # Remove links, emojis e caracteres especiais
    texto = re.sub(r"http\S+", "", texto)  # Remove links
    texto = re.sub(r"<@[!&]?\d+>", "", texto)  # Remove menções do Discord (<@123456789>)
    texto = re.sub(r"[^A-Za-zÀ-ÿ0-9\s]", "", texto)  # Remove símbolos e emojis
    texto = texto.lower().strip()
    return texto

def geraWordCloud(caminhoJson, caminhoSaida="wordcloud.png"):
    if not os.path.exists(caminhoJson):
        print(f"Arquivo '{caminhoJson}' não encontrado.")
        sys.exit(1)

    with open(caminhoJson, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    mensagens = []
    for canal in dados.get("canais", []):
        for mensagem in canal.get("mensagens", []):
            conteudo = mensagem.get("conteudo", "").strip()
            if conteudo:  # Ignora mensagens vazias
                mensagens.append(conteudo)

    if not mensagens:
        print("Nenhuma mensagem com conteúdo encontrada no arquivo JSON.")
        return

    # Junta tudo encontrado e limpa
    textoCompleto = " ".join(mensagens)
    textoCompleto = limpaTexto(textoCompleto)

    # Separa novamente pra contar as frequências de cada palavra
    palavras = textoCompleto.split()
    freq = Counter(palavras)

    if not freq:
        print("Nenhuma palavra encontrada após limpeza de texto.")
        return

    # Cria a WordCloud
    wordCloud = WordCloud(
        width=1200,
        height=800,
        background_color="black",
        colormap="rainbow",
        max_words=10000
    ).generate_from_frequencies(freq)

    # Exibe e salva
    plt.figure(figsize=(12, 8))
    plt.imshow(wordCloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(caminhoSaida, dpi=300)
    plt.close()

    print("Word Cloud criada em:", caminhoSaida)

if __name__ == "__main__":
    geraWordCloud("servidor_410599528178384907.json", "wordcloud.png")
