import pygame
import sys
# O Python agora encontrará 'APP' pois estamos na raiz do projeto
from APP.controllers.app_controller import AppController
from APP.infrastructure.storage.profile_repository import ProfileRepository

def main():
    # 1. Inicializa o Pygame
    pygame.init()
    
    # 2. Configurações de Janela (Pode usar seu settings.py aqui)
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Machete MTG Simulator")

    # 3. Inicializa a Infraestrutura
    # O ProfileRepository gerencia o profiler.json em data/profiles/
    profile_repo = ProfileRepository()

    # 4. Inicializa o Controlador Geral (Maestro)
    # Passamos o repo para ele distribuir aos sub-controladores
    app = AppController(screen, profile_repo)
    
    # 5. Roda o jogo
    app.run()

if __name__ == "__main__":
    main()