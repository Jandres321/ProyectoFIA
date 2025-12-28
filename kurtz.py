from entorno import Palacio
from agente import AgenteLogico, Colores # Usamos la clase Colores que ya tienes en agente.py
import sys

def interpretar_perceptos(p):
    """Traduce los booleanos a texto COLOREADO para que coincida con el mapa."""
    txt = []
    # Usamos los mismos colores que la leyenda del mapa
    if p[0]: txt.append(f"{Colores.CYAN}Brisa{Colores.RESET}")       # Frío/Aire
    if p[1]: txt.append(f"{Colores.AMARILLO}Ronquido{Colores.RESET}") # Precaución
    if p[2]: txt.append(f"{Colores.BLANCO_B}Resplandor{Colores.RESET}") # Luz
    if p[7]: txt.append(f"{Colores.ROJO_B}¡GRITO!{Colores.RESET}")    # Muerte confirmada
    
    # Paredes (Opcional, pero útil)
    paredes = []
    if p[3]: paredes.append("N")
    if p[4]: paredes.append("E")
    if p[5]: paredes.append("S")
    if p[6]: paredes.append("O")
    if paredes:
        txt.append(f"{Colores.NEGRO}(Muros: {''.join(paredes)}){Colores.RESET}")

    return ", ".join(txt) if txt else f"{Colores.NEGRO}Silencio absoluto...{Colores.RESET}"

def main():
    print(f"{Colores.VERDE_B}--- BUSCANDO AL CORONEL KURTZ (Modo Lógico) ---{Colores.RESET}")
    juego = Palacio()
    cerebro = AgenteLogico(juego.n)
    
    # Cheat sheet (opcional)
    # juego.imprimir_tablero_cheat() 
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos
        perceptos = juego.obtener_perceptos()
        
        # 2. Razonar
        cerebro.razonar(juego.pos_capitan, perceptos)
        
        # 3. Dibujar
        cerebro.imprimir_mapa_mental(juego.pos_capitan, juego.kurtz_encontrado)
        
        # --- INTERFAZ DE USUARIO MEJORADA ---
        print(f"{Colores.MAGENTA}Perceptos:{Colores.RESET} {interpretar_perceptos(perceptos)}")
        
        if juego.kurtz_encontrado:
            print(f"{Colores.AMARILLO_B}>>> OBJETIVO: ¡LLEVA A KURTZ A LA SALIDA (Resplandor)! <<<{Colores.RESET}")
        else:
            print(f"{Colores.AZUL}>>> OBJETIVO: Encuentra a Kurtz (está en una celda segura).{Colores.RESET}")
        
        # 4. Input usuario
        print(f"{Colores.NEGRO}Controles: WASD (Mover), G (Granada), E (Salir), Q (Rendirse){Colores.RESET}")
        
        # El input también puede tener color en la pregunta
        accion_raw = input(f"{Colores.VERDE_B}Orden:{Colores.RESET} ").lower().strip()
        
        if accion_raw == 'q': 
            print("El Capitán abandona la misión.")
            break
        
        accion_final = None
        
        # Lógica de input para Granada
        if accion_raw == 'g':
            if juego.granada_usada:
                print(f"{Colores.ROJO}>>> ¡Ya no te quedan granadas! <<<{Colores.RESET}")
                continue
            
            dir_granada = input(f"¿Hacia dónde lanzar? ({Colores.BLANCO_B}w/a/s/d{Colores.RESET}): ").lower().strip()
            if dir_granada in ['w', 'a', 's', 'd']:
                accion_final = 'g' + dir_granada
            else:
                print("Dirección inválida. Lanzamiento cancelado.")
                continue
        elif accion_raw in ['w', 'a', 's', 'd', 'e']:
            accion_final = accion_raw
            
        # Ejecutar paso
        if accion_final:
            nuevos_perceptos, terminado, mensaje = juego.paso(accion_final)
            
            # Imprimimos el mensaje de lo que ha pasado con un separador visual
            print(f"\n{Colores.BLANCO_B}>> {mensaje} <<{Colores.RESET}\n") 
            
            # --- LÓGICA DE FIN DE JUEGO ---
            if terminado:
                jugando = False 
                
                if "MISIÓN CUMPLIDA" in mensaje:
                    # VICTORIA EN VERDE
                    print(f"\n{Colores.VERDE_B}" + "🌟" * 15)
                    print("     VICTORIA TOTAL     ")
                    print(" Has rescatado a Kurtz  ")
                    print("🌟" * 15 + f"{Colores.RESET}\n")
                else:
                    # DERROTA EN ROJO SANGRE
                    print(f"\n{Colores.ROJO_B}" + "☠️ " * 10)
                    print("     GAME OVER      ")
                    print(f"  {mensaje}  ")
                    print("☠️ " * 10 + f"{Colores.RESET}\n")
        else:
            print("Acción inválida.")

if __name__ == "__main__":
    main()