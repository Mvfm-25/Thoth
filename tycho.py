# Primeira implementação de 'tycho.py'. 
# Sua única função essencialmete é ler do arquivo gerado pelo 'thoth.py' para criar uma word cloud das 200 palavras mais frequentemente usadas no servidor selecionado.
#
# [mvfm]
#
# Criado : 11/11/2025  ||  Última vez alterado : 11/11/2025

import json
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

def limpaTexto(texto):
    # Método para remover links, emojis e caracteres especiais como emojis
    texto = re.sub(r"http\S+", "", texto) # Remove links
    texto = re.sub(r"[^A-Za-zÀ-ÿ0-9\s]", "", texto)
    texto = texto.lower()

    return texto

def geraWordCloud(caminhoJson, caminhoSaida = "wordcloud.png"):

    # Pega o arquivo
    with open(caminhoJson, 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    # Carrega as mensagens, respeitando a formatção do JSON
    mensagens = []
    for canal in dados.get("canais", []):
        for mensagem in canal.get("mensagens", []):
            conteudo = mensagem.get()
            if conteudo:
                mensagens.append(mensagem["conteudo"])

    # Junta tudo encontrado e limpa
    textoCompleto = "".join(mensagens)
    textoCompleto = limpaTexto(textoCompleto)

    # Separa novamente pra contar as frequências de cada palavra.
    palavras = textoCompleto.split()
    freq = Counter(palavras)

    # Cria a WordCloud
    wordCloud = WordCloud(
        width=1200,
        height=800,
        background_color="black",
        colormap="rainbow",
        max_words=200
    ).generate_from_frequencies(freq)

    # Exibe e salva
    plt.figure(figsize=(12, 8))
    plt.imshow(wordCloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(caminhoSaida, dpi=300)
    plt.close()

    print("Word Cloud criada em : " + caminhoSaida)


if __name__ == "__main__":
    geraWordCloud("servidor_410599528178384907.json", "wordcloud.png")

    