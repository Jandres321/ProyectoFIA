import numpy as np
from agente import Colores

class AgenteBayesiano:
    def __init__(self, size=6):
        self.n = size
        # Matrices de Probabilidad (Heatmaps)
        # Inicializamos con 1/(N-1) salvo en (0,0) que es 0
        prob_inicial = 1.0 / ((size * size) - 1)
        
        self.P_fuego = np.full((size, size), prob_inicial)
        self.P_pinchos = np.full((size, size), prob_inicial)
        self.P_dardos = np.full((size, size), prob_inicial)
        self.P_soldado = np.full((size, size), prob_inicial)
        self.P_salida = np.full((size, size), prob_inicial)
        
        # La casilla (0,0) sabemos que es segura al inicio
        for M in [self.P_fuego, self.P_pinchos, self.P_dardos, self.P_soldado, self.P_salida]:
            M[0, 0] = 0.0
            
        self.tengo_a_kurtz = False

    def actualizar_creencias(self, pos_actual, perceptos):
        """
        perceptos: [Olor, Crujido, Cable, Ronquido, Resplandor, ...]
        Aplica Bayes para cada tipo de amenaza/objetivo independientemente.
        """
        # Desempaquetar perceptos de interés (booleanos)
        e_fuego = perceptos[0]
        e_pinchos = perceptos[1]
        e_dardos = perceptos[2]
        e_soldado = perceptos[3]
        e_salida = perceptos[4]
        grito = perceptos[9]
        
        # 1. Si escuchamos Grito, el soldado ya no existe (Prob = 0 en todo el mapa)
        if grito:
            self.P_soldado = np.zeros((self.n, self.n))
        else:
            # Actualizar Soldado
            self._aplicar_bayes(self.P_soldado, pos_actual, e_soldado)

        # 2. Actualizar Trampas
        self._aplicar_bayes(self.P_fuego, pos_actual, e_fuego)
        self._aplicar_bayes(self.P_pinchos, pos_actual, e_pinchos)
        self._aplicar_bayes(self.P_dardos, pos_actual, e_dardos)
        
        # 3. Actualizar Salida
        self._aplicar_bayes(self.P_salida, pos_actual, e_salida)
        
        # 4. Caso especial: Donde estoy YO ahora, la probabilidad de trampa es 0
        # (porque sigo vivo). Esto es una evidencia implícita fuerte.
        r, c = pos_actual
        self.P_fuego[r, c] = 0
        self.P_pinchos[r, c] = 0
        self.P_dardos[r, c] = 0
        if not grito: self.P_soldado[r, c] = 0 # Si estoy vivo, el soldado no estaba aquí (o dormía, pero simplificamos)

        # Normalizar de nuevo para asegurar que suman 1 (o aprox)
        self._normalizar(self.P_fuego)
        self._normalizar(self.P_pinchos)
        self._normalizar(self.P_dardos)
        if not grito: self._normalizar(self.P_soldado)
        self._normalizar(self.P_salida)

    def _aplicar_bayes(self, matriz_prob, pos_observador, percibe_estimulo):
        """
        P(Trampa_ij | Evidencia) = alpha * P(Evidencia | Trampa_ij) * P(Trampa_ij)
        """
        r, c = pos_observador
        zona = self._obtener_adyacentes_y_propia(r, c)
        
        for i in range(self.n):
            for j in range(self.n):
                # Likelihood P(e | celda_ij tiene trampa)
                # Es 1.0 si la celda (i,j) está en la zona de influencia del observador
                # Es 0.0 si la celda (i,j) está LEJOS del observador
                
                es_vecino = (i, j) in zona
                
                if percibe_estimulo:
                    # SI huele a fuego:
                    # - Si (i,j) es vecino, P(e|T) = 1 (podría ser el culpable)
                    # - Si (i,j) NO es vecino, P(e|T) = 0 (no puede ser el culpable, olería allí no aquí)
                    # ERROR COMÚN: Si huele a fuego AQUÍ, el fuego DEBE estar en uno de los vecinos.
                    # Un fuego en la otra punta del mapa NO produciría olor AQUÍ.
                    likelihood = 1.0 if es_vecino else 0.0
                else:
                    # NO huele a fuego:
                    # - Si (i,j) es vecino, P(no e|T) = 0 (IMPOSIBLE: si estuviera, olería)
                    # - Si (i,j) NO es vecino, P(no e|T) = 1 (Compatible: el fuego está lejos)
                    likelihood = 0.0 if es_vecino else 1.0
                
                # Actualizamos
                matriz_prob[i, j] *= likelihood

    def _normalizar(self, matriz):
        suma = np.sum(matriz)
        if suma > 0: matriz /= suma

    def _obtener_adyacentes_y_propia(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1), (r, c)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    # ----------------------------------------------------------------------
    #   Lógica de análisis y visualización del mapa de calor
    # ----------------------------------------------------------------------

    def _analizar_celda(self, r, c):
        p_f = self.P_fuego[r, c]
        p_p = self.P_pinchos[r, c]
        p_d = self.P_dardos[r, c]
        p_m = self.P_soldado[r, c]
        p_salida = self.P_salida[r, c]

        prob_supervivencia = (1-p_f) * (1-p_p) * (1-p_d) * (1-p_m)
        riesgo_total = 1.0 - prob_supervivencia
        
        if p_salida > 0.50: 
            return f"S{int(p_salida*100)}", Colores.BLANCO_B

        if riesgo_total < 0.05:
            return "ok", Colores.VERDE

        amenazas = {'F': p_f, 'P': p_p, 'D': p_d, 'M': p_m}
        tipo_dominante = max(amenazas, key=amenazas.get)
        prob_dominante = amenazas[tipo_dominante]

        if prob_dominante > 0.50:
            texto = f"{tipo_dominante}{int(prob_dominante*100)}"
            color = Colores.BLANCO
            
            if tipo_dominante == 'F': color = Colores.ROJO       
            elif tipo_dominante == 'P': color = Colores.COLOR_PINCHOS 
            elif tipo_dominante == 'D': color = Colores.COLOR_DARDOS 
            elif tipo_dominante == 'M': color = Colores.COLOR_SOLDADO 
            
            return texto, color

        texto = f"R{int(riesgo_total*100)}"
        if riesgo_total > 0.50:
            color = Colores.ROJO_B 
        else:
            color = Colores.AMARILLO 
            
        return texto, color

    def imprimir_heatmap(self, pos_capitan):
        print("\n--- MAPA DE PROBABILIDAD (BAYES) ---")
        
        print(f"Leyenda: {Colores.AZUL_B}CW{Colores.RESET}=Tú  {Colores.BLANCO_B}S{Colores.RESET}=Salida  {Colores.VERDE}ok{Colores.RESET}=Seguro")
        print(f"Genérico: {Colores.AMARILLO}R{Colores.RESET}=Riesgo Total (Fuente desconocida)")
        print(f"Amenazas: {Colores.ROJO}F{Colores.RESET}=Fuego  {Colores.COLOR_PINCHOS}P{Colores.RESET}=Pinchos  {Colores.COLOR_DARDOS}D{Colores.RESET}=Dardos  {Colores.COLOR_SOLDADO}M{Colores.RESET}=Soldado")
        print("-" * 50)
        
        for r in range(self.n):
            fila_str = ""
            for c in range(self.n):
                
                txt_celda = ""
                color_celda = Colores.RESET
                
                if (r, c) == pos_capitan:
                    txt_celda = "CW"
                    color_celda = Colores.AZUL_B
                else:
                    txt_celda, color_celda = self._analizar_celda(r, c)
                
                fila_str += f"{color_celda}[{txt_celda:^4}]{Colores.RESET}"
            print(fila_str)
        print("----------------------------------------\n")