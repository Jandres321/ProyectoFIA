from entorno import Palacio
from entorno_bayesiano import PalacioBayesiano
from entorno_rio import RioMDP
from agente import AgenteLogico, Colores
from agente_bayesiano import AgenteBayesiano
from agente_mdp import AgenteMDP
import sys
import time
import os
import numpy as np

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
    if p[1]: txt.append(f"{Colores.COLOR_PINCHOS}Crujido (Pinchos){Colores.RESET}")
    if p[2]: txt.append(f"{Colores.COLOR_DARDOS}Cables (Dardos){Colores.RESET}")
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
    """Ejecuta el bucle de juego de la Parte 2.1 (Inferencia Bayesiana)."""
    print(f"\n{Colores.MAGENTA_B}--- PARTE 2.1: EL PALACIO BAYESIANO ---{Colores.RESET}")
    print("El Capitán Willard usa estadística para sobrevivir.")
    
    print("Selecciona el modo de control:")
    print(f"1. {Colores.AZUL_B}Manual{Colores.RESET} (Tú decides basándote en el Heatmap)")
    print(f"2. {Colores.AMARILLO_B}Automático{Colores.RESET} (Navegación por A* y Riesgo)")
    
    modo = input(f"{Colores.VERDE_B}Opción (1/2): {Colores.RESET}").strip()
    es_automatico = (modo == '2')
    
    juego = PalacioBayesiano()
    cerebro = AgenteBayesiano(juego.n)
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos
        perceptos = juego.obtener_perceptos()
        
        # 2. Actualizar creencias (Bayes)
        cerebro.actualizar_creencias(juego.pos_capitan, perceptos)
        cerebro.tengo_a_kurtz = juego.kurtz_encontrado
        
        # 3. Visualizar
        cerebro.imprimir_heatmap(juego.pos_capitan)
        print(f"{Colores.MAGENTA}Perceptos:{Colores.RESET} {interpretar_perceptos_bayes(perceptos)}")
        
        if juego.kurtz_encontrado:
            print(f"{Colores.AMARILLO_B}>>> OBJETIVO: ¡LLEVA A KURTZ A LA SALIDA (S)! <<<{Colores.RESET}")
        else:
            print(f"{Colores.AZUL}>>> OBJETIVO: Encuentra a Kurtz (Explora zonas seguras).{Colores.RESET}")

        accion_final = None
        
        if not es_automatico:
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
            print(f"{Colores.CYAN}El Capitán está calculando riesgos...{Colores.RESET}")
            time.sleep(0.8)
            
            accion_final = cerebro.decidir_accion_automatica(juego.pos_capitan)
            
            if accion_final:
                print(f"Acción decidida: {Colores.VERDE_B}{accion_final.upper()}{Colores.RESET}")
            else:
                print(f"{Colores.ROJO_B}¡Pánico! No hay ruta segura (<20% riesgo). El Capitán se queda paralizado.{Colores.RESET}")
                break

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

def loop_parte2_rio():
    """Ejecuta el bucle de juego de la Parte 2.2 (MDP y Value Iteration)."""
    print(f"\n{Colores.CYAN}--- PARTE 2.2: CRUZANDO EL RÍO (MDP) ---{Colores.RESET}")
    print("Generando entorno estocástico...")
    
    # 1. Crear entorno
    rio = RioMDP(rows=6, cols=6)
    rio.print_grid(rio.start)
    
    # 2. Inicializar Agente y Resolver MDP
    print(f"{Colores.AMARILLO}El Capitán está analizando las corrientes (Value Iteration)...{Colores.RESET}")
    cerebro = AgenteMDP(rio)
    cerebro.value_iteration(gamma=0.9)
    
    print("\n--- POLÍTICA ÓPTIMA CALCULADA ---")
    for r in range(rio.rows):
        row_str = ""
        for c in range(rio.cols):
            s = (r, c)
            if s == rio.exit: symb = "EXIT"
            elif s in rio.islands: symb = "####"
            else:
                act = cerebro.policy[s]
                # Flechas para visualizar mejor la política
                if act == 'up': symb = " ^ "
                elif act == 'down': symb = " v "
                elif act == 'left': symb = " < "
                elif act == 'right': symb = " > "
                elif act == 'stay': symb = " o "
                else: symb = " ? "
            row_str += f"[{symb:^4}]"
        print(row_str)
    
    # 3. Simulación de Partida
    print(f"\n{Colores.VERDE}--- INICIANDO CRUCE ---{Colores.RESET}")
    input("Pulsa Enter para comenzar la simulación...")
    
    state = rio.start
    steps = 0
    total_reward = 0
    
    while state != rio.exit and steps < 50:
        # Visualizar (Limpiar pantalla para efecto animación)
        os.system('cls' if os.name == 'nt' else 'clear') 
        print(f"\nPasos: {steps} | Recompensa Acumulada: {total_reward}")
        rio.print_grid(state)
        
        # Decidir
        action = cerebro.get_best_action(state)
        print(f"El Capitán decide: {Colores.AZUL}{action.upper()}{Colores.RESET}")
        time.sleep(1) 
        
        # Ejecutar transición (Estocástica)
        transitions = rio.get_transitions(state, action)
        
        # Elegir siguiente estado según probabilidades
        probs = [t[0] for t in transitions]
        indices = range(len(transitions))
        chosen_idx = np.random.choice(indices, p=probs)
        
        prob, next_state, reward = transitions[chosen_idx]
        
        # Feedback narrativo si hubo deriva
        if next_state != state and action != 'stay':
            # Comprobación simple de deriva (si acabamos más abajo de lo esperado o no nos movimos donde queríamos)
            # Nota: Esto es simplificado para feedback visual
            if next_state[0] > state[0] and action != 'down':
                 print(f"{Colores.ROJO}¡La corriente arrastra al bote hacia el sur!{Colores.RESET}")
        
        state = next_state
        total_reward += reward
        steps += 1
        
        time.sleep(0.5)

    # Final
    rio.print_grid(state)
    if state == rio.exit:
        print(f"\n{Colores.VERDE}🌟 ¡VICTORIA! Willard y Kurtz han cruzado el río a salvo. 🌟{Colores.RESET}\n")
    else:
        print(f"\n{Colores.ROJO}☠️ FRACASO: Se acabaron los suministros o el tiempo. ☠️{Colores.RESET}\n")

def menu_parte2():
    print(f"\n{Colores.VERDE_B}--- PARTE 2: INCERTIDUMBRE ---{Colores.RESET}")
    print("1. El Palacio (Inferencia Bayesiana)")
    print("2. El Río (MDP - Value Iteration)")
    
    sub_opcion = input(f"{Colores.VERDE_B}Selecciona Escenario (1/2): {Colores.RESET}").strip()
    
    if sub_opcion == '1':
        loop_parte2_bayesiana()
    elif sub_opcion == '2':
        loop_parte2_rio()
    else:
        print("Opción inválida.")

def main():
    print(f"{Colores.VERDE_B}--- PROYECTO: BUSCANDO AL CORONEL KURTZ ---{Colores.RESET}")
    print("1. Parte 1: El Palacio (Lógica y Búsqueda)")
    print("2. Parte 2: Incertidumbre (Bayes y MDP)")
    
    opcion = input(f"{Colores.VERDE_B}Selecciona Parte (1/2): {Colores.RESET}").strip()
    
    if opcion == '1':
        loop_parte1_logica()
    elif opcion == '2':
        menu_parte2()
    else:
        print("Opción no válida. Saliendo.")

if __name__ == "__main__":
    main()