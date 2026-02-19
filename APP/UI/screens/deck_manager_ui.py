import pygame
from pathlib import Path
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles import colors, settings
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.button import MenuButton
from APP.UI.components.label import Label

class DeckManagerView(BaseScreen):
    def __init__(self, screen, controller, deck_ctrl):
        super().__init__(screen, controller)
        self.deck_ctrl = deck_ctrl
        self.fontes = get_fonts()
        
        self.cx = self.screen.get_width() // 2
        self.cy = self.screen.get_height() // 2
        
        # --- Elementos Fixos ---
        self.label_titulo = Label("GALERIA DE DECKS", (self.cx, 60), self.fontes['titulo'], colors.ACCENT)
        
        self.btn_cadastrar = MenuButton(
            pygame.Rect(self.screen.get_width() - 250, 40, 200, 45), 
            "NOVO DECK", 
            self.fontes['menu']
        )
        
        self.btn_voltar = MenuButton(
            pygame.Rect(40, self.screen.get_height() - 80, 150, 45), 
            "VOLTAR", 
            self.fontes['menu']
        )
        
        # --- Controles do Carrossel Visual ---
        self.btn_prev = MenuButton(pygame.Rect(self.cx - 240, self.cy + 50, 60, 60), "<", self.fontes['menu'])
        self.btn_next = MenuButton(pygame.Rect(self.cx + 180, self.cy + 50, 60, 60), ">", self.fontes['menu'])
        
        # Botão de ação principal
        self.btn_jogar = MenuButton(
            pygame.Rect(self.cx - 150, self.cy + 240, 300, 55), 
            "JOGAR COM ESTE DECK", 
            self.fontes['menu']
        )
        
        self.img_cache_local = {} # Cache para as imagens já salvas no HD

        # Força a leitura do profiler.json para atualizar a lista
        if hasattr(self.deck_ctrl, 'reload_data'):
            self.deck_ctrl.reload_data()

    def _get_local_image(self, caminho):
        """Lê a imagem do HD (pasta assets) e coloca na RAM."""
        if not caminho: return None
        if caminho in self.img_cache_local: return self.img_cache_local[caminho]
        
        try:
            caminho_fisico = Path(caminho)
            if caminho_fisico.exists():
                surf = pygame.image.load(str(caminho_fisico))
                surf = pygame.transform.scale(surf, (280, 390))
                self.img_cache_local[caminho] = surf
                return surf
        except Exception as e:
            print(f"Erro ao carregar capa local {caminho}: {e}")
            
        return None

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.btn_cadastrar.update(mouse_pos)
        self.btn_voltar.update(mouse_pos)
        
        tem_decks = len(self.deck_ctrl.decks_disponiveis) > 0
        
        if tem_decks:
            self.btn_prev.update(mouse_pos)
            self.btn_next.update(mouse_pos)
            self.btn_jogar.update(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.btn_voltar.is_clicked(event):
                    return "MENU"
                
                if self.btn_cadastrar.is_clicked(event):
                    return "DECK_REGISTER"
                    
                if tem_decks:
                    if self.btn_prev.is_clicked(event):
                        self.deck_ctrl.navegar_decks(-1)
                    elif self.btn_next.is_clicked(event):
                        self.deck_ctrl.navegar_decks(1)
                    elif self.btn_jogar.is_clicked(event):
                        # Ação de iniciar a partida (No futuro vai retornar "GAME_START")
                        sucesso = self.deck_ctrl.selecionar_deck_para_jogo()
                        if sucesso:
                            print("Iniciando Jogo... (Implementar Tela de Mesa)")
                            # return "GAME_START" # Descomente quando a tela GameView existir
        return None

    def draw(self):
        self.screen.fill(colors.BG)
        self.label_titulo.draw(self.screen)
        
        self.btn_cadastrar.draw(self.screen)
        self.btn_voltar.draw(self.screen)
        
        decks = self.deck_ctrl.decks_disponiveis
        
        if not decks:
            Label("Sua coleção está vazia.", (self.cx, self.cy - 30), self.fontes['status'], colors.TEXT_SEC).draw(self.screen)
            Label("Clique em 'NOVO DECK' para começar.", (self.cx, self.cy + 10), self.fontes['label'], colors.TEXT_PRIMARY).draw(self.screen)
        else:
            deck_atual = self.deck_ctrl.get_deck_atual()
            if deck_atual:
                # Desenha o Nome do Deck e do Comandante no topo
                Label(deck_atual.get('name', 'Sem Nome').upper(), (self.cx, self.cy - 220), self.fontes['titulo'], colors.TEXT_PRIMARY).draw(self.screen)
                Label(f"Cmd: {deck_atual.get('commander', 'Desconhecido')}", (self.cx, self.cy - 190), self.fontes['label'], colors.ACCENT).draw(self.screen)
                
                # Desenha a Arte da Capa
                caminho_arte = deck_atual.get('cover_image_path', '')
                surf = self._get_local_image(caminho_arte)
                
                if surf:
                    rect = surf.get_rect(center=(self.cx, self.cy + 20))
                    self.screen.blit(surf, rect)
                else:
                    # Desenha um quadrado de "Arte não encontrada" se o arquivo deletou do HD
                    rect_vazio = pygame.Rect(0, 0, 280, 390)
                    rect_vazio.center = (self.cx, self.cy + 20)
                    pygame.draw.rect(self.screen, (40, 40, 40), rect_vazio, border_radius=10)
                    pygame.draw.rect(self.screen, colors.INPUT_BORDER, rect_vazio, 2, border_radius=10)
                    Label("Arte Indisponível", (self.cx, self.cy + 20), self.fontes['status'], colors.TEXT_SEC).draw(self.screen)
            
            # Desenha os botões do carrossel e o botão jogar
            self.btn_prev.draw(self.screen)
            self.btn_next.draw(self.screen)
            self.btn_jogar.draw(self.screen)