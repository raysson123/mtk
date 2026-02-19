import pygame
from APP.UI.screens.base_screens import BaseScreen
from APP.UI.styles.colors import BG, TEXT_PRIMARY, TEXT_SEC
from APP.UI.styles.fonts import get_fonts
from APP.UI.components.card_ui import CardUI
from APP.UI.components.zone_ui import ZoneUI

class MatchView(BaseScreen):
    def __init__(self, screen, controller, asset_manager): 
        """
        Visualização da Partida orquestrando os componentes ZoneUI e CardUI.
        """
        super().__init__(screen, controller)
        self.asset_manager = asset_manager 
        
        self.largura, self.altura = self.screen.get_size()
        self.fontes = get_fonts()
        
        self.match = self.controller.match_model
        
        self.card_w = 70
        self.card_h = 100
        
        # 1. Dicionário para guardar as Zonas de Jogo instanciadas
        self.zonas = {}
        
        # 2. Inicializa as zonas uma única vez para evitar sobrecarga
        self._inicializar_zonas()

        # Lista de componentes das cartas na Mão (para checar cliques)
        self.mao_ui = []

    def _inicializar_zonas(self):
        """Cria os componentes ZoneUI para cada jogador, com seus layouts."""
        jogadores_ids = list(self.match.players.keys())
        qtd_jogadores = len(jogadores_ids)
        
        for index, p_id in enumerate(jogadores_ids):
            id_visual = index + 1
            rect_area = self._get_area_jogador(id_visual, qtd_jogadores)
            
            w_zona = rect_area.width * 0.22
            h_top = rect_area.height * 0.45
            
            # --- Instancia as Zonas para este jogador ---
            # 1. Comandante (Layout: Stack)
            r_cmd = pygame.Rect(rect_area.x + 5, rect_area.y + 35, w_zona - 10, h_top - 40)
            z_cmd = ZoneUI(r_cmd, "COMANDANTE", (45, 45, 70), "stack")
            
            # 2. Mana/Terrenos (Layout: Overlap/Cascata)
            r_mana = pygame.Rect(rect_area.x + 5, rect_area.bottom - (rect_area.height * 0.35), w_zona - 10, (rect_area.height * 0.35) - 10)
            z_mana = ZoneUI(r_mana, "MANA", (30, 50, 30), "overlap")
            
            # 3. Cemitério (Layout: Stack)
            r_grave = pygame.Rect(rect_area.right - w_zona + 5, rect_area.y + 35, w_zona - 10, h_top - 40)
            z_grave = ZoneUI(r_grave, "CEMITÉRIO", (40, 30, 30), "stack")
            
            # 4. Campo de Batalha Principal (Criaturas - Layout: Grid)
            r_battle = pygame.Rect(r_cmd.right + 10, rect_area.y + 35, rect_area.width - (w_zona * 2) - 20, h_top - 40)
            z_battle = ZoneUI(r_battle, "CAMPO DE BATALHA", (40, 45, 40), "grid")

            self.zonas[p_id] = {
                "COMANDANTE": z_cmd,
                "MANA": z_mana,
                "CEMITERIO": z_grave,
                "CAMPO": z_battle
            }

    def _get_area_jogador(self, id_visual, qtd):
        w, h = self.largura, self.altura
        if qtd <= 2:
            if id_visual == 2: return pygame.Rect(0, 0, w, h // 2)      
            if id_visual == 1: return pygame.Rect(0, h // 2, w, h // 2) 
        return pygame.Rect(0, 0, w, h)

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        # Atualiza os componentes visuais da mão
        for card_ui in self.mao_ui:
            card_ui.update(mouse_pos)

        for event in events:
            if event.type == pygame.QUIT:
                return "SAIR"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if event.key == pygame.K_d:
                    self.controller.draw_card("P1", 1) 

            # NOVO: Lógica de clique baseada no CardUI
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, card_ui in enumerate(self.mao_ui):
                    if card_ui.is_clicked(event):
                        card = card_ui.card
                        if card.is_land:
                            self.controller.play_land("P1", i)
                        elif card.is_creature:
                            self.controller.cast_creature("P1", i)
                        else:
                            self.controller.cast_other("P1", i)
                        break # Se clicou numa carta, não precisa testar as outras
                        
        return None

    def draw(self):
        self.screen.fill(BG)
        
        jogadores_ids = list(self.match.players.keys())
        qtd_jogadores = len(jogadores_ids)
        
        for index, p_id in enumerate(jogadores_ids):
            id_visual = index + 1 
            self._atualizar_e_desenhar_jogador(p_id, id_visual, qtd_jogadores)

    def _atualizar_e_desenhar_jogador(self, p_id_banco, id_visual, qtd_jogadores):
        player = self.match.players[p_id_banco]
        eh_humano = (id_visual == 1)
        rect_area = self._get_area_jogador(id_visual, qtd_jogadores)

        # 1. Desenha o fundo da área do jogador
        cor_fundo = (30, 30, 45) if eh_humano else (25, 25, 35)
        pygame.draw.rect(self.screen, cor_fundo, rect_area)
        pygame.draw.rect(self.screen, (100, 100, 120), rect_area, 2) 

        # 2. Informações de Vida
        info_txt = f"{player.name} | {player.life} PV"
        txt = self.fontes['label'].render(info_txt, True, TEXT_PRIMARY)
        self.screen.blit(txt, (rect_area.centerx - txt.get_width()//2, rect_area.y + 5))

        # 3. Pega as zonas deste jogador
        zonas_do_jogador = self.zonas[p_id_banco]

        # 4. Sincroniza os Modelos (CardModel) com as Zonas (CardUI)
        
        # --- COMANDANTE ---
        zonas_do_jogador["COMANDANTE"].clear_cards()
        if player.deck.commander_card:
            card_ui = CardUI(player.deck.commander_card, self.asset_manager, 0, 0, 50, 70)
            zonas_do_jogador["COMANDANTE"].add_card_ui(card_ui)
        zonas_do_jogador["COMANDANTE"].draw(self.screen)

        # --- MANA/TERRENOS ---
        zonas_do_jogador["MANA"].clear_cards()
        for land_card in player.battlefield_lands:
            card_ui = CardUI(land_card, self.asset_manager, 0, 0, 40, 56)
            zonas_do_jogador["MANA"].add_card_ui(card_ui)
        zonas_do_jogador["MANA"].draw(self.screen)

        # --- CEMITÉRIO ---
        zonas_do_jogador["CEMITERIO"].clear_cards()
        if player.graveyard:
            card_ui = CardUI(player.graveyard[-1], self.asset_manager, 0, 0, 50, 70)
            zonas_do_jogador["CEMITERIO"].add_card_ui(card_ui)
        zonas_do_jogador["CEMITERIO"].draw(self.screen)
        
        # --- CAMPO DE BATALHA ---
        zonas_do_jogador["CAMPO"].clear_cards()
        for creature in player.battlefield_creatures:
            card_ui = CardUI(creature, self.asset_manager, 0, 0, 50, 70)
            zonas_do_jogador["CAMPO"].add_card_ui(card_ui)
        zonas_do_jogador["CAMPO"].draw(self.screen)

        # 5. Renderiza a Mão
        if eh_humano:
            self._renderizar_mao(player.hand, rect_area)
        else:
            txt_mao = self.fontes['label'].render(f"Cartas na Mão: {len(player.hand)}", True, TEXT_SEC)
            self.screen.blit(txt_mao, (rect_area.centerx - txt_mao.get_width()//2, rect_area.bottom - 40))

    def _renderizar_mao(self, hand_models, rect_area):
        qtd = len(hand_models)
        if qtd == 0: 
            self.mao_ui.clear()
            return

        espacamento = 5
        largura_total_mao = qtd * (self.card_w + espacamento)
        
        if largura_total_mao > rect_area.width * 0.7:
            espacamento = - (largura_total_mao - rect_area.width * 0.7) // qtd

        start_x = rect_area.centerx - (largura_total_mao // 2)
        y = rect_area.bottom - self.card_h - 15

        # Recria a lista de UI da mão para refletir as posições atuais
        self.mao_ui.clear()
        
        for i, card_obj in enumerate(hand_models):
            x = start_x + (i * (self.card_w + espacamento))
            
            card_ui = CardUI(card_obj, self.asset_manager, x, y, self.card_w, self.card_h)
            self.mao_ui.append(card_ui)
            
            # Desenha com os highlights dinâmicos do CardUI
            card_ui.draw(self.screen)