from entorno import Palacio
from agente import AgenteLogico # <--- Importamos la nueva clase
import sys

# ... (Mantén la función interpretar_perceptos igual que antes) ...
def interpretar_perceptos(p):
    # (Código anterior de interpretar_perceptos)
    txt = []
    if p[0]: txt.append("Brisa")
    if p[1]: txt.append("Ronquido")
    if p[2]: txt.append("Resplandor")
    if p[7]: txt.append("Grito")
    return ", ".join(txt) if txt else "Nada"

def main():
    print("--- BUSCANDO AL CORONEL KURTZ (Modo Lógico) ---")
    juego = Palacio()
    cerebro = AgenteLogico(juego.n) # <--- Inicializamos el cerebro
    
    # Cheat sheet para ti (opcional, para comparar)
    # juego.imprimir_tablero_cheat() 
    
    jugando = True
    while jugando:
        # 1. Obtener perceptos reales
        perceptos = juego.obtener_perceptos()
        
        # 2. El Agente RAZONA
        cerebro.razonar(juego.pos_capitan, perceptos)
        
        # 3. Mostrar la visión del Agente
        cerebro.imprimir_mapa_mental(juego.pos_capitan)
        
        print(f"Perceptos en {juego.pos_capitan}: {interpretar_perceptos(perceptos)}")
        
        # 4. Input usuario
        accion = input("Acción (w/a/s/d, e, q): ").lower().strip()
        
        if accion == 'q': break
            
        if accion in ['w', 'a', 's', 'd', 'e']:
            nuevos_perceptos, terminado, mensaje = juego.paso(accion)
            if terminado:
                print("\n" + "!"*30)
                print(mensaje)
                print("!"*30)
                jugando = False
        else:
            print("Acción inválida.")

if __name__ == "__main__":
    main()