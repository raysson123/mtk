import threading
import time
from datetime import datetime

class DeckRegisterController:
    def __init__(self, scryfall_service, deck_repo, profile_repo, image_downloader):
        self.scryfall = scryfall_service
        self.deck_repo = deck_repo
        self.profile_repo = profile_repo
        self.image_downloader = image_downloader 
        
        self.estado = "INICIAL"
        self.progresso = 0
        self.carta_atual_nome = ""
        self.nome_deck_temp = ""
        self.mensagem_erro = "" 
        
        self.cartas_processadas = []
        self.lendas_encontradas = []
        self.index_lenda = 0

    def limpar_dados(self):
        """Zera todos os resquícios da memória e volta ao estado zero."""
        self.estado = "INICIAL"
        self.progresso = 0
        self.carta_atual_nome = ""
        self.nome_deck_temp = ""
        self.mensagem_erro = ""
        
        # O .clear() força o Python a liberar a memória RAM dessas listas
        self.cartas_processadas.clear()
        self.lendas_encontradas.clear()
        self.index_lenda = 0

    def iniciar_analise(self, nome_deck, linhas_txt):
        """Inicia a análise puramente textual em background."""
        self.limpar_dados() # Garante que está limpo antes de começar
        self.nome_deck_temp = nome_deck if nome_deck else "Novo Deck"
        self.estado = "ANALISANDO" # Ativa a Barra Circular
        
        thread = threading.Thread(target=self._processar_lista_batch, args=(linhas_txt,))
        thread.daemon = True 
        thread.start()

    def _processar_lista_batch(self, linhas):
        """Processamento ultra-rápido: Apenas textos e URLs."""
        time.sleep(0.5) 
        try:
            linhas_validas = [l.strip() for l in linhas if l.strip()]
            if not linhas_validas:
                self.mensagem_erro = "Arquivo TXT vazio ou inválido."
                self.estado = "INICIAL"
                return

            nomes_lista = []
            mapa_quantidades = {}
            total_cartas_txt = 0

            for linha in linhas_validas:
                partes = linha.split(' ', 1)
                qtd = int(partes[0]) if partes[0].isdigit() else 1
                nome = partes[1] if partes[0].isdigit() else linha
                nomes_lista.append(nome)
                mapa_quantidades[nome] = qtd
                total_cartas_txt += qtd

            # VALIDAÇÃO DO COMMANDER (100 Cartas)
            if total_cartas_txt != 100:
                print(f"[AVISO] O deck tem {total_cartas_txt} cartas. O formato Commander exige 100.")
                self.mensagem_erro = f"Deck inválido: {total_cartas_txt}/100 cartas."

            self.progresso = 10
            self.carta_atual_nome = "Consultando Scryfall (Textos)..."

            cartas_retornadas = []
            for i in range(0, len(nomes_lista), 75):
                lote = nomes_lista[i:i+75]
                resultados = self.scryfall.buscar_lote_cartas(lote)
                if resultados:
                    cartas_retornadas.extend(resultados)
                self.progresso = 20 + int((i / len(nomes_lista)) * 60)

            for dados in cartas_retornadas:
                if not dados or not isinstance(dados, dict): continue
                
                nome_card = dados.get('name', 'Desconhecido')
                self.carta_atual_nome = nome_card
                dados['quantity'] = mapa_quantidades.get(nome_card, 1)
                
                self.cartas_processadas.append(dados)

                type_line = dados.get('type_line', '')
                if "Legendary" in type_line and "Creature" in type_line:
                    self.lendas_encontradas.append({
                        "name": nome_card,
                        "url_temp": dados.get('image_url')
                    })

            self.progresso = 100
            
            if not self.lendas_encontradas:
                self.mensagem_erro = "Nenhuma criatura lendária encontrada para ser Comandante."
                self.estado = "INICIAL"
            else:
                self.estado = "SELECAO"
            
        except Exception as e:
            print(f"Erro no processamento: {e}")
            self.mensagem_erro = "Erro crítico ao processar o arquivo .txt"
            self.estado = "INICIAL"

    def obter_comandante_atual(self):
        if self.lendas_encontradas and self.index_lenda < len(self.lendas_encontradas):
            return self.lendas_encontradas[self.index_lenda]
        return None

    def navegar_lendas(self, direcao):
        if self.lendas_encontradas:
            self.index_lenda = (self.index_lenda + direcao) % len(self.lendas_encontradas)

    def _estruturar_dados_offline(self, deck_final):
        """Executa o ImageDownloader em background e reporta o progresso linear."""
        cartas_estruturadas = []
        total_cartas = len(deck_final['cards'])
        
        for index, carta_data in enumerate(deck_final['cards']):
            # Atualiza para a View saber o que escrever embaixo da barra
            self.carta_atual_nome = carta_data.get('name', 'Desconhecido')
            
            # Atualiza a porcentagem de 0 a 100
            self.progresso = int(((index + 1) / total_cartas) * 100)
            
            dados_locais = self.image_downloader.garantir_imagem_e_dados(carta_data)
            if dados_locais:
                cartas_estruturadas.append(dados_locais)
        
        deck_final['cards'] = cartas_estruturadas
        
        # Salva fisicamente
        self.deck_repo.salvar_deck_físico(deck_final)
        self.profile_repo.adicionar_referencia_deck(deck_final)
        
        print(f"\n[SISTEMA] Estruturação offline do deck '{deck_final['name']}' concluída!")
        
        # GATILHO FINAL: A View está esperando por isso para fechar a tela!
        self.estado = "CONCLUIDO"

    def finalizar_registro(self):
        """Muda o estado para SALVANDO e inicia a thread do backup."""
        comandante = self.obter_comandante_atual()
        if not comandante: return False
        
        total_cartas = sum(c.get('quantity', 1) for c in self.cartas_processadas)
        
        try:
            deck_final = {
                "name": self.nome_deck_temp,
                "commander": comandante['name'],
                "commander_url": comandante['url_temp'], 
                "total_cards": total_cartas,
                "cards": self.cartas_processadas, 
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }

            # Prepara a tela para exibir a Barra Linear
            self.estado = "SALVANDO"
            self.progresso = 0
            self.carta_atual_nome = "Iniciando estruturação..."
            
            # Dispara a thread de I/O pesado
            thread_offline = threading.Thread(target=self._estruturar_dados_offline, args=(deck_final,))
            thread_offline.daemon = True
            thread_offline.start()
            
            return True
            
        except Exception as e:
            print(f"Erro ao finalizar registro: {e}")
            self.mensagem_erro = "Erro ao salvar o deck no banco de dados."
            self.estado = "SELECAO" # Devolve para a tela de escolha em caso de falha
            
        return False