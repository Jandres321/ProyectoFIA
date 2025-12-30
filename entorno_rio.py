import numpy as np
import random

class RioMDP:
    def __init__(self, rows=6, cols=6):
        self.rows = rows
        self.cols = cols
        self.start = (0, 0) # Posición inicial estándar (Top-Left)
        self.exit = None    # Se define en generación
        self.islands = []   # Lista de obstáculos
        self.currents = np.zeros(cols) # Fuerza de corriente por columna
        
        self._generar_entorno()

    def _generar_entorno(self):
        """Genera islas, salida y fuerzas de corriente aleatorias."""
        # 1. Definir Salida (E): Debe estar en la orilla derecha (última columna)
        # Opcional: Puede ser aleatoria en la última columna o fija.
        # El diagrama muestra la salida en un punto medio. La pondremos aleatoria en col N-1.
        exit_row = random.randint(1, self.rows - 2)
        self.exit = (exit_row, self.cols - 1)

        # 2. Generar Corrientes (Source 137-140)
        # Bordes (0 y N-1) tienen fuerza 0. Interiores aleatorio [0.06, 0.94]
        for j in range(self.cols):
            if j == 0 or j == self.cols - 1:
                self.currents[j] = 0.0
            else:
                self.currents[j] = round(random.uniform(0.06, 0.94), 2)

        # 3. Generar Islas (Source 108-109)
        # n_islas = 2. No en primera/última fila. No superpuestas.
        posibles = []
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1): # Evitamos orillas extremas para islas también
                if (r, c) != self.exit and (r, c) != self.start:
                    posibles.append((r, c))
        
        if len(posibles) >= 2:
            self.islands = random.sample(posibles, 2)
        else:
            self.islands = [] # Fallback raro

    def get_states(self):
        """Devuelve todos los estados posibles (r, c)."""
        return [(r, c) for r in range(self.rows) for c in range(self.cols)]

    def get_actions(self):
        """Acciones permitidas (Source 120)."""
        return ['up', 'down', 'left', 'right', 'stay']

    def get_transitions(self, state, action):
        """
        Retorna una lista de tuplas (probabilidad, nuevo_estado, recompensa).
        Calcula la física del río según Source 128-136.
        """
        if state == self.exit:
            return [] # Estado terminal

        r, c = state
        strength = self.currents[c]
        transitions = []

        # Función auxiliar para verificar límites y obstáculos
        def get_valid_next(nr, nc):
            # Si se sale del mapa o choca con isla, se queda en el sitio (Bounce)
            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                return state
            if (nr, nc) in self.islands:
                return state
            return (nr, nc)

        # --- LÓGICA DE TRANSICIÓN ---
        
        # Caso 1: Acción DOWN (Source 130)
        # La corriente ayuda, así que la probabilidad es 1.0 hacia abajo.
        if action == 'down':
            next_s = get_valid_next(r + 1, c)
            rew = 100 if next_s == self.exit else -1
            transitions.append((1.0, next_s, rew))

        # Caso 2: STAY (Source 126 implícito o decisión de diseño)
        # Asumiremos que STAY también sufre deriva si hay corriente, 
        # pero para simplificar y seguir "moves in desired direction", 
        # trataremos STAY como intento de quedarse (P_dir) + arrastre (P_down).
        elif action == 'stay':
            # Intento: Quedarse
            # Deriva: Bajar
            dest_intended = state
            dest_drift = get_valid_next(r + 1, c)
            
            p_intent = 1.0 - strength
            p_drift = strength
            
            # Recompensas
            rew_intent = -1 # Gastar tiempo cuesta
            rew_drift = 100 if dest_drift == self.exit else -1
            
            if p_intent > 0: transitions.append((p_intent, dest_intended, rew_intent))
            if p_drift > 0: transitions.append((p_drift, dest_drift, rew_drift))

        # Caso 3: UP, LEFT, RIGHT (Source 129)
        else:
            # Determinar casilla objetivo del movimiento
            tr, tc = r, c
            if action == 'up': tr -= 1
            elif action == 'left': tc -= 1
            elif action == 'right': tc += 1
            
            dest_intended = get_valid_next(tr, tc)
            dest_drift = get_valid_next(r + 1, c) # La corriente siempre empuja al sur
            
            p_intent = 1.0 - strength
            p_drift = strength
            
            rew_intent = 100 if dest_intended == self.exit else -1
            rew_drift = 100 if dest_drift == self.exit else -1
            
            # Agregamos transiciones (sumando prob si el destino es el mismo)
            # Simplificación: Añadimos ambas y el algoritmo de Value Iteration sumará.
            if p_intent > 0: transitions.append((p_intent, dest_intended, rew_intent))
            if p_drift > 0: transitions.append((p_drift, dest_drift, rew_drift))

        return transitions

    def print_grid(self, agent_pos=None):
        print("\n--- MAPA DEL RÍO (Fuerzas) ---")
        # Imprimir fuerzas
        header = "      "
        for c in range(self.cols):
            header += f"{self.currents[c]:<5} "
        print(header)
        
        for r in range(self.rows):
            row_str = f"Row {r}| "
            for c in range(self.cols):
                char = " .  "
                pos = (r, c)
                if pos == agent_pos: char = "CWCK"
                elif pos == self.exit: char = "EXIT"
                elif pos in self.islands: char = "####"
                
                row_str += f"[{char:^4}]"
            print(row_str)
        print("-" * 40)