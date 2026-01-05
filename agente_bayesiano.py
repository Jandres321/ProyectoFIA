import numpy as np
import heapq
from agente import Colores

class AgenteBayesiano:
    def __init__(self, size=6):
        self.n = size
        # Inicialización de matrices de probabilidad con prior uniforme
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
        self.casillas_visitadas = set() # Memoria para exploración

    def actualizar_creencias(self, pos_actual, perceptos):
        """
        Actualiza todas las matrices de probabilidad basándose en los nuevos perceptos.
        """
        self.casillas_visitadas.add(pos_actual)
        
        e_fuego = perceptos[0]
        e_pinchos = perceptos[1]
        e_dardos = perceptos[2]
        e_soldado = perceptos[3]
        e_salida = perceptos[4]
        grito = perceptos[9]
        
        # 1. Actualizar Soldado
        if grito:
            self.P_soldado = np.zeros((self.n, self.n))
        else:
            self._aplicar_bayes(self.P_soldado, pos_actual, e_soldado)

        # 2. Actualizar Trampas
        self._aplicar_bayes(self.P_fuego, pos_actual, e_fuego)
        self._aplicar_bayes(self.P_pinchos, pos_actual, e_pinchos)
        self._aplicar_bayes(self.P_dardos, pos_actual, e_dardos)
        
        # 3. Actualizar Salida
        self._aplicar_bayes(self.P_salida, pos_actual, e_salida)
        
        # 4. Evidencia Implícita (Estoy vivo aquí)
        r, c = pos_actual
        self.P_fuego[r, c] = 0
        self.P_pinchos[r, c] = 0
        self.P_dardos[r, c] = 0
        if not grito: self.P_soldado[r, c] = 0 

        # 5. Normalizar
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
                
                # Modelo del sensor determinista
                if percibe_estimulo:
                    likelihood = 1.0 if es_vecino else 0.0
                else:
                    likelihood = 0.0 if es_vecino else 1.0
                
                matriz_prob[i, j] *= likelihood

    def _normalizar(self, matriz):
        suma = np.sum(matriz)
        if suma > 0: matriz /= suma

    def obtener_riesgo(self, r, c):
        """Calcula la probabilidad de MUERTE en una casilla."""
        p_f = self.P_fuego[r, c]
        p_p = self.P_pinchos[r, c]
        p_d = self.P_dardos[r, c]
        p_m = self.P_soldado[r, c]
        
        # Probabilidad de sobrevivir (asumiendo independencia)
        prob_vivir = (1 - p_f) * (1 - p_p) * (1 - p_d) * (1 - p_m)
        return 1.0 - prob_vivir

    def _obtener_adyacentes(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    def _obtener_adyacentes_y_propia(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1), (r, c)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    # =========================================================================
    #                   MOTOR DE DECISIÓN AUTOMÁTICA (A*)
    # =========================================================================

    def decidir_accion_automatica(self, pos_actual):
        """
        Decide la siguiente acción basándose en riesgos y objetivos.
        Estrategia:
        1. Si hay Soldado detectado (>50%) al lado -> GRANADA.
        2. Si tengo a Kurtz -> Ir a Salida (Celda con max P_salida).
        3. Si no tengo a Kurtz -> Explorar (Ir a casilla segura no visitada más cercana).
        """
        # 1. ¿Amenaza Inmediata de Soldado?
        vecinos = self._obtener_adyacentes(*pos_actual)
        for v in vecinos:
            if self.P_soldado[v] > 0.5:
                # Calcular dirección granada
                dr, dc = v[0] - pos_actual[0], v[1] - pos_actual[1]
                if dr == -1: return 'gw'
                if dr == 1: return 'gs'
                if dc == -1: return 'ga'
                if dc == 1: return 'gd'

        # 2. Definir Meta
        meta = None
        
        if self.tengo_a_kurtz:
            # Buscar la celda con mayor probabilidad de ser salida
            # Argmax en 2D
            idx_flat = np.argmax(self.P_salida)
            meta = np.unravel_index(idx_flat, self.P_salida.shape)
            # Si la probabilidad es muy baja, seguimos explorando mejor
            if self.P_salida[meta] < 0.1:
                meta = None 
        
        # 3. Calcular Ruta
        # Intentamos primero con riesgo MUY BAJO (Cautela máxima)
        umbral_riesgo = 0.05 
        siguiente_paso = self._planificar_ruta(pos_actual, meta, umbral_riesgo)
        
        # Si no hay ruta segura, nos "desesperamos" un poco (hasta 20% riesgo)
        if not siguiente_paso:
            umbral_riesgo = 0.20
            siguiente_paso = self._planificar_ruta(pos_actual, meta, umbral_riesgo)
            
        # 4. Traducir paso a acción
        if siguiente_paso:
            if siguiente_paso == pos_actual: return 'e' # Estamos en la meta (salida)
            
            dr = siguiente_paso[0] - pos_actual[0]
            dc = siguiente_paso[1] - pos_actual[1]
            if dr == -1: return 'w'
            if dr == 1: return 's'
            if dc == -1: return 'a'
            if dc == 1: return 'd'
            
        return None # Atascado o sin plan

    def _planificar_ruta(self, inicio, meta_concreta, umbral_riesgo):
        """
        Algoritmo A* (A-Star) que considera obstáculos las celdas con Riesgo > Umbral.
        Si meta_concreta es None, busca la casilla 'Visitada=False' más cercana (Exploración).
        """
        # Cola de prioridad: (Costo_f, Costo_g, Posicion, Camino)
        # Costo_g = Pasos dados
        # Costo_h = Distancia Manhattan a meta (o 0 si es exploración)
        cola = []
        heapq.heappush(cola, (0, 0, inicio, []))
        
        visitados_algoritmo = set()
        visitados_algoritmo.add(inicio)
        
        while cola:
            f, g, actual, camino = heapq.heappop(cola)
            
            # Chequeo de Meta
            es_meta = False
            if meta_concreta:
                if actual == meta_concreta: es_meta = True
            else:
                # Modo Exploración: Cualquier casilla NO visitada previamente y accesible es meta
                if actual not in self.casillas_visitadas:
                    es_meta = True
            
            if es_meta:
                if not camino: return actual # Ya estamos ahí
                return camino[0] # Retornamos el primer paso
            
            # Expansión
            vecinos = self._obtener_adyacentes(*actual)
            for v in vecinos:
                if v in visitados_algoritmo: continue
                
                riesgo = self.obtener_riesgo(*v)
                
                # Solo transitamos si el riesgo es aceptable
                if riesgo < umbral_riesgo:
                    visitados_algoritmo.add(v)
                    
                    nuevo_g = g + 1
                    
                    # Heurística
                    h = 0
                    if meta_concreta:
                        h = abs(v[0] - meta_concreta[0]) + abs(v[1] - meta_concreta[1])
                    
                    # Penalización por riesgo (opcional, para preferir caminos MÁS seguros entre los seguros)
                    # Añadimos riesgo * 10 al costo para romper empates a favor de seguridad
                    costo_riesgo = riesgo * 10 
                    
                    nuevo_f = nuevo_g + h + costo_riesgo
                    
                    heapq.heappush(cola, (nuevo_f, nuevo_g, v, camino + [v]))
                    
        return None

    # ----------------------------------------------------------------------
    #   Visualización
    # ----------------------------------------------------------------------

    def _analizar_celda(self, r, c):
        """Determina texto y color para el Heatmap."""
        p_f = self.P_fuego[r, c]
        p_p = self.P_pinchos[r, c]
        p_d = self.P_dardos[r, c]
        p_m = self.P_soldado[r, c]
        p_salida = self.P_salida[r, c]

        riesgo_total = self.obtener_riesgo(r, c)
        
        # Prioridad 1: Salida
        if p_salida > 0.50: 
            return f"S{int(p_salida*100)}", Colores.BLANCO_B

        # Prioridad 2: Seguridad
        if riesgo_total < 0.05:
            return "ok", Colores.VERDE

        # Prioridad 3: Amenaza Identificada (>50%)
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

        # Prioridad 4: Riesgo Genérico
        texto = f"R{int(riesgo_total*100)}"
        color = Colores.ROJO_B if riesgo_total > 0.50 else Colores.AMARILLO
        return texto, color

    def imprimir_heatmap(self, pos_capitan):
        print("\n--- MAPA DE PROBABILIDAD (BAYES) ---")
        print(f"Leyenda: {Colores.AZUL_B}CW{Colores.RESET}=Tú  {Colores.CYAN_B}CW+K{Colores.RESET}=Con Kurtz  {Colores.BLANCO_B}S{Colores.RESET}=Salida  {Colores.VERDE}ok{Colores.RESET}=Seguro")
        print(f"Genérico: {Colores.AMARILLO}R{Colores.RESET}=Riesgo Total (Fuente desconocida)")
        print(f"Amenazas: {Colores.ROJO}F{Colores.RESET}=Fuego  {Colores.COLOR_PINCHOS}P{Colores.RESET}=Pinchos  {Colores.COLOR_DARDOS}D{Colores.RESET}=Dardos  {Colores.COLOR_SOLDADO}M{Colores.RESET}=Soldado")
        print("-" * 50)
        
        for r in range(self.n):
            fila_str = ""
            for c in range(self.n):
                txt_celda = ""
                color_celda = Colores.RESET
                
                if (r, c) == pos_capitan:
                    # Si tengo a Kurtz, mostramos CW+K en Cyan Brillante
                    if self.tengo_a_kurtz:
                        txt_celda = "CW+K"
                        color_celda = Colores.CYAN_B
                    else:
                        txt_celda = "CW"
                        color_celda = Colores.AZUL_B
                else:
                    txt_celda, color_celda = self._analizar_celda(r, c)
                
                fila_str += f"{color_celda}[{txt_celda:^4}]{Colores.RESET}"
            print(fila_str)
        print("----------------------------------------\n")