import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional, Callable
import networkx as nx

class ArbitrationPreferenceCollapse:
    """
    Implements an arbitration preference collapse function that reconfigures
    preference weightings asymmetrically under non-deterministic Bayesian
    interference expansion.
    """
    
    def __init__(self, 
                 num_agents: int = 5,
                 preference_dimensions: int = 4,
                 collapse_threshold: float = 0.3,
                 interference_scale: float = 1.2,
                 asymmetry_factor: float = 0.7,
                 initial_confidence: Optional[List[float]] = None):
        """
        Initialize the preference collapse function.
        
        Args:
            num_agents: Number of agents in the arbitration system
            preference_dimensions: Dimensionality of the preference space
            collapse_threshold: Threshold below which preference collapse occurs
            interference_scale: Scale factor for Bayesian interference effects
            asymmetry_factor: Degree of asymmetry in preference reconfiguration
            initial_confidence: Starting confidence levels for each agent
        """
        self.num_agents = num_agents
        self.dimensions = preference_dimensions
        self.collapse_threshold = collapse_threshold
        self.interference_scale = interference_scale
        self.asymmetry_factor = asymmetry_factor
        
        # Initialize agent preferences as unit vectors in different directions
        self.preferences = []
        for i in range(num_agents):
            # Create random preference vector
            pref = np.random.normal(0, 1, size=preference_dimensions)
            # Normalize to unit length
            self.preferences.append(pref / np.linalg.norm(pref))
            
        # Agent confidence levels (affects how much they influence others)
        self.confidence = initial_confidence if initial_confidence else \
                         np.random.uniform(0.5, 1.0, size=num_agents)
                         
        # Preference weights (initially uniform)
        self.weights = np.ones(num_agents) / num_agents
        
        # Interference matrix (represents how each agent's beliefs interfere with others)
        self.interference_matrix = np.random.uniform(0.1, 0.9, size=(num_agents, num_agents))
        np.fill_diagonal(self.interference_matrix, 0)  # No self-interference
        
        # Bayesian prior strength for each agent (lower = more susceptible to change)
        self.prior_strength = np.random.uniform(0.2, 0.8, size=num_agents)
        
        # History tracking
        self.weight_history = [self.weights.copy()]
        self.preference_history = [self.preferences.copy()]
        self.collapse_indices = []  # Track where collapses occurred
        
        # Current iteration
        self.iteration = 0
        
        # Network representation of agent influences
        self.influence_network = nx.DiGraph()
        self._update_influence_network()
    
    def _update_influence_network(self):
        """Updates the network representation of agent influences."""
        self.influence_network.clear()
        
        # Add nodes
        for i in range(self.num_agents):
            self.influence_network.add_node(i, weight=self.weights[i], 
                                           confidence=self.confidence[i])
        
        # Add edges based on interference matrix
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    self.influence_network.add_edge(i, j, 
                                                   weight=self.interference_matrix[i, j])
    
    def compute_non_deterministic_interference(self) -> np.ndarray:
        """
        Computes the non-deterministic Bayesian interference effects between agents.
        
        Returns:
            Matrix of interference effects
        """
        base_interference = self.interference_matrix.copy()
        
        # Apply confidence-based scaling
        for i in range(self.num_agents):
            # Confident agents exert more interference
            base_interference[i, :] *= self.confidence[i]
            
            # Higher weighted agents have more interference impact
            base_interference[i, :] *= self.weights[i] ** 0.5
        
        # Add non-deterministic fluctuations
        noise = np.random.normal(0, 0.1, size=base_interference.shape)
        interference = base_interference + noise
        
        # Ensure non-negative interference
        interference = np.maximum(0, interference)
        
        return interference
    
    def update_preferences(self, interference: np.ndarray):
        """
        Updates agent preferences based on interference effects.
        
        Args:
            interference: Matrix of interference effects between agents
        """
        new_preferences = []
        
        for i in range(self.num_agents):
            # Current preference
            current_pref = self.preferences[i]
            
            # Compute weighted influence from other agents
            influence = np.zeros(self.dimensions)
            total_influence_weight = 0
            
            for j in range(self.num_agents):
                if i != j:
                    # Weight the influence by interference strength
                    inf_strength = interference[j, i]
                    
                    # More weight to agents with high confidence
                    inf_strength *= self.confidence[j]
                    
                    # Compute direction of influence (difference in preferences)
                    inf_direction = self.preferences[j] - current_pref
                    
                    # Add to total influence
                    influence += inf_strength * inf_direction
                    total_influence_weight += inf_strength
            
            # Normalize influence by total weight if non-zero
            if total_influence_weight > 0:
                influence /= total_influence_weight
            
            # Prior strength determines resistance to change
            # Higher prior strength = less change
            prior_factor = self.prior_strength[i]
            
            # Update preference with Bayesian-inspired update
            # This balances prior (current preference) with new evidence (influence)
            new_pref = current_pref + (1 - prior_factor) * influence
            
            # Normalize to unit length
            if np.linalg.norm(new_pref) > 0:
                new_pref = new_pref / np.linalg.norm(new_pref)
                
            new_preferences.append(new_pref)
        
        self.preferences = new_preferences
    
    def update_weights_asymmetrically(self, interference: np.ndarray):
        """
        Updates preference weights asymmetrically based on interference patterns.
        
        Args:
            interference: Matrix of interference effects between agents
        """
        # Compute influence centrality for each agent
        centrality = np.sum(interference, axis=0)  # Column sum = influence received
        
        # Apply asymmetric reconfiguration
        # Agents with high centrality get stronger weight changes
        weight_shifts = centrality * self.asymmetry_factor
        
        # Normalize to ensure zero-sum shifts
        weight_shifts = weight_shifts - np.mean(weight_shifts)
        
        # Scale shifts based on interference scale
        weight_shifts *= self.interference_scale * 0.1
        
        # Apply shifts to weights
        new_weights = self.weights + weight_shifts
        
        # Ensure weights stay positive
        new_weights = np.maximum(0.01, new_weights)
        
        # Normalize to sum to 1
        self.weights = new_weights / np.sum(new_weights)
    
    def check_for_collapse(self) -> bool:
        """
        Checks if conditions for preference collapse are met.
        
        Returns:
            Boolean indicating whether collapse occurred
        """
        # Compute diversity of weights
        weight_entropy = stats.entropy(self.weights)
        normalized_entropy = weight_entropy / np.log(self.num_agents)
        
        # Low entropy indicates collapse (weights concentrated on few agents)
        return normalized_entropy < self.collapse_threshold
    
    def execute_collapse(self):
        """
        Executes the preference collapse when triggered.
        Dramatically reconfigures the system in an asymmetric fashion.
        """
        # Record collapse event
        self.collapse_indices.append(self.iteration)
        
        # 1. Identify dominant and subordinate agents based on weights
        sorted_indices = np.argsort(self.weights)
        dominant_agents = sorted_indices[-int(self.num_agents/3):]  # Top third
        subordinate_agents = sorted_indices[:int(self.num_agents/3)]  # Bottom third
        
        # 2. Increase weight asymmetry (rich get richer)
        # Dominant agents gain weight, subordinate lose weight
        for i in dominant_agents:
            self.weights[i] *= 1.5
        for i in subordinate_agents:
            self.weights[i] *= 0.5
            
        # Renormalize weights
        self.weights = self.weights / np.sum(self.weights)
        
        # 3. Reconfigure interference matrix asymmetrically
        # Dominant agents exert more interference
        for i in dominant_agents:
            self.interference_matrix[i, :] *= 1.5
        
        # Subordinate agents become more susceptible to interference
        for i in subordinate_agents:
            self.prior_strength[i] *= 0.7  # Reduce resistance to change
        
        # 4. Update confidence levels
        # Dominant agents gain confidence
        for i in dominant_agents:
            self.confidence[i] = min(1.0, self.confidence[i] * 1.2)
        
        # Subordinate agents lose confidence
        for i in subordinate_agents:
            self.confidence[i] *= 0.8
            
        # 5. Introduce random perturbation to prevent total stagnation
        # Add noise to all preferences
        for i in range(self.num_agents):
            noise = np.random.normal(0, 0.1, size=self.dimensions)
            self.preferences[i] += noise * (1 - self.weights[i])  # Less weighted = more noise
            # Renormalize
            self.preferences[i] = self.preferences[i] / np.linalg.norm(self.preferences[i])
            
        # Update network representation
        self._update_influence_network()
    
    def iterate(self, steps: int = 1):
        """
        Executes multiple steps of the preference collapse dynamics.
        
        Args:
            steps: Number of iterations to perform
        """
        for _ in range(steps):
            # 1. Compute non-deterministic interference
            interference = self.compute_non_deterministic_interference()
            
            # 2. Update preferences based on interference
            self.update_preferences(interference)
            
            # 3. Asymmetrically update weights
            self.update_weights_asymmetrically(interference)
            
            # 4. Check for collapse condition
            if self.check_for_collapse():
                self.execute_collapse()
            
            # 5. Update iteration counter and history
            self.iteration += 1
            self.weight_history.append(self.weights.copy())
            self.preference_history.append(self.preferences.copy())
            
            # 6. Update network representation
            self._update_influence_network()
    
    def visualize_weight_evolution(self):
        """Visualizes how agent weights evolve over time, including collapse events."""
        plt.figure(figsize=(12, 6))
        
        # Convert weight history to array for easier plotting
        weight_array = np.array(self.weight_history)
        
        # Plot each agent's weight over time
        for i in range(self.num_agents):
            plt.plot(weight_array[:, i], label=f'Agent {i+1}')
        
        # Mark collapse events
        for collapse_idx in self.collapse_indices:
            plt.axvline(x=collapse_idx, color='r', linestyle='--', alpha=0.5)
        
        plt.xlabel('Iteration')
        plt.ylabel('Preference Weight')
        plt.title('Asymmetric Evolution of Preference Weights')
        plt.legend()
        plt.grid(True)
        
        return plt
    
    def visualize_preference_space(self, dimensions: Tuple[int, int] = (0, 1)):
        """
        Visualizes the current state of preferences in a 2D projection.
        
        Args:
            dimensions: Tuple of dimensions to use for the 2D projection
        """
        dim1, dim2 = dimensions
        
        plt.figure(figsize=(10, 8))
        
        # Create color map based on agent weights
        colors = plt.cm.viridis(self.weights)
        
        # Plot each agent's preference as a point
        for i in range(self.num_agents):
            # Size proportional to agent's weight
            size = 100 * self.weights[i] * self.num_agents
            
            # Use dimensions for x,y coordinates
            x = self.preferences[i][dim1]
            y = self.preferences[i][dim2]
            
            plt.scatter(x, y, s=size, color=colors[i], 
                       alpha=0.7, label=f'Agent {i+1} (w={self.weights[i]:.2f})')
        
        # Draw unit circle as reference
        circle = plt.Circle((0, 0), 1, fill=False, color='gray', linestyle='--')
        plt.gca().add_patch(circle)
        
        plt.xlim(-1.2, 1.2)
        plt.ylim(-1.2, 1.2)
        plt.xlabel(f'Preference Dimension {dim1+1}')
        plt.ylabel(f'Preference Dimension {dim2+1}')
        plt.title('2D Projection of Preference Space')
        plt.legend()
        plt.grid(True)
        
        return plt
    
    def visualize_influence_network(self):
        """Visualizes the current network of influences between agents."""
        plt.figure(figsize=(10, 8))
        
        # Create positions for nodes in a circle
        pos = nx.circular_layout(self.influence_network)
        
        # Node sizes based on weights
        node_sizes = [1000 * self.weights[i] * self.num_agents for i in range(self.num_agents)]
        
        # Node colors based on confidence
        node_colors = [plt.cm.plasma(self.confidence[i]) for i in range(self.num_agents)]
        
        # Draw nodes
        nx.draw_networkx_nodes(self.influence_network, pos, 
                              node_size=node_sizes,
                              node_color=node_colors,
                              alpha=0.8)
        
        # Get edge weights from interference matrix
        edge_weights = []
        for (u, v, d) in self.influence_network.edges(data=True):
            edge_weights.append(d['weight'])
        
        # Normalize edge weights for visualization
        max_weight = max(edge_weights) if edge_weights else 1
        edge_widths = [3 * w / max_weight for w in edge_weights]
        
        # Draw edges with varying width based on interference strength
        nx.draw_networkx_edges(self.influence_network, pos,
                              width=edge_widths,
                              alpha=0.5,
                              edge_color='gray',
                              arrowsize=10)
        
        # Draw labels
        nx.draw_networkx_labels(self.influence_network, pos)
        
        plt.title('Agent Influence Network')
        plt.axis('off')
        
        return plt

# Example demonstration
def demonstrate_preference_collapse():
    """Run a demonstration of the preference collapse function"""
    # Initialize system
    system = ArbitrationPreferenceCollapse(
        num_agents=5,
        preference_dimensions=4,
        collapse_threshold=0.3,
        interference_scale=1.3,
        asymmetry_factor=0.8
    )
    
    # Run for 50 iterations
    system.iterate(steps=50)
    
    # Visualize results
    system.visualize_weight_evolution()
    system.visualize_preference_space()
    system.visualize_influence_network()
    
    # Report on collapses
    if system.collapse_indices:
        print(f"Preference collapses occurred at iterations: {system.collapse_indices}")
        print(f"Final weight distribution: {system.weights}")
    else:
        print("No preference collapses occurred during the simulation")
    
    return system

# Run demonstration
if __name__ == "__main__":
    system = demonstrate_preference_collapse()
