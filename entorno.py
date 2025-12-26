import numpy as np
import random

class Palacio:
    def __init__(self, size=6):
        self.n = size
        # Elementos del juego
        self.pos_precipicios = []
        self.pos_soldado = None
        self.pos_kurtz = None
        self.pos_salida = None
        self.pos_capitan = (0, 0) # Siempre empieza en (0,0) [cite: 34]
        
        # Estado del juego
        self.kurtz_encontrado = False
        self.soldado_neutralizado = False
        self.juego_terminado = False
        self.mensaje_final = ""
        self.granada_usada = False
        
        # Inicializar mapa
        self._generar_mapa_aleatorio()

    def _generar_mapa_aleatorio(self):
        """Distribuye los elementos aleatoriamente respetando las reglas."""
        todas_las_celdas = [(r, c) for r in range(self.n) for c in range(self.n)]
        # El capitán empieza en (0,0), esa celda debe estar libre de peligros inmediatos al spawn
        todas_las_celdas.remove((0, 0)) 
        
        random.shuffle(todas_las_celdas)
        
        # 1. Colocar 3 Precipicios [cite: 23]
        self.pos_precipicios = [todas_las_celdas.pop() for _ in range(3)]
        
        # 2. Colocar Soldado [cite: 24]
        self.pos_soldado = todas_las_celdas.pop()
        
        # 3. Colocar Coronel Kurtz (No puede estar en precipicio ni soldado) [cite: 32]
        # Al usar .pop() de la lista barajada, garantizamos que no coinciden
        self.pos_kurtz = todas_las_celdas.pop()
        
        # 4. Colocar Salida (Posición desconocida) [cite: 27]
        self.pos_salida = todas_las_celdas.pop()

    def obtener_perceptos(self):
        """
        Devuelve la lista de booleanos:
        [Brisa, Ronquido, Resplandor, ParedN, ParedE, ParedS, ParedW, Grito]
        Según se define en el manual[cite: 71].
        """
        r, c = self.pos_capitan
        adyacentes = self._obtener_adyacentes(r, c)
        
        # 1. Brisa (Cerca de precipicio) [cite: 61]
        brisa = any(pos in self.pos_precipicios for pos in adyacentes)
        
        # 2. Ronquido (Cerca del soldado vivo) [cite: 62]
        ronquido = False
        if not self.soldado_neutralizado:
            # Si el soldado está vivo, emite ronquido en adyacentes
            ronquido = any(pos == self.pos_soldado for pos in adyacentes)
            
        # 3. Resplandor (En la salida o adyacente) [cite: 63]
        # Nota: El PDF dice "en la salida, o en una celda adyacente a ésta"
        es_salida_o_cerca = (self.pos_capitan == self.pos_salida) or \
                            any(pos == self.pos_salida for pos in adyacentes)
        resplandor = es_salida_o_cerca
        
        # 4. Paredes (Norte, Este, Sur, Oeste) [cite: 64]
        # Asumimos (0,0) es esquina superior izquierda. 
        # Norte: r-1 < 0. Sur: r+1 >= n. Oeste: c-1 < 0. Este: c+1 >= n.
        pared_norte = (r == 0)
        pared_este = (c == self.n - 1)
        pared_sur = (r == self.n - 1)
        pared_oeste = (c == 0)
        
        # 5. Grito (Si acabamos de matar al soldado) [cite: 65]
        # Esto depende de si la acción anterior fue exitosa, lo simulamos simple por ahora
        grito = False 
        
        return [brisa, ronquido, resplandor, pared_norte, pared_este, pared_sur, pared_oeste, grito]

    def _obtener_adyacentes(self, r, c):
        """Retorna coordenadas válidas adyacentes (arriba, abajo, izq, der)."""
        candidatos = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        validos = []
        for fr, fc in candidatos:
            if 0 <= fr < self.n and 0 <= fc < self.n:
                validos.append((fr, fc))
        return validos

    def paso(self, accion):
        """
        Ejecuta una acción: 'w','a','s','d' (mover), 'g' (granada), 'e' (salir).
        Devuelve: (perceptos, juego_terminado, mensaje)
        """
        if self.juego_terminado:
            return self.obtener_perceptos(), True, self.mensaje_final

        r, c = self.pos_capitan
        nueva_r, nueva_c = r, c
        
        # Movimiento
        if accion == 'w' and r > 0: nueva_r -= 1
        elif accion == 's' and r < self.n - 1: nueva_r += 1
        elif accion == 'a' and c > 0: nueva_c -= 1
        elif accion == 'd' and c < self.n - 1: nueva_c += 1
        
        # Acción Salir
        elif accion == 'e':
            if self.pos_capitan == self.pos_salida:
                if self.kurtz_encontrado:
                    self.juego_terminado = True
                    self.mensaje_final = "¡MISIÓN CUMPLIDA! Has rescatado a Kurtz."
                else:
                    self.mensaje_final = "Has salido... pero sin Kurtz. Misión fallida."
                    # El PDF dice "si ejecuta salir en otra celda, el estado se mantiene" [cite: 54]
                    # Asumimos que salir sin Kurtz no termina el juego, o termina mal.
            return self.obtener_perceptos(), self.juego_terminado, self.mensaje_final

        # Actualizar posición
        self.pos_capitan = (nueva_r, nueva_c)
        
        # Verificar muerte por Precipicio [cite: 45]
        if self.pos_capitan in self.pos_precipicios:
            self.juego_terminado = True
            self.mensaje_final = "MUERTE: Has caído en un precipicio."
            
        # Verificar muerte por Soldado [cite: 46]
        elif self.pos_capitan == self.pos_soldado and not self.soldado_neutralizado:
            self.juego_terminado = True
            self.mensaje_final = "MUERTE: El soldado enemigo ha despertado y te ha eliminado."

        # Encontrar a Kurtz [cite: 56]
        if self.pos_capitan == self.pos_kurtz:
            self.kurtz_encontrado = True

        return self.obtener_perceptos(), self.juego_terminado, self.mensaje_final

    def imprimir_tablero_cheat(self):
        """Muestra el mapa completo (SOLO PARA DEBUG/EVALUACIÓN)"""
        print("\n--- MAPA (CHEAT SHEET) ---")
        for r in range(self.n):
            fila_str = ""
            for c in range(self.n):
                celda = " . "
                pos = (r, c)
                contenido = []
                
                if pos == self.pos_capitan: contenido.append("CW")
                if pos == self.pos_kurtz: contenido.append("CK")
                if pos == self.pos_soldado: contenido.append("S" if not self.soldado_neutralizado else "s_muerto")
                if pos in self.pos_precipicios: contenido.append("P")
                if pos == self.pos_salida: contenido.append("E") # Exit
                
                if contenido:
                    celda = " ".join(contenido)
                    celda = f"[{celda:^5}]" # Centrado
                else:
                    celda = "[     ]"
                fila_str += celda
            print(fila_str)
        print("--------------------------\n")