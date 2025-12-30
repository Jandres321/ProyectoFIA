import numpy as np
import random

class PalacioBayesiano:
    def __init__(self, size=6):
        self.n = size
        self.pos_capitan = (0, 0)
        
        # Elementos específicos
        self.pos_fuego = None
        self.pos_pinchos = None
        self.pos_dardos = None
        self.pos_soldado = None
        self.pos_kurtz = None
        self.pos_salida = None
        
        # Estado
        self.kurtz_encontrado = False
        self.soldado_neutralizado = False
        self.juego_terminado = False
        self.mensaje_final = ""
        self.granada_usada = False
        self.grito_pendiente = False
        
        self._generar_mapa_aleatorio()

    def _generar_mapa_aleatorio(self):
        """
        Generación compleja:
        1. Fuego, Pinchos y Dardos se colocan independientemente (pueden coincidir).
        2. Soldado, Kurtz y Salida se colocan en casillas SIN trampas (pueden coincidir entre ellos).
        """
        todas = [(r, c) for r in range(self.n) for c in range(self.n)]
        todas.remove((0, 0)) # El spawn siempre libre
        
        # 1. Colocar Trampas (Independientes)
        self.pos_fuego = random.choice(todas)
        self.pos_pinchos = random.choice(todas)
        self.pos_dardos = random.choice(todas)
        
        # Identificar casillas "sucias" (con alguna trampa)
        casillas_trampa = {self.pos_fuego, self.pos_pinchos, self.pos_dardos}
        
        # Identificar casillas "limpias" para NPCs y Salida
        # (Deben ser casillas sin trampas y distintas a (0,0))
        casillas_limpias = [pos for pos in todas if pos not in casillas_trampa]
        
        # Si por azar llenamos todo de trampas y no hay sitio (muy improbable en 6x6), reseteamos
        if len(casillas_limpias) < 1:
            self._generar_mapa_aleatorio()
            return

        # 2. Colocar Soldado, Kurtz y Salida en zona limpia
        # El enunciado dice que pueden coincidir (M, S, CK en la misma celda es posible)
        self.pos_soldado = random.choice(casillas_limpias)
        self.pos_kurtz = random.choice(casillas_limpias)
        self.pos_salida = random.choice(casillas_limpias)

    def obtener_perceptos(self):
        """
        Retorna: [Olor(F), Crujido(P), Cable(D), Ronquido(M), Resplandor(S), 
                  ParedN, ParedE, ParedS, ParedW, Grito]
        """
        r, c = self.pos_capitan
        ady = self._obtener_adyacentes_y_propia(r, c) # Incluye la propia celda
        ady_estricta = self._obtener_adyacentes(r, c)  # Solo vecinos
        
        # Estímulos de Trampas (Se sienten en vecina Y propia)
        olor_fuego = any(pos == self.pos_fuego for pos in ady)
        crujido_pinchos = any(pos == self.pos_pinchos for pos in ady)
        cable_dardos = any(pos == self.pos_dardos for pos in ady)
        
        # Estímulo Soldado (Se siente en vecina Y propia)
        # Nota: El manual dice "audible desde las celdas contiguas". 
        # Asumiremos modelo estándar: contiguas + propia.
        ronquido = False
        if not self.soldado_neutralizado:
            ronquido = any(pos == self.pos_soldado for pos in ady)
            
        # Estímulo Salida
        resplandor = any(pos == self.pos_salida for pos in ady)
        
        # Paredes
        pn = (r == 0)
        pe = (c == self.n - 1)
        ps = (r == self.n - 1)
        pw = (c == 0)
        
        grito = self.grito_pendiente
        self.grito_pendiente = False
        
        return [olor_fuego, crujido_pinchos, cable_dardos, ronquido, resplandor, 
                pn, pe, ps, pw, grito]

    def _obtener_adyacentes(self, r, c):
        cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        return [(fr, fc) for fr, fc in cand if 0 <= fr < self.n and 0 <= fc < self.n]

    def _obtener_adyacentes_y_propia(self, r, c):
        lista = self._obtener_adyacentes(r, c)
        lista.append((r, c))
        return lista

    def paso(self, accion):
        # La lógica de movimiento es idéntica a la Parte 1, pero verificando trampas específicas
        if self.juego_terminado:
            return self.obtener_perceptos(), True, self.mensaje_final

        r, c = self.pos_capitan
        
        # --- GRANADA (Igual que parte 1) ---
        if accion.startswith('g'):
            if self.granada_usada:
                return self.obtener_perceptos(), False, "Sin munición."
            self.granada_usada = True
            dr, dc = 0, 0
            if 'w' in accion: dr = -1
            elif 's' in accion: dr = 1
            elif 'a' in accion: dc = -1
            elif 'd' in accion: dc = 1
            target = (r + dr, c + dc)
            
            if target == self.pos_soldado:
                self.soldado_neutralizado = True
                self.grito_pendiente = True
                return self.obtener_perceptos(), False, "¡BOOM! Soldado eliminado."
            return self.obtener_perceptos(), False, "¡BOOM! Fallaste."

        # --- MOVIMIENTO ---
        nr, nc = r, c
        if accion == 'w' and r > 0: nr -= 1
        elif accion == 's' and r < self.n - 1: nr += 1
        elif accion == 'a' and c > 0: nc -= 1
        elif accion == 'd' and c < self.n - 1: nc += 1
        elif accion == 'e':
            if self.pos_capitan == self.pos_salida:
                if self.kurtz_encontrado:
                    self.juego_terminado = True
                    return self.obtener_perceptos(), True, "MISIÓN CUMPLIDA (Bayes)"
                else:
                    return self.obtener_perceptos(), False, "¡No puedes irte sin Kurtz! Búscalo primero."
            else:
                return self.obtener_perceptos(), False, "Aquí no hay ninguna salida."
        
        self.pos_capitan = (nr, nc)
        
        # Verificar Muertes
        muerte = []
        if self.pos_capitan == self.pos_fuego: muerte.append("QUEMADO por Trampa de Fuego")
        if self.pos_capitan == self.pos_pinchos: muerte.append("EMPALADO por Pinchos")
        if self.pos_capitan == self.pos_dardos: muerte.append("ENVENENADO por Dardos")
        if self.pos_capitan == self.pos_soldado and not self.soldado_neutralizado: muerte.append("EJECUTADO por Soldado")
        
        if muerte:
            self.juego_terminado = True
            self.mensaje_final = f"MUERTE: {' + '.join(muerte)}"
            return self.obtener_perceptos(), True, self.mensaje_final
            
        # Verificar Kurtz
        msg = "Avanzas..."
        if self.pos_capitan == self.pos_kurtz and not self.kurtz_encontrado:
            self.kurtz_encontrado = True
            msg = "¡HAS ENCONTRADO AL CORONEL KURTZ! Te sigue. ¡Corre a la salida!"
            
        return self.obtener_perceptos(), False, msg