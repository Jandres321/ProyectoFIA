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
        self.pos_capitan = (0, 0) # Siempre empieza en (0,0)
        
        # Estado del juego
        self.kurtz_encontrado = False
        self.soldado_neutralizado = False
        self.juego_terminado = False
        self.mensaje_final = ""
        self.granada_usada = False
        self.grito_pendiente = False # Nuevo flag para el percepto del grito        
        
        # Inicializar mapa
        self._generar_mapa_aleatorio()

    def _generar_mapa_aleatorio(self):
        """Distribuye los elementos aleatoriamente respetando las reglas."""
        todas_las_celdas = [(r, c) for r in range(self.n) for c in range(self.n)]
        # El capitán empieza en (0,0), esa celda debe estar libre de peligros inmediatos al spawn
        todas_las_celdas.remove((0, 0)) 
        
        random.shuffle(todas_las_celdas)
        
        # 1. Colocar 3 Precipicios
        self.pos_precipicios = [todas_las_celdas.pop() for _ in range(3)]
        
        # 2. Colocar Soldado
        self.pos_soldado = todas_las_celdas.pop()
        
        # 3. Colocar Coronel Kurtz (No puede estar en precipicio ni soldado)
        # Al usar .pop() de la lista barajada, garantizamos que no coinciden
        self.pos_kurtz = todas_las_celdas.pop()
        
        # 4. Colocar Salida (Posición desconocida)
        self.pos_salida = todas_las_celdas.pop()

    def obtener_perceptos(self):
        r, c = self.pos_capitan
        adyacentes = self._obtener_adyacentes(r, c)
        
        # 1. Brisa (igual que antes)
        brisa = any(pos in self.pos_precipicios for pos in adyacentes)
        
        # 2. Ronquido (MODIFICADO: Si está neutralizado, ya no ronca)
        ronquido = False
        if not self.soldado_neutralizado:
            ronquido = any(pos == self.pos_soldado for pos in adyacentes)
            
        # 3. Resplandor y 4. Paredes (igual que antes)
        es_salida_o_cerca = (self.pos_capitan == self.pos_salida) or \
                            any(pos == self.pos_salida for pos in adyacentes)
        resplandor = es_salida_o_cerca
        
        pared_norte = (r == 0)
        pared_este = (c == self.n - 1)
        pared_sur = (r == self.n - 1)
        pared_oeste = (c == 0)
        
        # 5. Grito (MODIFICADO: Se activa solo el turno justo después de matar)
        grito = self.grito_pendiente
        self.grito_pendiente = False # El grito se oye una vez y se desvanece
        
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
        Admite 'w','a','s','d' (mover), 'e' (salir)
        Y AHORA: 'gw', 'ga', 'gs', 'gd' (lanzar granada norte, oeste, sur, este)
        """
        if self.juego_terminado:
            return self.obtener_perceptos(), True, self.mensaje_final

        r, c = self.pos_capitan
        
        # --- LÓGICA DE LA GRANADA ---
        if accion.startswith('g'):
            if self.granada_usada:
                # Si ya la usó, no pasa nada (o mensaje de error), pero pierde el turno
                return self.obtener_perceptos(), False, "Ya no tienes granadas."
            
            self.granada_usada = True
            direccion = accion[1] # w, a, s, d
            
            # Calcular dónde cae la granada
            tr, tc = r, c
            if direccion == 'w': tr -= 1
            elif direccion == 's': tr += 1
            elif direccion == 'a': tc -= 1
            elif direccion == 'd': tc += 1
            
            target = (tr, tc)
            
            # Verificar impacto
            if target == self.pos_soldado:
                self.soldado_neutralizado = True
                self.grito_pendiente = True # ¡Bingo!
                mensaje_turno = "¡BOOM! Has lanzado la granada y escuchas un alarido."
            else:
                mensaje_turno = "¡BOOM! La explosión retumba... pero solo hay silencio después."
                
            return self.obtener_perceptos(), False, mensaje_turno

        # --- LÓGICA DE MOVIMIENTO (Igual que antes, con pequeña modificación en muerte) ---
        nueva_r, nueva_c = r, c
        if accion == 'w' and r > 0: nueva_r -= 1
        elif accion == 's' and r < self.n - 1: nueva_r += 1
        elif accion == 'a' and c > 0: nueva_c -= 1
        elif accion == 'd' and c < self.n - 1: nueva_c += 1
        # Lógica de SALIDA (e)
        elif accion == 'e':
            if self.pos_capitan == self.pos_salida:
                if self.kurtz_encontrado:
                    self.juego_terminado = True
                    return self.obtener_perceptos(), True, "¡MISIÓN CUMPLIDA! Escapas del palacio con el Coronel Kurtz."
                else:
                    # El manual dice que si sales sin él, el estado se mantiene (no terminas, o es error)
                    return self.obtener_perceptos(), False, "¡No puedes irte sin Kurtz! Búscalo primero."
            else:
                return self.obtener_perceptos(), False, "Aquí no hay ninguna salida."

        # Actualizar posición
        self.pos_capitan = (nueva_r, nueva_c)
        mensaje_turno = "Avanzas con cautela..." # Mensaje por defecto

        # Verificar muerte (Precipicio/Soldado)
        if self.pos_capitan in self.pos_precipicios:
            self.juego_terminado = True
            self.mensaje_final = "MUERTE: Has caído en un precipicio."
        elif self.pos_capitan == self.pos_soldado and not self.soldado_neutralizado:
            self.juego_terminado = True
            self.mensaje_final = "MUERTE: El soldado enemigo ha despertado."

        # --- LÓGICA DE RECOGER A KURTZ ---
        # Si pisamos su celda y no lo teníamos, lo recogemos
        if self.pos_capitan == self.pos_kurtz and not self.kurtz_encontrado:
            self.kurtz_encontrado = True
            mensaje_turno = "¡HAS ENCONTRADO AL CORONEL KURTZ! Te sigue. ¡Corre a la salida!"

        return self.obtener_perceptos(), self.juego_terminado, (self.mensaje_final if self.juego_terminado else mensaje_turno)

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