# Primeira implementação, procurando só ler mensagens recentes em um canal específico para salvar em um JSON.
# Nada muito complicado ainda.
#
# [mvfm]
#
# Criado : 11/11/2025  ||  Última vez Alterado : 11/11/2025

# Colocado assim pq eu estava muito puto com o pip não encontrando o módulo.
try:
    import discord
except Exception:
    import sys
    print("Módulo 'discord' não encontrado. Instale com: python -m pip install -U discord.py")
    sys.exit(1)

import json
import os
import aiohttp

# Token do bot corrigido. Alcançado pelo portal de desenvolvedores do Discord.
with open('config.json', 'r') as f:
    TOKEN = json.load(f)["token"]

intents = discord.Intents.default()
# Pra conseguir ler a mensagem.
intents.message_content = True
intents.guilds = True
# Pra ver informação dos membros.
intents.members = True

cliente = discord.Client(intents = intents)

# Correção para conseguir de fato os arquivos anexados.
# Vou estar salvando tudo do servidor, basicamente.
PASTA_SAIDA = "anexos"
os.makedirs(PASTA_SAIDA, exist_ok=True)

@cliente.event
async def on_ready():
    print(f'Loggado como:  {cliente.user}')

    async with aiohttp.ClientSession() as session:
        for guild in cliente.guilds:
            print(f'Processando servidor: {guild.name} (id: {guild.id}) ')
            dadosServidor ={
                "id" : guild.id,
                "nome" : guild.name,
                "canais" : []
            }
            # Passa por todos canais de texto.
            for canal in guild.text_channels:
                print(f'Processando canal: {canal.name} (id: {canal.id})')
                dadosCanal ={
                    "id" : canal.id,
                    "nome" : canal.name,
                    "mensagens" : []
                }
                try :
                    # Passa por cada mensagem no canal.
                    async for mensagem in canal.history(limit=None):

                        arquivos_info = []
                        if mensagem.attachments:
                            # Criando subpasta para o canal.
                            pasta_canal = os.path.join(PASTA_SAIDA, f'servidor_{guild.name}', f'canal_{canal.name}')
                            os.makedirs(pasta_canal, exist_ok=True)

                            for attachment in mensagem.attachments:
                                nome_aquivo = f"{mensagem.auto_nome}_{attachment.filename}"
                                caminho_local = os.path.join(pasta_canal, nome_aquivo)

                                # Baixando então o arquivo.
                                try:
                                    async with session.get(attachment.url) as resp:
                                        if resp.status == 200:
                                            with open(caminho_local, 'wb') as f_out:
                                                f_out.write(await resp.read())
                                            print("Arquivo salvo em:", {caminho_local})
                                        else :
                                            print("Erro ao baixar arquivo:", attachment.url)
                                except Exception as e:
                                    print("Erro ao baixar arquivo:", attachment.url, " - ", e)

                                arquivos_info.append({
                                    "url_original" : attachment.url,
                                    "caminho_local" : caminho_local.replace("\\", "/")
                                })

                        dadosMensagem = {
                            "id" : mensagem.id,
                            "autor_id" : mensagem.author.id,
                            "autor_nome" : mensagem.author.name,
                            "conteudo" : mensagem.content,
                            "data" : str(mensagem.created_at),
                            "arquivos": arquivos_info # Metadados, não só links agora.
                        }

                        dadosCanal["mensagens"].append(dadosMensagem)
                except discord.Forbidden:
                    print(f'Não tenho permissão para ler o canal: {canal.name} (id: {canal.id})')
                except Exception as e:
                    print(f'Erro ao ler o canal: {canal.name} (id: {canal.id}) - {e}')
                dadosServidor["canais"].append(dadosCanal)
        
            # Salavndo tudo coletado em um arquivo JSON adequado.
            nomeArquivo = f'servidor_{guild.id}.json'
            with open(nomeArquivo, 'w', encoding='utf-8') as f:
                json.dump(dadosServidor, f, ensure_ascii=False, indent=4)
            print(f'Dados do servidor salvos em: {nomeArquivo}')

    await cliente.close()

cliente.run(TOKEN)

        