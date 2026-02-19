import threading
from datetime import datetime
import json
from pathlib import Path

class DeckController:
    def __init__(self, deck_model, deck_repo, profile_repo, scryfall, downloader):
        """
        Controlador da GALERIA DE DECKS. 
        Ele lê os decks já salvos no HD e exibe para o jogador escolher.
        """
        self.model = deck_model
        self.deck_repo = deck_repo
        self.profile_repo = profile_repo
        self.scryfall = scryfall
        self.downloader = downloader
        
        # --- ATRIBUTOS PARA A UI DA GALERIA ---
        self.estado = "INICIAL" 
        self.decks_disponiveis = [] # Lista de decks para a tela de seleção
        
        # Controladores de Navegação no Carrossel da Galeria
        self.index_deck_atual = 0

        # Carrega os dados do "Machete" ao iniciar o programa
        self.reload_data()

    def reload_data(self):
        """
        Lê o 'profiler.json' para pegar a lista rápida de decks do jogador.
        Para cada deck, vai no arquivo físico dele tentar puxar a imagem do comandante para usar como capa.
        """
        # Limpa a lista antes de recarregar para não duplicar
        self.decks_disponiveis.clear()
        
        # 1. Lê o perfil usando o ProfileRepository (Garante que ler_perfil seja usado)
        try:
            perfil = self.profile_repo.ler_perfil()
            # Pega a lista "decks". Se não existir, retorna lista vazia []
            lista_decks_perfil = perfil.get("decks", [])
        except Exception as e:
            print(f"[AVISO] Erro ao ler perfil na Galeria: {e}")
            lista_decks_perfil = []

        # 2. Para cada deck no perfil, tenta achar a arte local do Comandante
        for ref_deck in lista_decks_perfil:
            nome_deck = ref_deck.get("name", "Sem Nome")
            nome_comandante = ref_deck.get("commander", "Desconhecido")
            caminho_capa = ""
            
            # Formata o nome do deck igual fizemos no repositório para achar o arquivo físico
            nome_arquivo_deck = nome_deck.replace(" ", "_").lower() + ".json"
            caminho_arquivo = Path("data/decks") / nome_arquivo_deck
            
            # Tenta abrir o arquivo físico do deck para achar onde está a foto do Comandante
            if caminho_arquivo.exists():
                try:
                    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                        dados_fisicos = json.load(f)
                        # Procura a carta que tem o mesmo nome do comandante
                        for carta in dados_fisicos.get("cards", []):
                            if carta.get("name") == nome_comandante:
                                # Acha a imagem local na pasta assets!
                                caminho_capa = carta.get("ref_image", "")
                                break
                except Exception as e:
                    print(f"Não foi possível ler a capa de {nome_deck}: {e}")

            # Monta o objeto para a Galeria renderizar
            self.decks_disponiveis.append({
                "name": nome_deck,
                "commander": nome_comandante,
                "cover_image_path": caminho_capa # <--- O PULO DO GATO PARA A UI
            })
            
        # Garante que o índice não estoure se um deck foi deletado
        if self.decks_disponiveis and self.index_deck_atual >= len(self.decks_disponiveis):
            self.index_deck_atual = 0

    def get_deck_atual(self):
        """Retorna o deck que está em foco na tela da galeria."""
        if self.decks_disponiveis and 0 <= self.index_deck_atual < len(self.decks_disponiveis):
            return self.decks_disponiveis[self.index_deck_atual]
        return None

    def navegar_decks(self, direcao):
        """Muda o deck selecionado na galeria (Direita ou Esquerda)."""
        if self.decks_disponiveis:
            self.index_deck_atual = (self.index_deck_atual + direcao) % len(self.decks_disponiveis)

    def selecionar_deck_para_jogo(self):
        """
        Ação final da Galeria: O Machete clicou em 'JOGAR'.
        Retorna os dados do deck para o GameController carregar a partida.
        """
        deck_selecionado = self.get_deck_atual()
        if deck_selecionado:
            print(f"[MESA] Carregando o deck '{deck_selecionado['name']}' para a partida...")
            # Aqui você no futuro vai conectar com o GameModel
            return True
        return False