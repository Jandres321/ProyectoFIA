import numpy as np

class AgenteLogico:
    def __init__(self, size=6):
        self.n = size
        
        # --- MEMORIA DEL AGENTE ---
        self.casillas_visitadas = set() # Casillas seguras donde ya hemos pisado (OK)
        self.casillas_seguras = set()   # Casillas deducidas como seguras (aunque no visitadas)
        
        # Percepciones guardadas
        self.brisas = set()    # Donde sentimos brisa
        self.ronquidos = set() # Donde escuchamos ronquidos
        
        # Deducciones
        self.pozos_posibles = set()   # Candidatos a ser pozo (P?)
        self.pozos_seguros = set()    # Pozos confirmados (P!)
        
        self.soldado_posible = set()  # Candidatos a soldado (S?)
        self.soldado_seguro = set()   # Soldado confirmado (S!)

    def razonar(self, posicion_actual, perceptos):
        """
        Recibe los perceptos actuales y actualiza la base de conocimiento.
        perceptos = [Brisa, Ronquido, ...]
        """
        r, c = posicion_actual
        self.casillas_visitadas.add(posicion_actual)
        self.casillas_seguras.add(posicion_actual)
        
        # Limpiar sospechas previas en la celda actual (si estoy vivo, aquí no hay nada)
        self.pozos_posibles.discard(posicion_actual)
        self.soldado_posible.discard(posicion_actual)
        
        tiene_brisa = perceptos[0]
        tiene_ronquido = perceptos[1]
        escucha_grito = perceptos[7] # Índice 7 es el Grito
        
        adyacentes = self._obtener_adyacentes(r, c)
        
        # --- LÓGICA DE GRITO ---
        if escucha_grito:
            # Si escuchamos un grito, el soldado ha muerto.
            # Borramos todas las sospechas de soldado del mapa.
            self.soldado_posible.clear()
            self.soldado_seguro.clear()
            # Nota: Como el soldado es único, al morir, sus casillas se vuelven seguras 
            # (si no hay precipicio, claro).

        # --- LÓGICA DE PRECIPICIOS ---
        if tiene_brisa:
            self.brisas.add(posicion_actual)
            # Si hay brisa, los vecinos NO visitados/seguros son sospechosos
            for vecino in adyacentes:
                if vecino not in self.casillas_seguras and vecino not in self.pozos_seguros:
                    self.pozos_posibles.add(vecino)
        else:
            # Si NO hay brisa, los vecinos son SEGUROS de precipicio
            for vecino in adyacentes:
                self.pozos_posibles.discard(vecino) # Ya no es sospechoso
                self.pozos_seguros.discard(vecino)  # Si pensábamos que era, nos equivocamos (o lógica anterior falló)
                # Nota: Saber que no es pozo no significa que sea transitable (podría ser soldado)
        
        # --- LÓGICA DEL SOLDADO ---
        # Solo procesamos ronquidos si NO acabamos de oír el grito (que implica muerte)
        if tiene_ronquido and not escucha_grito:
            self.ronquidos.add(posicion_actual)
            for vecino in adyacentes:
                if vecino not in self.casillas_seguras and vecino not in self.soldado_seguro:
                    self.soldado_posible.add(vecino)
        elif not tiene_ronquido:
            # Si no hay ronquido (o el soldado está muerto), limpiamos zona
            for vecino in adyacentes:
                self.soldado_posible.discard(vecino)
                self.soldado_seguro.discard(vecino)


        # --- MOTOR DE INFERENCIA (DEDUCCIÓN FUERTE) ---
        # Repasamos todas las brisas pasadas para ver si podemos confirmar algo
        self._inferir_trampas(tipo="PRECIPICIO")
        self._inferir_trampas(tipo="SOLDADO")
        
        # Actualizar casillas seguras globales
        self._actualizar_seguras_globales(adyacentes, tiene_brisa, tiene_ronquido)

    def _inferir_trampas(self, tipo):
        """
        Si en una casilla con Brisa solo queda 1 vecino que NO es seguro,
        ese vecino TIENE que ser el Precipicio.
        """
        origen_percepto = self.brisas if tipo == "PRECIPICIO" else self.ronquidos
        set_seguros = self.pozos_seguros if tipo == "PRECIPICIO" else self.soldado_seguro
        set_posibles = self.pozos_posibles if tipo == "PRECIPICIO" else self.soldado_posible
        
        for (r, c) in origen_percepto:
            vecinos = self._obtener_adyacentes(r, c)
            # Filtramos vecinos que ya sabemos que son seguros (libres de este peligro)
            candidatos = []
            for v in vecinos:
                # Un vecino es candidato si no lo hemos marcado como seguro respecto a este peligro
                # (Para simplificar, usamos casillas_seguras general, pero idealmente se separa)
                if v not in self.casillas_seguras:
                    candidatos.append(v)
            
            # LA DEDUCCIÓN CLAVE:
            if len(candidatos) == 1:
                culpable = candidatos[0]
                # ¡Confirmado!
                set_seguros.add(culpable)
                if culpable in set_posibles:
                    set_posibles.remove(culpable)

    def _actualizar_seguras_globales(self, adyacentes_actuales, brisa, ronquido):
        """Marca vecinos como seguros si no percibimos peligro."""
        if not brisa and not ronquido:
            # Si no hay nada, todos los vecinos son transitables (seguros)
            for v in adyacentes_actuales:
                self.casillas_seguras.add(v)
        
        # También, si un vecino era sospechoso pero ya no está en ninguna lista de posibles...
        # (Esta lógica se puede hacer más compleja, pero para empezar vale)

    def _obtener_adyacentes(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    def imprimir_mapa_mental(self, pos_capitan):
        """Dibuja lo que el agente SABE."""
        print("\n--- MAPA MENTAL DEL AGENTE ---")
        print("Leyenda: OK=Seguro visitado, #=Desconocido, B=Brisa, P?=Posible Pozo, P!=Pozo CONFIRMADO")
        
        for r in range(self.n):
            fila_str = ""
            for c in range(self.n):
                pos = (r, c)
                texto = " # " # Por defecto desconocido
                
                # Prioridad de visualización
                if pos == pos_capitan:
                    texto = "CW"
                elif pos in self.pozos_seguros:
                    texto = "P!"  # PELIGRO CONFIRMADO
                elif pos in self.soldado_seguro:
                    texto = "S!"
                elif pos in self.pozos_posibles:
                    texto = "P?"
                elif pos in self.soldado_posible:
                    texto = "S?"
                elif pos in self.casillas_visitadas:
                    # Si visitamos y hay brisa, mostramos B, si no OK
                    info = []
                    if pos in self.brisas: info.append("B")
                    if pos in self.ronquidos: info.append("R")
                    if not info: info.append("OK")
                    texto = "".join(info)
                elif pos in self.casillas_seguras:
                    texto = "ok" # Seguro no visitado
                
                fila_str += f"[{texto:^4}]"
            print(fila_str)
        print("------------------------------\n")