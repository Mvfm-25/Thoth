import json
from datetime import datetime
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

class DiscordWrapped:
    def __init__(self, arquivo_json):
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            self.dados = json.load(f)
        
        self.stats = {
            'mensagens_por_usuario': defaultdict(int),
            'mensagens_por_canal': defaultdict(int),
            'mensagens_por_mes': defaultdict(int),
            'mensagens_por_hora': defaultdict(int),
            'arquivos_por_usuario': defaultdict(int),
            'total_arquivos': 0,
            'total_mensagens': 0,
            'mensagens_por_usuario_mes': defaultdict(lambda: defaultdict(int)),
            'canais_por_usuario': defaultdict(lambda: defaultdict(int))
        }
        
    def processar_dados(self):
        """Processa todas as mensagens e coleta estatísticas"""
        print("🔄 Processando dados do servidor...")
        
        for canal in self.dados['canais']:
            nome_canal = canal['nome']
            
            for msg in canal['mensagens']:
                # Parse da data
                try:
                    data = datetime.fromisoformat(msg['data'].replace('Z', '+00:00'))
                except:
                    continue
                
                usuario = msg['autor_nome']
                mes = data.strftime('%Y-%m')
                hora = data.hour
                
                # Contadores gerais
                self.stats['mensagens_por_usuario'][usuario] += 1
                self.stats['mensagens_por_canal'][nome_canal] += 1
                self.stats['mensagens_por_mes'][mes] += 1
                self.stats['mensagens_por_hora'][hora] += 1
                self.stats['total_mensagens'] += 1
                
                # Contadores por usuário/mês
                self.stats['mensagens_por_usuario_mes'][usuario][mes] += 1
                self.stats['canais_por_usuario'][usuario][nome_canal] += 1
                
                # Contagem de arquivos
                num_arquivos = len(msg.get('arquivos', []))
                if num_arquivos > 0:
                    self.stats['arquivos_por_usuario'][usuario] += num_arquivos
                    self.stats['total_arquivos'] += num_arquivos
        
        print(f"✓ Processadas {self.stats['total_mensagens']} mensagens!")
    
    def gerar_wrapped_anual(self, ano=None):
        """Gera o recap anual do servidor"""
        if ano is None:
            ano = datetime.now().year
        
        print(f"\n{'='*60}")
        print(f"🎉 DISCORD WRAPPED {ano} 🎉".center(60))
        print(f"{'='*60}\n")
        
        # Filtrar dados do ano
        msgs_ano = {mes: count for mes, count in self.stats['mensagens_por_mes'].items() 
                    if mes.startswith(str(ano))}
        
        if not msgs_ano:
            print(f"⚠️  Nenhuma mensagem encontrada para o ano {ano}")
            return
        
        total_msgs_ano = sum(msgs_ano.values())
        
        print(f"📊 ESTATÍSTICAS GERAIS")
        print(f"   Total de mensagens: {total_msgs_ano:,}")
        print(f"   Total de arquivos compartilhados: {self.stats['total_arquivos']:,}")
        print(f"   Média de msgs/dia: {total_msgs_ano/365:.1f}")
        
        # Top usuários do ano
        usuarios_ano = defaultdict(int)
        for usuario, msgs_por_mes in self.stats['mensagens_por_usuario_mes'].items():
            for mes, count in msgs_por_mes.items():
                if mes.startswith(str(ano)):
                    usuarios_ano[usuario] += count
        
        print(f"\n👑 TOP 5 USUÁRIOS MAIS ATIVOS")
        for i, (usuario, count) in enumerate(sorted(usuarios_ano.items(), 
                                                     key=lambda x: x[1], reverse=True)[:5], 1):
            porcentagem = (count / total_msgs_ano) * 100
            print(f"   {i}. {usuario}: {count:,} msgs ({porcentagem:.1f}%)")
        
        # Top canais
        print(f"\n📺 TOP 5 CANAIS MAIS ATIVOS")
        for i, (canal, count) in enumerate(sorted(self.stats['mensagens_por_canal'].items(), 
                                                   key=lambda x: x[1], reverse=True)[:5], 1):
            porcentagem = (count / self.stats['total_mensagens']) * 100
            print(f"   {i}. #{canal}: {count:,} msgs ({porcentagem:.1f}%)")
        
        # Mês mais ativo
        print(f"\n📅 MESES MAIS ATIVOS")
        meses_ordenados = sorted(msgs_ano.items(), key=lambda x: x[1], reverse=True)
        for i, (mes, count) in enumerate(meses_ordenados[:3], 1):
            mes_nome = datetime.strptime(mes, '%Y-%m').strftime('%B')
            print(f"   {i}. {mes_nome}: {count:,} msgs")
        
        # Top compartilhadores de arquivos
        if self.stats['total_arquivos'] > 0:
            print(f"\n📎 TOP 3 COMPARTILHADORES DE ARQUIVOS")
            for i, (usuario, count) in enumerate(sorted(self.stats['arquivos_por_usuario'].items(), 
                                                         key=lambda x: x[1], reverse=True)[:3], 1):
                print(f"   {i}. {usuario}: {count} arquivos")
        
        # Horários mais ativos
        print(f"\n⏰ HORÁRIOS MAIS ATIVOS")
        top_horas = sorted(self.stats['mensagens_por_hora'].items(), 
                          key=lambda x: x[1], reverse=True)[:3]
        for i, (hora, count) in enumerate(top_horas, 1):
            print(f"   {i}. {hora:02d}:00 - {hora+1:02d}:00: {count:,} msgs")
        
        # Criar visualizações
        self._criar_graficos_anuais(ano, msgs_ano, usuarios_ano)
    
    def gerar_wrapped_mensal(self, mes=None, ano=None):
        """Gera o recap mensal do servidor"""
        if mes is None:
            mes = datetime.now().month
        if ano is None:
            ano = datetime.now().year
        
        mes_str = f"{ano}-{mes:02d}"
        mes_nome = datetime.strptime(mes_str, '%Y-%m').strftime('%B de %Y')
        
        print(f"\n{'='*60}")
        print(f"📅 WRAPPED DE {mes_nome.upper()} 📅".center(60))
        print(f"{'='*60}\n")
        
        # Filtrar dados do mês
        msgs_mes = self.stats['mensagens_por_mes'].get(mes_str, 0)
        
        if msgs_mes == 0:
            print(f"⚠️  Nenhuma mensagem encontrada para {mes_nome}")
            return
        
        print(f"📊 ESTATÍSTICAS DO MÊS")
        print(f"   Total de mensagens: {msgs_mes:,}")
        print(f"   Média de msgs/dia: {msgs_mes/30:.1f}")
        
        # Top usuários do mês
        usuarios_mes = {usuario: msgs[mes_str] 
                       for usuario, msgs in self.stats['mensagens_por_usuario_mes'].items()
                       if mes_str in msgs}
        
        print(f"\n👑 TOP 5 USUÁRIOS DO MÊS")
        for i, (usuario, count) in enumerate(sorted(usuarios_mes.items(), 
                                                     key=lambda x: x[1], reverse=True)[:5], 1):
            porcentagem = (count / msgs_mes) * 100
            print(f"   {i}. {usuario}: {count:,} msgs ({porcentagem:.1f}%)")
        
        # MVP do mês (quem mais cresceu comparado ao mês anterior)
        mes_anterior = f"{ano}-{mes-1:02d}" if mes > 1 else f"{ano-1}-12"
        crescimentos = {}
        for usuario, count in usuarios_mes.items():
            count_anterior = self.stats['mensagens_por_usuario_mes'][usuario].get(mes_anterior, 0)
            if count_anterior > 0:
                crescimento = ((count - count_anterior) / count_anterior) * 100
                crescimentos[usuario] = crescimento
        
        if crescimentos:
            print(f"\n🚀 MVP DO MÊS (maior crescimento)")
            mvp = max(crescimentos.items(), key=lambda x: x[1])
            print(f"   {mvp[0]}: +{mvp[1]:.1f}% de crescimento!")
        
        self._criar_graficos_mensais(mes_str, usuarios_mes)
    
    def gerar_wrapped_individual(self, usuario):
        """Gera o wrapped personalizado para um usuário específico"""
        if usuario not in self.stats['mensagens_por_usuario']:
            print(f"⚠️  Usuário '{usuario}' não encontrado")
            return
        
        print(f"\n{'='*60}")
        print(f"🎯 SEU WRAPPED PESSOAL, {usuario.upper()}! 🎯".center(60))
        print(f"{'='*60}\n")
        
        total_msgs = self.stats['mensagens_por_usuario'][usuario]
        total_arquivos = self.stats['arquivos_por_usuario'].get(usuario, 0)
        
        print(f"📊 SUAS ESTATÍSTICAS")
        print(f"   Total de mensagens: {total_msgs:,}")
        print(f"   Arquivos compartilhados: {total_arquivos}")
        
        # Posição no ranking geral
        ranking = sorted(self.stats['mensagens_por_usuario'].items(), 
                        key=lambda x: x[1], reverse=True)
        posicao = next(i for i, (u, _) in enumerate(ranking, 1) if u == usuario)
        print(f"   Sua posição no servidor: #{posicao} de {len(ranking)}")
        
        # Canal favorito
        canais_usuario = self.stats['canais_por_usuario'][usuario]
        canal_fav = max(canais_usuario.items(), key=lambda x: x[1])
        print(f"\n📺 SEU CANAL FAVORITO")
        print(f"   #{canal_fav[0]}: {canal_fav[1]:,} mensagens")
        
        # Mês mais ativo
        msgs_por_mes = self.stats['mensagens_por_usuario_mes'][usuario]
        mes_ativo = max(msgs_por_mes.items(), key=lambda x: x[1])
        mes_nome = datetime.strptime(mes_ativo[0], '%Y-%m').strftime('%B de %Y')
        print(f"\n🔥 SEU MÊS MAIS ATIVO")
        print(f"   {mes_nome}: {mes_ativo[1]:,} mensagens")
        
    def _criar_graficos_anuais(self, ano, msgs_ano, usuarios_ano):
        """Cria visualizações para o wrapped anual"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'Discord Wrapped {ano}', fontsize=20, fontweight='bold')
        
        # Gráfico 1: Mensagens por mês
        meses = sorted(msgs_ano.keys())
        valores = [msgs_ano[m] for m in meses]
        meses_labels = [datetime.strptime(m, '%Y-%m').strftime('%b') for m in meses]
        
        axes[0, 0].bar(meses_labels, valores, color='#5865F2')
        axes[0, 0].set_title('Mensagens por Mês', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('Número de Mensagens')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Gráfico 2: Top 10 usuários
        top_usuarios = sorted(usuarios_ano.items(), key=lambda x: x[1], reverse=True)[:10]
        nomes = [u[0][:15] for u in top_usuarios]
        msgs = [u[1] for u in top_usuarios]
        
        axes[0, 1].barh(nomes, msgs, color='#57F287')
        axes[0, 1].set_title('Top 10 Usuários', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Número de Mensagens')
        axes[0, 1].invert_yaxis()
        
        # Gráfico 3: Atividade por hora
        horas = list(range(24))
        msgs_por_hora = [self.stats['mensagens_por_hora'].get(h, 0) for h in horas]
        
        axes[1, 0].plot(horas, msgs_por_hora, marker='o', linewidth=2, color='#FEE75C')
        axes[1, 0].fill_between(horas, msgs_por_hora, alpha=0.3, color='#FEE75C')
        axes[1, 0].set_title('Atividade por Horário', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Hora do Dia')
        axes[1, 0].set_ylabel('Número de Mensagens')
        axes[1, 0].set_xticks(range(0, 24, 3))
        axes[1, 0].grid(True, alpha=0.3)
        
        # Gráfico 4: Top 5 canais
        top_canais = sorted(self.stats['mensagens_por_canal'].items(), 
                           key=lambda x: x[1], reverse=True)[:5]
        nomes_canais = [f"#{c[0][:20]}" for c in top_canais]
        msgs_canais = [c[1] for c in top_canais]
        
        colors = ['#5865F2', '#57F287', '#FEE75C', '#EB459E', '#ED4245']
        axes[1, 1].pie(msgs_canais, labels=nomes_canais, autopct='%1.1f%%',
                       colors=colors, startangle=90)
        axes[1, 1].set_title('Top 5 Canais', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Salvar
        Path('wrapped').mkdir(exist_ok=True)
        plt.savefig(f'wrapped/wrapped_{ano}.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Gráficos salvos em 'wrapped/wrapped_{ano}.png'")
        plt.show()
    
    def _criar_graficos_mensais(self, mes_str, usuarios_mes):
        """Cria visualizações para o wrapped mensal"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        mes_nome = datetime.strptime(mes_str, '%Y-%m').strftime('%B de %Y')
        fig.suptitle(f'Wrapped de {mes_nome}', fontsize=18, fontweight='bold')
        
        # Gráfico 1: Top 10 usuários do mês
        top_usuarios = sorted(usuarios_mes.items(), key=lambda x: x[1], reverse=True)[:10]
        nomes = [u[0][:15] for u in top_usuarios]
        msgs = [u[1] for u in top_usuarios]
        
        axes[0].barh(nomes, msgs, color='#5865F2')
        axes[0].set_title('Top 10 Usuários do Mês', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Número de Mensagens')
        axes[0].invert_yaxis()
        
        # Gráfico 2: Distribuição percentual
        colors = plt.cm.Set3(range(len(top_usuarios)))
        axes[1].pie(msgs, labels=nomes, autopct='%1.1f%%',
                   colors=colors, startangle=90)
        axes[1].set_title('Distribuição de Atividade', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        # Salvar
        Path('wrapped').mkdir(exist_ok=True)
        arquivo = mes_str.replace('-', '_')
        plt.savefig(f'wrapped/wrapped_{arquivo}.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Gráficos salvos em 'wrapped/wrapped_{arquivo}.png'")
        plt.show()

# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Inicializar com o arquivo JSON do seu servidor
    wrapped = DiscordWrapped('servidor_410599528178384907.json')
    
    # Processar todos os dados
    wrapped.processar_dados()
    
    # Gerar wrapped anual (ano atual ou especificar)
    wrapped.gerar_wrapped_anual(2024)
    
    # Gerar wrapped mensal (mês atual ou especificar)
    # wrapped.gerar_wrapped_mensal(11, 2024)  # Novembro 2024
    
    # Gerar wrapped individual para um usuário específico
    # wrapped.gerar_wrapped_individual('NomeDoUsuario')