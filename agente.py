import numpy as np
from collections import deque

class Colores:
    RESET = "\033[0m"
    NEGRO = "\033[30m"
    ROJO = "\033[31m"
    VERDE = "\033[32m"
    AMARILLO = "\033[33m"
    AZUL = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BLANCO = "\033[37m"
    ROJO_B = "\033[1;31m"
    VERDE_B = "\033[1;32m"
    AMARILLO_B = "\033[1;33m"
    AZUL_B = "\033[1;34m"
    MAGENTA_B = "\033[1;35m"
    CYAN_B = "\033[1;36m"
    BLANCO_B = "\033[1;37m"

class AgenteLogico:
    def __init__(self, size=6):
        self.n = size
        # Memoria
        self.casillas_visitadas = set()
        self.casillas_seguras = set()
        self.brisas = set()
        self.ronquidos = set()
        self.resplandores = set()
        self.ha_visto_luz = False
        
        # Deducciones
        self.pozos_posibles = set()
        self.pozos_seguros = set()
        self.soldado_posible = set()
        self.soldado_seguro = set()
        self.salida_posible = set((r, c) for r in range(size) for c in range(size))
        self.salida_segura = None 
        
        # Estado
        self.tengo_a_kurtz = False
        self.kurtz_ubicacion_conocida = None # Si lo pisamos o deducimos

    def razonar(self, posicion_actual, perceptos):
        r, c = posicion_actual
        self.casillas_visitadas.add(posicion_actual)
        self.casillas_seguras.add(posicion_actual)
        
        # Limpieza de zona segura
        self.pozos_posibles.discard(posicion_actual)
        self.soldado_posible.discard(posicion_actual)
        
        # Extracción de perceptos
        tiene_brisa = perceptos[0]
        tiene_ronquido = perceptos[1]
        tiene_resplandor = perceptos[2]
        escucha_grito = perceptos[7]
        
        adyacentes = self._obtener_adyacentes(r, c)
        
        # --- LÓGICA SALIDA ---
        zona_foco = set(adyacentes)
        zona_foco.add(posicion_actual)
        if tiene_resplandor:
            self.ha_visto_luz = True
            self.resplandores.add(posicion_actual)
            self.salida_posible &= zona_foco
        else:
            self.salida_posible -= zona_foco
            
        if len(self.salida_posible) == 1:
            self.salida_segura = list(self.salida_posible)[0]
        
        # --- LÓGICA PELIGROS ---
        if escucha_grito:
            self.soldado_posible.clear()
            self.soldado_seguro.clear()
        
        if tiene_brisa:
            self.brisas.add(posicion_actual)
            for v in adyacentes:
                if v not in self.casillas_seguras and v not in self.pozos_seguros:
                    self.pozos_posibles.add(v)
        else:
            for v in adyacentes:
                self.pozos_posibles.discard(v)
                self.pozos_seguros.discard(v)
        
        if tiene_ronquido and not escucha_grito:
            self.ronquidos.add(posicion_actual)
            for v in adyacentes:
                if v not in self.casillas_seguras and v not in self.soldado_seguro:
                    self.soldado_posible.add(v)
        elif not tiene_ronquido:
            for v in adyacentes:
                self.soldado_posible.discard(v)
                self.soldado_seguro.discard(v)

        self._inferir_trampas(self.brisas, self.pozos_seguros, self.pozos_posibles)
        self._inferir_trampas(self.ronquidos, self.soldado_seguro, self.soldado_posible)
        self._actualizar_seguras_globales(adyacentes, tiene_brisa, tiene_ronquido)

    def _inferir_trampas(self, perceptos_origen, set_seguros, set_posibles):
        for (r, c) in perceptos_origen:
            vecinos = self._obtener_adyacentes(r, c)
            candidatos = [v for v in vecinos if v not in self.casillas_seguras]
            if len(candidatos) == 1:
                culpable = candidatos[0]
                set_seguros.add(culpable)
                if culpable in set_posibles: set_posibles.remove(culpable)

    def _actualizar_seguras_globales(self, adyacentes, brisa, ronquido):
        if not brisa and not ronquido:
            for v in adyacentes: self.casillas_seguras.add(v)

    def _obtener_adyacentes(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    # =========================================================================
    #                   MOTOR DE BÚSQUEDA Y DECISIÓN (AUTO)
    # =========================================================================

    def decidir_accion_automatica(self, pos_actual, algoritmo="BFS"):
        """
        Calcula la siguiente acción basada en el estado actual y el algoritmo elegido.
        Retorna: 'w', 'a', 's', 'd', 'e', 'g...', o None (si está atascado)
        """
        
        # 1. ¿Tengo que matar al soldado? (Prioridad de Supervivencia)
        # Si hay un soldado confirmado al lado, lanzamos granada.
        adyacentes = self._obtener_adyacentes(*pos_actual)
        for vecino in adyacentes:
            if vecino in self.soldado_seguro:
                # Calcular dirección
                dr, dc = vecino[0] - pos_actual[0], vecino[1] - pos_actual[1]
                dir_char = ""
                if dr == -1: dir_char = 'w'
                elif dr == 1: dir_char = 's'
                elif dc == -1: dir_char = 'a'
                elif dc == 1: dir_char = 'd'
                return 'g' + dir_char

        # 2. Definir OBJETIVO
        meta = None
        tipo_meta = ""

        # A) Si tengo a Kurtz -> Voy a la Salida
        if self.tengo_a_kurtz:
            if self.salida_segura:
                meta = self.salida_segura
                tipo_meta = "SALIDA"
            else:
                # Tengo a Kurtz pero no sé dónde está la salida -> Explorar
                tipo_meta = "EXPLORAR (Con Kurtz)"
        
        # B) Si no tengo a Kurtz -> Voy a por Kurtz (si sé dónde está)
        elif self.kurtz_ubicacion_conocida:
            meta = self.kurtz_ubicacion_conocida
            tipo_meta = "RESCATAR KURTZ"
            
        # C) Si no tengo meta clara -> EXPLORAR (Buscar casilla segura no visitada)
        if meta is None:
            tipo_meta = "EXPLORAR"
            # La meta será determinada por el algoritmo (la más cercana)

        # 3. Ejecutar Algoritmo de Búsqueda
        siguiente_casilla = None
        
        if algoritmo == "BFS":
            siguiente_casilla = self._busqueda_bfs(pos_actual, meta)
        elif algoritmo == "DFS":
            siguiente_casilla = self._busqueda_dfs(pos_actual, meta)

        # 4. Traducir casilla a acción
        if siguiente_casilla:
            # Si la siguiente casilla es la salida y tengo a Kurtz, SALIR
            if siguiente_casilla == pos_actual and self.tengo_a_kurtz and pos_actual == self.salida_segura:
                return 'e'
            if siguiente_casilla == pos_actual: # Ya estoy en la meta (ej. acabamos de llegar a la salida)
                 return 'e' if (pos_actual == self.salida_segura and self.tengo_a_kurtz) else None

            dr = siguiente_casilla[0] - pos_actual[0]
            dc = siguiente_casilla[1] - pos_actual[1]
            if dr == -1: return 'w'
            if dr == 1: return 's'
            if dc == -1: return 'a'
            if dc == 1: return 'd'
        
        # Caso especial: Estamos en la salida con Kurtz pero el algoritmo devolvió la propia casilla
        if self.tengo_a_kurtz and self.salida_segura == pos_actual:
            return 'e'

        return None # Atascado

    def _busqueda_bfs(self, inicio, meta_concreta=None):
        """
        Búsqueda en Anchura.
        Si meta_concreta es None, busca la casilla 'segura no visitada' más cercana.
        Retorna la COORDENADA del primer paso a dar.
        """
        cola = deque([(inicio, [])]) # (posicion_actual, camino_hasta_aqui)
        visitados_bfs = {inicio}

        while cola:
            (actual, camino) = cola.popleft()

            # Condición de éxito
            es_meta = False
            if meta_concreta:
                if actual == meta_concreta: es_meta = True
            else:
                # Modo Exploración: La meta es cualquier casilla segura no visitada
                # OJO: Excluimos la propia casilla inicial
                if actual not in self.casillas_visitadas and actual in self.casillas_seguras:
                    es_meta = True

            if es_meta:
                # Si el camino está vacío, significa que ya estamos en la meta
                if not camino: return actual
                return camino[0] # Retornamos el PRIMER paso del plan

            # Expansión (Solo por casillas SEGURAS)
            for vecino in self._obtener_adyacentes(*actual):
                if vecino not in visitados_bfs:
                    # REGLA DE ORO: Solo transitamos por casillas confirmadas como seguras
                    if vecino in self.casillas_seguras:
                        visitados_bfs.add(vecino)
                        cola.append((vecino, camino + [vecino]))
        return None

    def _busqueda_dfs(self, inicio, meta_concreta=None):
        """
        Búsqueda en Profundidad. Menos óptima, pero cumple requisitos académicos.
        """
        pila = [(inicio, [])]
        visitados_dfs = {inicio}

        while pila:
            (actual, camino) = pila.pop()

            es_meta = False
            if meta_concreta:
                if actual == meta_concreta: es_meta = True
            else:
                if actual not in self.casillas_visitadas and actual in self.casillas_seguras:
                    es_meta = True

            if es_meta:
                if not camino: return actual
                return camino[0]

            # En DFS el orden de expansión afecta mucho al camino.
            for vecino in self._obtener_adyacentes(*actual):
                if vecino not in visitados_dfs:
                    if vecino in self.casillas_seguras:
                        visitados_dfs.add(vecino)
                        pila.append((vecino, camino + [vecino]))
        return None

    # =========================================================================

    def imprimir_mapa_mental(self, pos_capitan, tiene_kurtz):
        self.tengo_a_kurtz = tiene_kurtz
        # Si encontramos a Kurtz (lo pisamos), guardamos su ubicación
        if tiene_kurtz: 
            self.kurtz_ubicacion_conocida = pos_capitan # Ya va con nosotros
        elif not self.kurtz_ubicacion_conocida and pos_capitan in self.casillas_visitadas:
             # Nota: La lógica real de encontrar a Kurtz viene del entorno, 
             # pero aquí asumimos que si visitamos una celda segura y no morimos, la exploramos.
             pass

        print("\n--- MAPA MENTAL (Deducción + Búsqueda) ---")
        
        # --- LEYENDA ACTUALIZADA ---
        print("LEYENDA:")
        print(f"| {Colores.AZUL_B}[CW]{Colores.RESET}: Tú | {Colores.CYAN_B}[CW+K]{Colores.RESET}: Con Kurtz | {Colores.BLANCO_B}[E!]{Colores.RESET}: Salida | {Colores.BLANCO}[E?]{Colores.RESET}: Posible Salida |")
        print(f"| {Colores.ROJO_B}[P!]{Colores.RESET}: Precipicio | {Colores.ROJO_B}[S!]{Colores.RESET}: Soldado | {Colores.AMARILLO}[P/S?]{Colores.RESET}: Peligros Posibles |")
        print(f"| {Colores.MAGENTA}[B/R/L]{Colores.RESET}: Perceptos | {Colores.VERDE}[ok]{Colores.RESET}: Seguro | {Colores.NEGRO}[#]{Colores.RESET}: Desconocido |")
        print("-" * 60)

        for r in range(self.n):
            fila_str = ""
            for c in range(self.n):
                pos = (r, c)
                texto = " # "
                color = Colores.RESET 
                
                # --- 1. JUGADOR ---
                if pos == pos_capitan:
                    texto = "CW+K" if self.tengo_a_kurtz else "CW"
                    color = Colores.CYAN_B if self.tengo_a_kurtz else Colores.AZUL_B
                
                # --- 2. CERTEZAS ---
                elif self.salida_segura == pos: 
                    texto = "E!"
                    color = Colores.BLANCO_B
                elif pos in self.pozos_seguros:
                    texto = "P!"
                    color = Colores.ROJO_B
                elif pos in self.soldado_seguro:
                    texto = "S!"
                    color = Colores.ROJO_B

                # --- 3. INCERTIDUMBRES ---
                elif (pos in self.pozos_posibles or 
                      pos in self.soldado_posible or 
                      (self.ha_visto_luz and pos in self.salida_posible)):
                    
                    posibilidades = []
                    if pos in self.pozos_posibles: posibilidades.append("P")
                    if pos in self.soldado_posible: posibilidades.append("S")
                    if self.ha_visto_luz and pos in self.salida_posible: posibilidades.append("E")
                    
                    if len(posibilidades) == 3: texto = "All?"
                    else: texto = "/".join(posibilidades) + "?"
                    
                    if "P" in posibilidades or "S" in posibilidades: color = Colores.AMARILLO
                    else: color = Colores.BLANCO
                
                # --- 4. MEMORIA ---
                elif pos in self.casillas_visitadas:
                    info = []
                    if pos in self.brisas: info.append("B")
                    if pos in self.ronquidos: info.append("R")
                    if pos in self.resplandores: info.append("L")
                    
                    if not info: 
                        texto = "ok"
                        color = Colores.VERDE
                    else:
                        texto = "".join(info)
                        color = Colores.MAGENTA

                # --- 5. SEGURAS ---
                elif pos in self.casillas_seguras:
                    texto = "ok"
                    color = Colores.VERDE

                celda_formateada = f"[{texto:^4}]"
                fila_str += f"{color}{celda_formateada}{Colores.RESET}"
                
            print(fila_str)
        
        if self.salida_segura:
            print(f"-> {Colores.BLANCO_B}¡DEDUCCIÓN: La salida ESTÁ en {self.salida_segura}!{Colores.RESET}")
        elif self.ha_visto_luz:
            print(f"-> {Colores.BLANCO}Pista de Luz encontrada.{Colores.RESET} Candidatos a Salida: {len(self.salida_posible)}")
        print("------------------------------\n")