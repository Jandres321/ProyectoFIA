import numpy as np

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
        print("| [CW]: Tú | [CW+K]: Tú con Kurtz | [E!]: Salida Confirmada | [E?]: Salida Posible |")
        print("| [P!]: Precipicio | [S!]: Soldado | [P?]/[S?]: Peligro Posible |")
        print("| [B]: Brisa | [R]: Ronquido | [L]: Luz | [ok]: Seguro | [#]: Desconocido |")
        print("-" * 60)

        for r in range(self.n):
            fila_str = ""
            for c in range(self.n):
                pos = (r, c)
                texto = " # "
                
                # 1. POSICIÓN DEL JUGADOR (Jerarquía máxima)
                if pos == pos_capitan:
                    texto = "CW+K" if self.tengo_a_kurtz else "CW"
                
                # 2. OBJETIVOS CONFIRMADOS
                elif self.salida_segura == pos: 
                    texto = "E!" 

                # 3. PELIGROS CONFIRMADOS (Deducidos)
                elif pos in self.pozos_seguros:
                    texto = "P!"
                elif pos in self.soldado_seguro:
                    texto = "S!"

                # 4. INCERTIDUMBRES (Si hemos visto luz, mostramos E?)
                elif self.ha_visto_luz and pos in self.salida_posible:
                    # Conflictos de información (¿Puede ser pozo y salida a la vez?)
                    if pos in self.pozos_posibles:
                        texto = "P/E?"
                    elif pos in self.soldado_posible:
                        texto = "S/E?"
                    else:
                        texto = "E?"
                
                # 5. SOSPECHAS DE PELIGRO
                elif pos in self.pozos_posibles:
                    texto = "P?"
                elif pos in self.soldado_posible:
                    texto = "S?"
                
                # 6. MEMORIA DE CASILLAS VISITADAS (Perceptos históricos)
                elif pos in self.casillas_visitadas:
                    info = []
                    if pos in self.brisas: info.append("B")
                    if pos in self.ronquidos: info.append("R")
                    if pos in self.resplandores: info.append("L")
                    
                    if not info: 
                        texto = "ok" # Sin perceptos, totalmente segura
                    else:
                        texto = "".join(info) # Ej: "BR" (Brisa y Ronquido)

                # 7. CASILLAS DEDUCIDAS COMO SEGURAS (Pero no visitadas)
                elif pos in self.casillas_seguras:
                    texto = "ok"
                
                fila_str += f"[{texto:^4}]"
            print(fila_str)
        
        # Mensajes de estado debajo del mapa
        if self.salida_segura:
            print(f"-> ¡DEDUCCIÓN: La salida ESTÁ en {self.salida_segura}!")
        elif self.ha_visto_luz:
            print(f"-> Pista de Luz encontrada. Candidatos a Salida: {len(self.salida_posible)}")
        
        print("------------------------------\n")