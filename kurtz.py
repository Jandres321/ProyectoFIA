from entorno import Palacio
from entorno_bayesiano import PalacioBayesiano
from agente import AgenteLogico, Colores
from agente_bayesiano import AgenteBayesiano
import sys
import time

def interpretar_perceptos_logicos(p):
    """Traduce los perceptos booleanos de la Parte 1 a texto coloreado."""
    txt = []
    if p[0]: txt.append(f"{Colores.CYAN}Brisa{Colores.RESET}")
    if p[1]: txt.append(f"{Colores.AMARILLO}Ronquido{Colores.RESET}")
    if p[2]: txt.append(f"{Colores.BLANCO_B}Resplandor{Colores.RESET}")
    if p[7]: txt.append(f"{Colores.ROJO_B}¡GRITO!{Colores.RESET}")
    
    paredes = []
    if p[3]: paredes.append("N")
    if p[4]: paredes.append("E")
    if p[5]: paredes.append("S")
    if p[6]: paredes.append("O")
    if paredes:
        txt.append(f"{Colores.NEGRO}(Muros: {''.join(paredes)}){Colores.RESET}")

    return ", ".join(txt) if txt else f"{Colores.NEGRO}Silencio absoluto...{Colores.RESET}"

def interpretar_perceptos_bayes(p):
    """Traduce los perceptos de la Parte 2 (Trampas específicas)."""
    txt = []
    if p[0]: txt.append(f"{Colores.ROJO}Olor Gas (Fuego){Colores.RESET}")
    if p[1]: txt.append(f"{Colores.ROJO}Crujido (Pinchos){Colores.RESET}")
    if p[2]: txt.append(f"{Colores.ROJO}Cables (Dardos){Colores.RESET}")
    if p[3]: txt.append(f"{Colores.AMARILLO}Ronquido{Colores.RESET}")
    if p[4]: txt.append(f"{Colores.BLANCO_B}Resplandor{Colores.RESET}")
    if p[9]: txt.append(f"{Colores.ROJO_B}¡GRITO!{Colores.RESET}")
    return ", ".join(txt) if txt else f"{Colores.NEGRO}Nada destacable{Colores.RESET}"

def loop_parte1_logica():
    """Ejecuta el bucle de juego de la Parte 1 (Lógica y Búsqueda)."""
    print(f"\n{Colores.VERDE_B}--- PARTE 1: EL PALACIO LÓGICO ---{Colores.RESET}")
    
    print("Selecciona el modo de control:")
    print(f"1. {Colores.AZUL_B}Manual{Colores.RESET}")
    print(f"2. {Colores.AMARILLO_B}Automático - BFS{Colores.RESET}")
    print(f"3. {Colores.MAGENTA_B}Automático - DFS{Colores.RESET}")
    
    modo = input(f"{Colores.VERDE_B}Opción (1/2/3): {Colores.RESET}").strip()
    
    algoritmo = "MANUAL"
    if modo == '2': algoritmo = "BFS"
    elif modo == '3': algoritmo = "DFS"
    
    juego = Palacio()
    cerebro = AgenteLogico(juego.n)
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos del entorno real
        perceptos = juego.obtener_perceptos()
        
        # 2. El agente razona y actualiza su mapa mental
        cerebro.razonar(juego.pos_capitan, perceptos)
        cerebro.imprimir_mapa_mental(juego.pos_capitan, juego.kurtz_encontrado)
        
        # Mostrar información al usuario
        print(f"{Colores.MAGENTA}Perceptos:{Colores.RESET} {interpretar_perceptos_logicos(perceptos)}")
        if juego.kurtz_encontrado:
            print(f"{Colores.AMARILLO_B}>>> OBJETIVO: ¡LLEVA A KURTZ A LA SALIDA! <<<{Colores.RESET}")
        else:
            print(f"{Colores.AZUL}>>> OBJETIVO: Encuentra a Kurtz.{Colores.RESET}")
        
        accion_final = None
        
        if algoritmo == "MANUAL":
            # --- MODO MANUAL ---
            print(f"{Colores.NEGRO}Controles: WASD (Mover), G (Granada), E (Salir), Q (Rendirse){Colores.RESET}")
            accion_raw = input(f"{Colores.VERDE_B}Orden:{Colores.RESET} ").lower().strip()
            
            if accion_raw == 'q': break
            
            if accion_raw == 'g':
                if juego.granada_usada:
                    print(f"{Colores.ROJO}¡Sin granadas!{Colores.RESET}")
                    continue
                d = input(f"¿Dirección? (w/a/s/d): ").strip()
                if d in 'wasd': accion_final = 'g' + d
            elif accion_raw in 'wasde':
                accion_final = accion_raw
        else:
            # --- MODO AUTOMÁTICO ---
            print(f"{Colores.CYAN}El Capitán está pensando ({algoritmo})...{Colores.RESET}")
            time.sleep(0.6)
            
            accion_final = cerebro.decidir_accion_automatica(juego.pos_capitan, algoritmo)
            
            if accion_final:
                print(f"Acción decidida: {Colores.VERDE_B}{accion_final.upper()}{Colores.RESET}")
            else:
                print(f"{Colores.ROJO_B}¡El Capitán está atascado!{Colores.RESET}")
                break

        # Ejecutar la acción
        if accion_final:
            nuevos_perceptos, terminado, mensaje = juego.paso(accion_final)
            print(f"\n{Colores.BLANCO_B}>> {mensaje} <<{Colores.RESET}\n") 
            
            if terminado:
                jugando = False 
                if "MISIÓN CUMPLIDA" in mensaje:
                    print(f"\n{Colores.VERDE_B}" + "🌟" * 15)
                    print("     VICTORIA TOTAL     ")
                    print("🌟" * 15 + f"{Colores.RESET}\n")
                else:
                    print(f"\n{Colores.ROJO_B}" + "☠️ " * 10)
                    print("     GAME OVER      ")
                    print("☠️ " * 10 + f"{Colores.RESET}\n")

def loop_parte2_bayesiana():
    """Ejecuta el bucle de juego de la Parte 2 (Inferencia Bayesiana)."""
    print(f"\n{Colores.MAGENTA_B}--- PARTE 2: INFERENCIA BAYESIANA ---{Colores.RESET}")
    print("Modo de navegación asistida por probabilidad.")
    
    juego = PalacioBayesiano()
    cerebro = AgenteBayesiano(juego.n)
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos (incluyen olores de trampas específicas)
        perceptos = juego.obtener_perceptos()
        
        # 2. Actualizar creencias (Mapas de calor de probabilidad)
        cerebro.actualizar_creencias(juego.pos_capitan, perceptos)
        cerebro.imprimir_heatmap(juego.pos_capitan)
        
        print(f"{Colores.MAGENTA}Perceptos:{Colores.RESET} {interpretar_perceptos_bayes(perceptos)}")
        
        # --- INPUT MANUAL (Por ahora) ---
        print(f"{Colores.NEGRO}Controles: WASD (Mover), G (Granada), E (Salir), Q (Rendirse){Colores.RESET}")
        accion_raw = input(f"{Colores.VERDE_B}Orden:{Colores.RESET} ").lower().strip()
        
        if accion_raw == 'q': break
        
        accion_final = None
        if accion_raw == 'g':
            if juego.granada_usada:
                print(f"{Colores.ROJO}¡Sin granadas!{Colores.RESET}")
                continue
            d = input(f"¿Dirección? (w/a/s/d): ").strip()
            if d in 'wasd': accion_final = 'g' + d
        elif accion_raw in 'wasde':
            accion_final = accion_raw

        # Ejecutar acción
        if accion_final:
            _, terminado, msg = juego.paso(accion_final)
            print(f"\n{Colores.BLANCO_B}>> {msg} <<{Colores.RESET}\n")
            if terminado:
                jugando = False
                if "MISIÓN CUMPLIDA" in msg:
                    print(f"\n{Colores.VERDE_B}🌟 VICTORIA (Superviviente Bayesiano) 🌟{Colores.RESET}\n")
                else:
                    print(f"\n{Colores.ROJO_B}☠️ HAS MUERTO ☠️{Colores.RESET}\n")

def main():
    print(f"{Colores.VERDE_B}--- PROYECTO: BUSCANDO AL CORONEL KURTZ ---{Colores.RESET}")
    print("1. Parte 1: El Palacio (Lógica y Búsqueda)")
    print("2. Parte 2: Incertidumbre (Bayes)")
    
    opcion = input(f"{Colores.VERDE_B}Selecciona Parte (1/2): {Colores.RESET}").strip()
    
    if opcion == '1':
        loop_parte1_logica()
    elif opcion == '2':
        loop_parte2_bayesiana()
    else:
        print("Opción no válida. Saliendo.")

if __name__ == "__main__":
    main()