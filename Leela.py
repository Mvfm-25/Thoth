# Script para baixar diretamente os arquivos anexados nas mensagens do dump JSON gerado pelo 'Thoth'.
# Criando isso agora pois estava muito chato clicar em um link para o arquivo e descobrir que o link foi expirado.
# [mvfm]
#
# Criado : 13/11/2025  ||  Última vez alterado : 13/11/2025

import os
import json
import requests

# Lendo o arquivo JSON resultante de 'Thoth'.
CAMINHO_JSON = "servidor_410599528178384907.json"
# Pasta onde os arquivos baixados serão salvos
PASTA_SAIDA = "anexos"

os.makedirs(PASTA_SAIDA, exist_ok=True)

with open(CAMINHO_JSON, "r", encoding="utf-8") as f:
    servidores = json.load(f)

# Caso o JSON seja um único servidor (não lista)
# Aqui caso 'Thoth' seja incluído em outros servidores futuramente.
if isinstance(servidores, dict):
    servidores = [servidores]

for servidor in servidores:
    nome_servidor = servidor.get("nome", f"servidor_{servidor.get('id', 'sem_id')}")
    print(f"\n=== Servidor: {nome_servidor} ===")

    for canal in servidor.get("canais", []):
        nome_canal = canal.get("nome", f"canal_{canal.get('id', 'sem_id')}")
        print(f"\n-> Canal: {nome_canal}")

        for mensagem in canal.get("mensagens", []):
            arquivos = mensagem.get("arquivos", [])
            if not arquivos:
                continue

            autor = mensagem.get("autor_nome", "desconhecido")
            data = mensagem.get("data", "sem_data")
            msg_id = mensagem.get("id")

            for i, url in enumerate(arquivos, start=1):
                try:
                    # Pega o nome do arquivo direto do link
                    nome_arquivo = url.split("/")[-1].split("?")[0]

                    # Gera uma estrutura de pastas organizada, levando em consideração a hierarquia dos canais.
                    pasta_destino = os.path.join(PASTA_SAIDA, nome_servidor, nome_canal)
                    os.makedirs(pasta_destino, exist_ok=True)

                    caminho_final = os.path.join(pasta_destino, nome_arquivo)

                    # Faz o download
                    resp = requests.get(url, timeout=15)
                    if resp.status_code == 200:
                        with open(caminho_final, "wb") as f_out:
                            f_out.write(resp.content)
                        print(f"[{autor}] {nome_arquivo} salvo em {pasta_destino}")
                    else:
                        print(f"Erro {resp.status_code} ao baixar {url}")

                except Exception as e:
                    print(f"Erro ao baixar arquivo da mensagem {msg_id}: {e}")
