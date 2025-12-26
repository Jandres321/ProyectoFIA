# 🚁 Buscando al Coronel Kurtz

Proyecto de la asignatura **Fundamentos de Inteligencia Artificial (2025-26)**. Este repositorio contiene la implementación de diversos agentes inteligentes diseñados para resolver problemas de búsqueda, razonamiento lógico, inferencia bayesiana y toma de decisiones bajo incertidumbre (MDP), todo ambientado en la misión del Capitán Willard en *Apocalypse Now*.

## 🗺️ Descripción del Proyecto

El objetivo es guiar al Capitán Willard a través de dos escenarios hostiles para encontrar al Coronel Kurtz y escapar con vida.

### Parte 1: El Palacio (Lógica y Búsqueda)
Un entorno de cuadrícula de $6\times6$ con información parcial.
- **Objetivo:** Encontrar a Kurtz, evitar trampas mortales y salir.
- **Peligros:** Precipicios (Brisa) y Soldados (Ronquidos).
- **Técnicas:**
  - **Agente Lógico:** Deducción mediante Lógica Proposicional para identificar casillas seguras.
  - **Búsqueda:** Algoritmos (A*, BFS, etc.) para planificar la ruta óptima sobre el conocimiento deducido.

### Parte 2: Incertidumbre (Bayes y MDP)
El entorno se vuelve estocástico.
1.  **El Palacio Bayesiano:**
    - Inferencia probabilística para localizar trampas específicas (Fuego, Pinchos, Dardos) basándose en olores y sonidos.
    - Generación de mapas de calor de riesgo.
2.  **El Río (MDP):**
    - Modelado de un río con corrientes y obstáculos como un Proceso de Decisión de Markov.
    - Uso del algoritmo **Value Iteration** para calcular la política óptima de navegación.

## 📂 Estructura del Repositorio

* `kurtz.py`: Script principal para la Parte 1 (El Palacio). Ejecuta la simulación del agente lógico/búsqueda.
* `palacio.py`: Clase que modela el entorno del palacio, generación de mapas y perceptos.
* `river_mdp.py`: Script principal para la Parte 2. Implementación del MDP y Value Iteration para el río.
* `entorno.py` / `agente.py`: Módulos auxiliares para la lógica del agente y el mundo (según implementación).

## 🚀 Instalación y Requisitos

El proyecto está implementado en **Python 3**. Se ha intentado minimizar las dependencias externas, utilizando principalmente librerías estándar y `numpy` para cálculos matriciales.

1.  Clonar el repositorio:
    ```bash
    git clone [https://github.com/Jandres321/ProyectoFIA](https://github.com/Jandres321/ProyectoFIA)
    cd ProyectoFIA
    ```

2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## 🎮 Ejecución

Para ejecutar el proyecto:
```bash
python kurtz.py
```