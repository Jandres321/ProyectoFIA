import numpy as np
import random

class AgenteMDP:
    def __init__(self, mdp):
        self.mdp = mdp
        self.V = {}  # Valores de utilidad V(s)
        self.policy = {} # Política óptima pi(s)
        
        # Inicializar valores a 0
        for s in mdp.get_states():
            self.V[s] = 0.0
            self.policy[s] = 'stay' # Default

    def value_iteration(self, gamma=0.9, epsilon=0.001):
        """
        Ejecuta el algoritmo Value Iteration hasta converger.
        V(s) = max_a sum(P(s'|s,a) * [R(s,a,s') + gamma * V(s')])
        """
        states = self.mdp.get_states()
        actions = self.mdp.get_actions()
        
        iteration = 0
        while True:
            delta = 0
            new_V = self.V.copy()
            
            for s in states:
                if s == self.mdp.exit:
                    new_V[s] = 0.0 # El valor del estado terminal suele ser 0 (o la recompensa ya obtenida)
                    continue
                
                # Calcular Q-values para todas las acciones
                action_values = []
                for a in actions:
                    q_val = 0
                    transitions = self.mdp.get_transitions(s, a)
                    
                    for (prob, next_s, reward) in transitions:
                        # Ecuación de Bellman
                        q_val += prob * (reward + gamma * self.V[next_s])
                    
                    action_values.append(q_val)
                
                # Actualizar V(s) con el máximo
                best_value = max(action_values)
                delta = max(delta, abs(best_value - self.V[s]))
                new_V[s] = best_value
            
            self.V = new_V
            iteration += 1
            
            # Condición de parada
            if delta < epsilon:
                print(f"Value Iteration convergió en {iteration} iteraciones.")
                break
        
        self._extract_policy(gamma)

    def _extract_policy(self, gamma):
        """Una vez calculados los V(s), extrae la mejor acción para cada estado."""
        states = self.mdp.get_states()
        actions = self.mdp.get_actions()
        
        for s in states:
            if s == self.mdp.exit:
                self.policy[s] = 'EXIT'
                continue
                
            best_action = None
            best_q = -float('inf')
            
            for a in actions:
                q_val = 0
                transitions = self.mdp.get_transitions(s, a)
                for (prob, next_s, reward) in transitions:
                    q_val += prob * (reward + gamma * self.V[next_s])
                
                if q_val > best_q:
                    best_q = q_val
                    best_action = a
            
            self.policy[s] = best_action

    def get_best_action(self, state):
        return self.policy.get(state, 'stay')