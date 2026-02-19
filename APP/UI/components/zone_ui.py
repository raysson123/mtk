import pygame
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts

class ZoneUI:
    def __init__(self, rect: pygame.Rect, title: str, bg_color: tuple, layout_style: str = "overlap"):
        """
        Componente modular para as zonas do campo de batalha (Mana, Cemitério, Exílio, etc).
        :param layout_style: 'overlap' (cartas empilhadas, ex: Mana), 'grid' (lado a lado), 'stack' (uma em cima da outra, ex: Cemitério).
        """
        self.rect = rect
        self.title = title
        self.bg_color = bg_color
        self.layout_style = layout_style
        self.fontes = get_fonts()
        
        self.cards_ui = [] # Lista de componentes CardUI que estão dentro desta zona

    def clear_cards(self):
        """Limpa as cartas da zona para re-renderizar no frame atual."""
        self.cards_ui.clear()

    def add_card_ui(self, card_ui):
        """Adiciona um componente CardUI para ser desenhado nesta zona."""
        self.cards_ui.append(card_ui)

    def draw(self, screen):
        """Renderiza a caixa da zona, o título e organiza as cartas dentro dela."""
        # 1. Desenha o Fundo da Zona
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=5)
        
        # 2. Desenha a Borda
        pygame.draw.rect(screen, (60, 60, 80), self.rect, 1, border_radius=5)
        
        # 3. Desenha o Título no canto superior esquerdo
        txt = self.fontes['status'].render(self.title, True, (160, 160, 160))
        screen.blit(txt, (self.rect.x + 5, self.rect.y + 2))

        # Se não houver cartas, para por aqui
        if not self.cards_ui:
            return

        # 4. Lógica de Organização Visual (Layout)
        start_x = self.rect.x + 10
        start_y = self.rect.y + 25
        
        if self.layout_style == "overlap":
            # Estilo Zona de Mana: Cartas aparecem em cascata horizontalmente
            espacamento = 25 # Quantos pixels a próxima carta aparece do lado
            for i, card_ui in enumerate(self.cards_ui):
                # Limita para não vazar da caixa (se tiver muita mana, agrupa)
                max_x = self.rect.right - card_ui.rect.width - 10
                x_pos = min(start_x + (i * espacamento), max_x)
                
                card_ui.update_position(x_pos, start_y)
                card_ui.draw(screen)

        elif self.layout_style == "stack":
            # Estilo Cemitério/Comandante: Desenha apenas a carta do topo (a última da lista)
            top_card_ui = self.cards_ui[-1]
            # Centraliza a carta na zona
            cx = self.rect.centerx - (top_card_ui.rect.width // 2)
            top_card_ui.update_position(cx, start_y)
            top_card_ui.draw(screen)

        elif self.layout_style == "grid":
            # Estilo Campo de Batalha (Criaturas): Lado a lado com espaço
            espacamento = card_ui.rect.width + 10
            for i, card_ui in enumerate(self.cards_ui):
                # Calcula quebra de linha se passar da caixa
                max_cards_row = max(1, (self.rect.width - 20) // espacamento)
                row = i // max_cards_row
                col = i % max_cards_row
                
                x_pos = start_x + (col * espacamento)
                y_pos = start_y + (row * (card_ui.rect.height + 10))
                
                card_ui.update_position(x_pos, y_pos)
                card_ui.draw(screen)