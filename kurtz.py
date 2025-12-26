from entorno import Palacio
import sys

def interpretar_perceptos(p):
    """Traduce la lista de booleanos a texto legible."""
    # p = [Brisa, Ronquido, Resplandor, ParN, ParE, ParS, ParW, Grito]
    txt = []
    if p[0]: txt.append("Sientes una BRISA fría.")
    if p[1]: txt.append("Escuchas un RONQUIDO cercano.")
    if p[2]: txt.append("Ves un RESPLANDOR.")
    if p[7]: txt.append("¡Escuchas un GRITO de agonía!")
    
    walls = []
    if p[3]: walls.append("Norte")
    if p[4]: walls.append("Este")
    if p[5]: walls.append("Sur")
    if p[6]: walls.append("Oeste")
    if walls: txt.append(f"Paredes en: {', '.join(walls)}")
    
    if not txt: return "Silencio absoluto..."
    return " | ".join(txt)

def main():
    print("--- BUSCANDO AL CORONEL KURTZ (Modo Manual) ---")
    juego = Palacio()
    
    # Imprimir el mapa real para que puedas comprobar si los perceptos son ciertos
    juego.imprimir_tablero_cheat()
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos
        perceptos = juego.obtener_perceptos()
        
        # 2. Mostrar estado al usuario
        print(f"\nPosición actual: {juego.pos_capitan}")
        if juego.kurtz_encontrado:
            print("** ¡KURTZ VA CONTIGO! Dirígete a la salida **")
        print(f"PERCEPCIÓN: {interpretar_perceptos(perceptos)}")
        
        # 3. Pedir acción
        accion = input("Acción (w/a/s/d moverse, e salir, q rendirse): ").lower().strip()
        
        if accion == 'q':
            print("El Capitán Willard abandona la misión.")
            break
            
        if accion in ['w', 'a', 's', 'd', 'e']:
            # 4. Ejecutar paso
            nuevos_perceptos, terminado, mensaje = juego.paso(accion)
            
            if terminado:
                print("\n" + "!"*30)
                print(mensaje)
                print("!"*30)
                jugando = False
        else:
            print("Acción no reconocida. Usa W, A, S, D para moverte.")

if __name__ == "__main__":
    main()