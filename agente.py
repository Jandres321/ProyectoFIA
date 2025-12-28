import numpy as np

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
    
    # Variantes brillantes (Bold/Bright)
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
        
        # --- MEMORIA DEL AGENTE ---
        self.casillas_visitadas = set()
        self.casillas_seguras = set()
        
        # Percepciones guardadas
        self.brisas = set()
        self.ronquidos = set()
        self.resplandores = set()
        self.ha_visto_luz = False # <--- NUEVO: Controla cuándo empezar a mostrar E?
        
        # Deducciones de PELIGROS
        self.pozos_posibles = set()
        self.pozos_seguros = set()
        
        self.soldado_posible = set()
        self.soldado_seguro = set()

        # Deducciones de OBJETIVOS
        # Al principio, la salida podría estar en cualquier parte
        self.salida_posible = set((r, c) for r in range(size) for c in range(size))
        self.salida_segura = None 
        self.tengo_a_kurtz = False # Nuevo estado interno del agente para visualización

    def razonar(self, posicion_actual, perceptos):
        """
        perceptos = [Brisa, Ronquido, Resplandor, ParedN, ParedE, ParedS, ParedW, Grito]
        """
        r, c = posicion_actual
        self.casillas_visitadas.add(posicion_actual)
        self.casillas_seguras.add(posicion_actual)
        
        self.pozos_posibles.discard(posicion_actual)
        self.soldado_posible.discard(posicion_actual)
        
        tiene_brisa = perceptos[0]
        tiene_ronquido = perceptos[1]
        tiene_resplandor = perceptos[2]
        escucha_grito = perceptos[7]
        
        adyacentes = self._obtener_adyacentes(r, c)
        
        # --- LÓGICA DE LA SALIDA (RESPLANDOR) ---
        zona_foco = set(adyacentes)
        zona_foco.add(posicion_actual)
        
        if tiene_resplandor:
            self.ha_visto_luz = True # <--- Activamos el flag visual
            self.resplandores.add(posicion_actual)
            # La salida tiene que estar en la zona de foco
            self.salida_posible &= zona_foco
        else:
            # La salida NO puede estar en la zona de foco
            self.salida_posible -= zona_foco
            
        if len(self.salida_posible) == 1:
            self.salida_segura = list(self.salida_posible)[0]
        
        # --- LÓGICA DE GRITO ---
        if escucha_grito:
            self.soldado_posible.clear()
            self.soldado_seguro.clear()
        
        # --- LÓGICA DE PRECIPICIOS ---
        if tiene_brisa:
            self.brisas.add(posicion_actual)
            for vecino in adyacentes:
                if vecino not in self.casillas_seguras and vecino not in self.pozos_seguros:
                    self.pozos_posibles.add(vecino)
        else:
            for vecino in adyacentes:
                self.pozos_posibles.discard(vecino)
                self.pozos_seguros.discard(vecino)
        
        # --- LÓGICA DEL SOLDADO ---
        if tiene_ronquido and not escucha_grito:
            self.ronquidos.add(posicion_actual)
            for vecino in adyacentes:
                if vecino not in self.casillas_seguras and vecino not in self.soldado_seguro:
                    self.soldado_posible.add(vecino)
        elif not tiene_ronquido:
            for vecino in adyacentes:
                self.soldado_posible.discard(vecino)
                self.soldado_seguro.discard(vecino)

        # Inferencias fuertes
        self._inferir_trampas(tipo="PRECIPICIO")
        self._inferir_trampas(tipo="SOLDADO")
        self._actualizar_seguras_globales(adyacentes, tiene_brisa, tiene_ronquido)

    def _inferir_trampas(self, tipo):
        origen_percepto = self.brisas if tipo == "PRECIPICIO" else self.ronquidos
        set_seguros = self.pozos_seguros if tipo == "PRECIPICIO" else self.soldado_seguro
        set_posibles = self.pozos_posibles if tipo == "PRECIPICIO" else self.soldado_posible
        
        for (r, c) in origen_percepto:
            vecinos = self._obtener_adyacentes(r, c)
            candidatos = [v for v in vecinos if v not in self.casillas_seguras]
            if len(candidatos) == 1:
                culpable = candidatos[0]
                set_seguros.add(culpable)
                if culpable in set_posibles:
                    set_posibles.remove(culpable)

    def _actualizar_seguras_globales(self, adyacentes_actuales, brisa, ronquido):
        if not brisa and not ronquido:
            for v in adyacentes_actuales:
                self.casillas_seguras.add(v)

    def _obtener_adyacentes(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    def imprimir_mapa_mental(self, pos_capitan, tiene_kurtz):
        self.tengo_a_kurtz = tiene_kurtz 
        
        print("\n--- MAPA MENTAL (Deducción) ---")
        
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
                
                # --- 1. JUGADOR (Prioridad Máxima) ---
                if pos == pos_capitan:
                    texto = "CW+K" if self.tengo_a_kurtz else "CW"
                    color = Colores.CYAN_B if self.tengo_a_kurtz else Colores.AZUL_B
                
                # --- 2. CERTEZAS (Objetos confirmados) ---
                elif self.salida_segura == pos: 
                    texto = "E!"
                    color = Colores.BLANCO_B # CAMBIO: Blanco Brillante (Luz)
                elif pos in self.pozos_seguros:
                    texto = "P!"
                    color = Colores.ROJO_B
                elif pos in self.soldado_seguro:
                    texto = "S!"
                    color = Colores.ROJO_B

                # --- 3. INCERTIDUMBRES Y POSIBILIDADES (El arreglo clave) ---
                # Verificamos si la casilla es candidata a ALGO (Pozo, Soldado o Salida)
                elif (pos in self.pozos_posibles or 
                      pos in self.soldado_posible or 
                      (self.ha_visto_luz and pos in self.salida_posible)):
                    
                    # Construimos una lista de posibilidades para esta celda
                    posibilidades = []
                    if pos in self.pozos_posibles: posibilidades.append("P")
                    if pos in self.soldado_posible: posibilidades.append("S")
                    if self.ha_visto_luz and pos in self.salida_posible: posibilidades.append("E")
                    
                    # Generamos el texto combinado (Ej: "P/S?")
                    if len(posibilidades) == 3:
                        texto = "All?" # Si puede ser todo, abreviamos
                    else:
                        texto = "/".join(posibilidades) + "?"
                    
                    # Lógica de Color para incertidumbre
                    if "P" in posibilidades or "S" in posibilidades:
                        color = Colores.AMARILLO # Si hay peligro posible -> Amarillo
                    else:
                        color = Colores.BLANCO # Si solo es posible salida -> Blanco normal
                
                # --- 4. MEMORIA / PERCEPTOS ---
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

                # --- 5. SEGURAS DEDUCIDAS ---
                elif pos in self.casillas_seguras:
                    texto = "ok"
                    color = Colores.VERDE

                # Renderizado
                celda_formateada = f"[{texto:^4}]"
                fila_str += f"{color}{celda_formateada}{Colores.RESET}"
                
            print(fila_str)
        
        if self.salida_segura:
            print(f"-> {Colores.BLANCO_B}¡DEDUCCIÓN: La salida ESTÁ en {self.salida_segura}!{Colores.RESET}")
        elif self.ha_visto_luz:
            print(f"-> {Colores.BLANCO}Pista de Luz encontrada.{Colores.RESET} Candidatos a Salida: {len(self.salida_posible)}")
        
        print("------------------------------\n")