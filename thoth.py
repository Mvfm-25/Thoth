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

TOKEN = "35a0034ac9550afe60ec47118651d3cd6865b741ca566dacd69815ab7761f39c"

intents = discord.Intents.default()
# Pra conseguir ler a mensagem.
intents.message_content = True
intents.guilds = True
# Pra ver informação dos membros.
intents.members = True

cliente = discord.Client(intents = intents)

@cliente.event
async def onReady():
    print(f'Loggado como:  {cliente.user}')
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
                async for mensagem in canal.history(limit=none):

                    dadosMensagem = {
                        "id" : mensagem.id,
                        "autor_id" : mensagem.author.id,
                        "autor_nome" : mensagem.author.name,
                        "conteudo" : mensagem.content,
                        "data" : str(mensagem.created_at),
                        "arquivos": [attachment.url for attachment in mensagem.attachments]
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

        