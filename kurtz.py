from entorno import Palacio
from agente import AgenteLogico, Colores
import sys
import time # Para darle emoción al modo automático

def interpretar_perceptos(p):
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

def main():
    print(f"{Colores.VERDE_B}--- BUSCANDO AL CORONEL KURTZ ---{Colores.RESET}")
    
    # --- MENÚ DE SELECCIÓN ---
    print("Selecciona el modo de juego:")
    print(f"1. {Colores.AZUL_B}Manual{Colores.RESET} (Tú controlas a Willard)")
    print(f"2. {Colores.AMARILLO_B}Automático - BFS{Colores.RESET} (Recomendado: Óptimo y seguro)")
    print(f"3. {Colores.MAGENTA_B}Automático - DFS{Colores.RESET} (Exploración profunda, puede ser caótica)")
    
    modo = input(f"{Colores.VERDE_B}Opción (1/2/3): {Colores.RESET}").strip()
    
    algoritmo = "MANUAL"
    if modo == '2': algoritmo = "BFS"
    elif modo == '3': algoritmo = "DFS"
    
    juego = Palacio()
    cerebro = AgenteLogico(juego.n)
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos
        perceptos = juego.obtener_perceptos()
        
        # 2. Razonar
        cerebro.razonar(juego.pos_capitan, perceptos)
        
        # 3. Dibujar
        cerebro.imprimir_mapa_mental(juego.pos_capitan, juego.kurtz_encontrado)
        
        # Info
        print(f"{Colores.MAGENTA}Perceptos:{Colores.RESET} {interpretar_perceptos(perceptos)}")
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
            time.sleep(0.8) # Pausa para ver qué pasa
            
            accion_final = cerebro.decidir_accion_automatica(juego.pos_capitan, algoritmo)
            
            if accion_final:
                print(f"Acción decidida: {Colores.VERDE_B}{accion_final.upper()}{Colores.RESET}")
            else:
                print(f"{Colores.ROJO_B}¡El Capitán está atascado! No encuentra camino seguro.{Colores.RESET}")
                break

        # Ejecutar paso
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

if __name__ == "__main__":
    main()