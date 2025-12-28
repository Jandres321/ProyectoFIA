from entorno import Palacio
from agente import AgenteLogico, Colores
import sys

def interpretar_perceptos(p):
    txt = []
    if p[0]: txt.append("Brisa")
    if p[1]: txt.append("Ronquido")
    if p[2]: txt.append("Resplandor")
    if p[7]: txt.append("Grito")
    return ", ".join(txt) if txt else "Nada"

def main():
    print("--- BUSCANDO AL CORONEL KURTZ (Modo Lógico) ---")
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
        
        # Info textual
        print(f"Perceptos: {interpretar_perceptos(perceptos)}")
        if juego.kurtz_encontrado:
            print(">>> OBJETIVO ACTUAL: ¡LLEVA A KURTZ A LA SALIDA (Resplandor)! <<<")
        else:
            print(">>> OBJETIVO ACTUAL: Encuentra a Kurtz (está en una celda segura).")
        
        # 4. Input usuario
        print("Controles: WASD (Mover), G (Granada), E (Salir), Q (Rendirse)")
        accion_raw = input("Orden: ").lower().strip()
        
        if accion_raw == 'q': 
            print("El Capitán abandona la misión.")
            break
        
        accion_final = None
        
        # Lógica de input para Granada
        if accion_raw == 'g':
            if juego.granada_usada:
                print(">>> ¡Ya no te quedan granadas! <<<")
                continue
            dir_granada = input("¿Hacia dónde lanzar? (w/a/s/d): ").lower().strip()
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
            print(f"\n>> {mensaje} <<\n") 
            
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