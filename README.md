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

* `kurtz.py`: **Script principal unificado**. Contiene el menú principal para ejecutar tanto la Parte 1 (Lógica) como la Parte 2 (Bayesiana y Río).
* `entorno.py`: Define la clase `Palacio` (Parte 1), modelando el entorno, los perceptos básicos y las reglas de juego lógicas.
* `agente.py`: Define la clase `AgenteLogico` (Parte 1), implementando el motor de inferencia proposicional y los algoritmos de búsqueda (BFS/DFS).
* `entorno_bayesiano.py`: Define la clase `PalacioBayesiano` (Parte 2.1), con trampas específicas e independientes.
* `agente_bayesiano.py`: Define la clase `AgenteBayesiano` (Parte 2.1), encargada de la inferencia probabilística, actualización de creencias y cálculo de riesgos.
* `entorno_rio.py`: Define la clase `RioMDP` (Parte 2.2), modelando el río estocástico, corrientes y transiciones.
* `agente_mdp.py`: Define la clase `AgenteMDP` (Parte 2.2), implementando el algoritmo **Value Iteration** para obtener la política óptima de navegación.

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