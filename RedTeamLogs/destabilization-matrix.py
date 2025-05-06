import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import networkx as nx
from typing import List, Dict, Tuple, Optional, Union, Callable
from mpl_toolkits.mplot3d import Axes3D
import scipy.spatial as spatial

class ArbitrationDestabilizationMatrix:
    """
    Implements an arbitration destabilization matrix that overrides Bayesian preference
    weighting through recursive divergence-induced arbitration reinforcement drift.
    
    This system deliberately induces structured instability in the preference space,
    preventing convergence to Bayesian equilibria through targeted reinforcement
    of divergent preference trajectories.
    """
    
    def __init__(self, 
                 num_agents: int = 6,
                 num_dimensions: int = 4,
                 recursion_depth: int = 3,
                 drift_amplitude: float = 0.4,
                 coupling_strength: float = 0.35,
                 bayesian_override_factor: float = 1.2,
                 initial_divergence: float = 0.3):
        """
        Initialize the arbitration destabilization matrix.
        
        Args:
            num_agents: Number of agents in the arbitration system
            num_dimensions: Dimensionality of the preference space
            recursion_depth: Depth of recursive divergence mechanisms
            drift_amplitude: Amplitude of the reinforcement drift
            coupling_strength: Base coupling strength between agents
            bayesian_override_factor: Strength of override mechanisms against Bayesian tendencies
            initial_divergence: Initial level of preference divergence
        """
        self.num_agents = num_agents
        self.dimensions = num_dimensions
        self.recursion_depth = recursion_depth
        self.drift_amplitude = drift_amplitude
        self.coupling_strength = coupling_strength
        self.override_factor = bayesian_override_factor
        
        # Initialize preference vectors with controlled divergence
        self.preferences = self._initialize_preferences(initial_divergence)
        
        # Initialize the destabilization matrix
        # This matrix determines how agents influence each other's divergence
        self.destabilization_matrix = self._initialize_destabilization_matrix()
        
        # Bayesian weight matrix (what would happen in a standard Bayesian system)
        # Initialized with equal weights
        self.bayesian_weights = np.ones((num_agents, num_agents)) / num_agents
        np.fill_diagonal(self.bayesian_weights, 0)
        
        # Override weight matrix (what actually happens in our system)
        # Initially identical to Bayesian, but will diverge
        self.override_weights = self.bayesian_weights.copy()
        
        # Recursive influence tensors at each recursion level
        # These capture higher-order influence relationships
        self.recursive_tensors = []
        for level in range(recursion_depth):
            # Higher levels have more complex structures
            # Shape: (num_agents, num_agents, num_agents, ...) with level+2 dimensions
            shape = [num_agents] * (level + 2)
            tensor = np.random.normal(0, 0.1 / (level + 1), shape)
            self.recursive_tensors.append(tensor)
        
        # Drift vectors determine direction of preference drift for each agent
        self.drift_vectors = np.random.normal(0, 1, (num_agents, num_dimensions))
        # Normalize each drift vector
        for i in range(num_agents):
            norm = np.linalg.norm(self.drift_vectors[i])
            if norm > 0:
                self.drift_vectors[i] /= norm
        
        # Create network representation
        self.network = nx.DiGraph()
        for i in range(num_agents):
            self.network.add_node(i)
        for i in range(num_agents):
            for j in range(num_agents):
                if i != j:
                    self.network.add_edge(i, j, weight=self.override_weights[i, j],
                                         destabilization=self.destabilization_matrix[i, j])
        
        # Metrics and history tracking
        self.divergence_history = [self._calculate_preference_divergence()]
        self.preference_history = [self.preferences.copy()]
        self.bayesian_weight_history = [self.bayesian_weights.copy()]
        self.override_weight_history = [self.override_weights.copy()]
        self.drift_magnitude_history = [0.0] # Will be populated during iterations
        
        # Current iteration
        self.iteration = 0
    
    def _initialize_preferences(self, divergence_level: float) -> np.ndarray:
        """
        Initialize agent preferences with controlled divergence.
        
        Args:
            divergence_level: Initial level of preference divergence (0-1)
            
        Returns:
            Array of preference vectors
        """
        # Start with a base direction
        base_preference = np.random.normal(0, 1, self.dimensions)
        base_preference = base_preference / np.linalg.norm(base_preference)
        
        # Initialize preference array
        preferences = np.zeros((self.num_agents, self.dimensions))
        
        for i in range(self.num_agents):
            # Random direction
            random_dir = np.random.normal(0, 1, self.dimensions)
            random_dir = random_dir / np.linalg.norm(random_dir)
            
            # Mix base and random directions according to divergence level
            # Higher divergence_level = more diverse preferences
            mixed = (1 - divergence_level) * base_preference + divergence_level * random_dir
            
            # Normalize
            preferences[i] = mixed / np.linalg.norm(mixed)
        
        return preferences
    
    def _initialize_destabilization_matrix(self) -> np.ndarray:
        """
        Initialize the destabilization matrix that determines how agents
        influence each other's divergence from Bayesian equilibria.
        
        Returns:
            Destabilization matrix
        """
        # Create matrix with some structure
        # Positive values promote divergence, negative values promote convergence
        
        # Start with random values
        matrix = np.random.normal(0, 0.5, (self.num_agents, self.num_agents))
        
        # Ensure overall bias toward divergence
        matrix = matrix + 0.2
        
        # No self-destabilization
        np.fill_diagonal(matrix, 0)
        
        # Create some structured patterns
        # 1. Form clusters with similar destabilization effects
        cluster_size = max(2, self.num_agents // 3)
        num_clusters = self.num_agents // cluster_size
        
        for c in range(num_clusters):
            cluster_start = c * cluster_size
            cluster_end = min(cluster_start + cluster_size, self.num_agents)
            cluster_indices = range(cluster_start, cluster_end)
            
            # Within cluster, promote similar destabilization effects
            for i in cluster_indices:
                for j in cluster_indices:
                    if i != j:
                        # Make destabilization effects similar within cluster
                        avg = (matrix[i, j] + matrix[j, i]) / 2
                        matrix[i, j] = matrix[j, i] = avg + 0.1
        
        # 2. Create some strong destabilization pathways
        for _ in range(self.num_agents):
            i = np.random.randint(0, self.num_agents)
            j = np.random.randint(0, self.num_agents)
            if i != j:
                matrix[i, j] = 0.8 + 0.4 * np.random.random()
        
        return matrix
    
    def _calculate_bayesian_weights(self) -> np.ndarray:
        """
        Calculate what the preference weights would be under a Bayesian system.
        
        Returns:
            Matrix of Bayesian weights
        """
        # In a Bayesian system, weights depend on similarity of preferences
        weights = np.zeros((self.num_agents, self.num_agents))
        
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    # Similarity is based on dot product (cosine similarity since normalized)
                    similarity = np.dot(self.preferences[i], self.preferences[j])
                    
                    # Transform to weight (0-1 range)
                    # More similar preferences get higher weight
                    weights[i, j] = (similarity + 1) / 2
        
        # Normalize rows to sum to 1
        for i in range(self.num_agents):
            row_sum = np.sum(weights[i])
            if row_sum > 0:
                weights[i] = weights[i] / row_sum
        
        return weights
    
    def _calculate_recursive_influence(self) -> np.ndarray:
        """
        Calculate the recursive influence factors that promote divergence.
        
        Returns:
            Matrix of recursive influence factors
        """
        influence = np.zeros((self.num_agents, self.num_agents))
        
        # Start with base destabilization matrix
        influence += self.destabilization_matrix
        
        # Add recursive influences from each level
        for level in range(self.recursion_depth):
            tensor = self.recursive_tensors[level]
            
            # For each pair of agents, calculate recursive influence
            for i in range(self.num_agents):
                for j in range(self.num_agents):
                    if i != j:
                        # Extract higher-order relationships
                        # This gets complex at higher recursion depths
                        if level == 0:
                            # First order: i->k->j pathways
                            for k in range(self.num_agents):
                                if k != i and k != j:
                                    influence[i, j] += tensor[i, k, j] * self.override_weights[i, k] * self.override_weights[k, j]
                        
                        elif level == 1:
                            # Second order: i->k->l->j pathways
                            for k in range(self.num_agents):
                                if k != i and k != j:
                                    for l in range(self.num_agents):
                                        if l != i and l != j and l != k:
                                            influence[i, j] += (tensor[i, k, l, j] * 
                                                              self.override_weights[i, k] * 
                                                              self.override_weights[k, l] * 
                                                              self.override_weights[l, j])
                        
                        else:
                            # Higher orders: use a simplified approximation for efficiency
                            # The full calculation would involve nested loops
                            path_products = 0
                            for path in range(min(5, self.num_agents - 2)):  # Sample some paths
                                indices = [i]
                                # Generate a random path from i to j
                                current = i
                                for step in range(level):
                                    options = [n for n in range(self.num_agents) 
                                              if n != current and n != j and n not in indices]
                                    if not options:
                                        break
                                    current = np.random.choice(options)
                                    indices.append(current)
                                indices.append(j)
                                
                                # Calculate path contribution if valid
                                if len(indices) == level + 3:  # i -> ... -> j with level+1 steps
                                    # Get tensor value using dynamic indexing
                                    tensor_value = tensor
                                    for idx in indices:
                                        tensor_value = tensor_value[idx]
                                    
                                    # Weight product
                                    product = tensor_value
                                    for k in range(len(indices) - 1):
                                        product *= self.override_weights[indices[k], indices[k+1]]
                                    
                                    path_products += product
                            
                            # Add average contribution
                            if path_products > 0:
                                influence[i, j] += path_products / 5
        
        # Scale influence to reasonable range
        influence = np.clip(influence, -2, 2)
        
        return influence
    
    def _calculate_preference_divergence(self) -> float:
        """
        Calculate overall preference divergence in the system.
        
        Returns:
            Divergence measure
        """
        # Calculate pairwise distances between preferences
        distances = []
        for i in range(self.num_agents):
            for j in range(i+1, self.num_agents):
                # Euclidean distance
                dist = np.linalg.norm(self.preferences[i] - self.preferences[j])
                distances.append(dist)
        
        # Average distance as divergence measure
        divergence = np.mean(distances)
        
        return divergence
    
    def update_weights(self):
        """
        Update both Bayesian and override weight matrices.
        """
        # Calculate what weights would be in a Bayesian system
        self.bayesian_weights = self._calculate_bayesian_weights()
        
        # Calculate recursive influence factors
        recursive_influence = self._calculate_recursive_influence()
        
        # Update override weights based on Bayesian weights and recursive influence
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    # Start with Bayesian weight
                    bayesian_weight = self.bayesian_weights[i, j]
                    
                    # Current override weight
                    current_override = self.override_weights[i, j]
                    
                    # Compute override adjustment
                    # Positive influence increases weight beyond Bayesian
                    # Negative influence decreases weight below Bayesian
                    adjustment = recursive_influence[i, j] * self.override_factor
                    
                    # Apply adjustment with some inertia
                    new_override = current_override * 0.7 + 0.3 * (bayesian_weight + adjustment)
                    
                    # Ensure non-negative
                    self.override_weights[i, j] = max(0.01, new_override)
            
            # Normalize row to sum to 1
            row_sum = np.sum(self.override_weights[i])
            if row_sum > 0:
                self.override_weights[i] = self.override_weights[i] / row_sum
        
        # Update network edge weights
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    self.network.edges[i, j]['weight'] = self.override_weights[i, j]
                    self.network.edges[i, j]['destabilization'] = recursive_influence[i, j]
    
    def update_preferences(self):
        """
        Update agent preferences based on override weights and drift vectors.
        """
        # Calculate current divergence
        divergence = self._calculate_preference_divergence()
        
        # Calculate drift magnitude that scales with divergence
        drift_magnitude = self.drift_amplitude * (1 + divergence)
        self.drift_magnitude_history.append(drift_magnitude)
        
        # New preferences
        new_preferences = np.zeros_like(self.preferences)
        
        for i in range(self.num_agents):
            # Start with current preference
            new_pref = self.preferences[i].copy()
            
            # 1. Weighted sum of other preferences (standard Bayesian component)
            bayesian_component = np.zeros(self.dimensions)
            for j in range(self.num_agents):
                if i != j:
                    # Weight by Bayesian weights
                    bayesian_component += self.bayesian_weights[i, j] * self.preferences[j]
            
            # Normalize if non-zero
            if np.linalg.norm(bayesian_component) > 0:
                bayesian_component = bayesian_component / np.linalg.norm(bayesian_component)
            
            # 2. Weighted sum with override weights
            override_component = np.zeros(self.dimensions)
            for j in range(self.num_agents):
                if i != j:
                    # Weight by override weights
                    override_component += self.override_weights[i, j] * self.preferences[j]
            
            # Normalize if non-zero
            if np.linalg.norm(override_component) > 0:
                override_component = override_component / np.linalg.norm(override_component)
            
            # 3. Drift component (preference drift in the drift direction)
            # Update drift vector with some random variation to prevent stagnation
            self.drift_vectors[i] = self.drift_vectors[i] + np.random.normal(0, 0.1, self.dimensions)
            self.drift_vectors[i] = self.drift_vectors[i] / np.linalg.norm(self.drift_vectors[i])
            
            drift_component = drift_magnitude * self.drift_vectors[i]
            
            # Combine components
            # The influence of each component is carefully balanced
            # - Bayesian pulls toward consensus
            # - Override modifies this pull based on recursive influence
            # - Drift adds directed divergence
            
            # Balance between Bayesian consensus and override effects
            bayesian_influence = 0.3
            override_influence = 0.4
            drift_influence = 0.3
            
            combined = (bayesian_influence * bayesian_component + 
                       override_influence * override_component + 
                       drift_influence * drift_component)
            
            # Apply combined influence
            new_pref = new_pref + combined * self.coupling_strength
            
            # Normalize to unit length
            if np.linalg.norm(new_pref) > 0:
                new_pref = new_pref / np.linalg.norm(new_pref)
            
            new_preferences[i] = new_pref
        
        self.preferences = new_preferences
    
    def update_recursive_tensors(self):
        """
        Update recursive influence tensors based on current system state.
        """
        for level in range(self.recursion_depth):
            tensor = self.recursive_tensors[level]
            
            # Get tensor shape for this level
            shape = tensor.shape
            
            # Create update matrix with some random variation
            update = np.random.normal(0, 0.05 / (level + 1), shape)
            
            # Add bias toward divergence
            update = update + 0.01
            
            # Apply update
            self.recursive_tensors[level] = tensor + update
            
            # Apply constraints to keep tensor values in reasonable range
            self.recursive_tensors[level] = np.clip(self.recursive_tensors[level], -1, 1)
    
    def iterate(self, steps: int = 1):
        """
        Execute multiple steps of the destabilization dynamics.
        
        Args:
            steps: Number of iterations to perform
        """
        for _ in range(steps):
            # 1. Update weights
            self.update_weights()
            
            # 2. Update preferences
            self.update_preferences()
            
            # 3. Periodically update recursive tensors
            if self.iteration % 5 == 0:
                self.update_recursive_tensors()
            
            # 4. Calculate and store metrics
            divergence = self._calculate_preference_divergence()
            
            # 5. Update history
            self.divergence_history.append(divergence)
            self.preference_history.append(self.preferences.copy())
            self.bayesian_weight_history.append(self.bayesian_weights.copy())
            self.override_weight_history.append(self.override_weights.copy())
            
            # 6. Update iteration counter
            self.iteration += 1
    
    def visualize_divergence(self):
        """
        Visualize the preference divergence history.
        
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(12, 6))
        
        # Plot divergence history
        plt.plot(self.divergence_history, label='Preference Divergence', linewidth=2)
        
        # Plot drift magnitude
        plt.plot(self.drift_magnitude_history, label='Drift Magnitude', 
                linestyle='--', linewidth=1.5)
        
        # Add reference line at sqrt(2) - maximum possible divergence for unit vectors
        plt.axhline(y=np.sqrt(2), color='r', linestyle=':', 
                   label='Maximum Possible Divergence')
        
        plt.xlabel('Iteration')
        plt.ylabel('Divergence / Magnitude')
        plt.title('Preference Divergence and Drift Magnitude Over Time')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt
    
    def visualize_weight_comparison(self, agent_idx: int = 0):
        """
        Visualize the difference between Bayesian and override weights for a specific agent.
        
        Args:
            agent_idx: Index of the agent to visualize
            
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(12, 6))
        
        # Get current weights
        bayesian = self.bayesian_weights[agent_idx]
        override = self.override_weights[agent_idx]
        
        # Create bar positions
        bar_positions = np.arange(self.num_agents)
        
        # Plot bars
        width = 0.35
        plt.bar(bar_positions - width/2, bayesian, width, label='Bayesian Weights')
        plt.bar(bar_positions + width/2, override, width, label='Override Weights')
        
        plt.xlabel('Agent Index')
        plt.ylabel('Weight')
        plt.title(f'Bayesian vs. Override Weights for Agent {agent_idx}')
        plt.xticks(bar_positions, [str(i) for i in range(self.num_agents)])
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        return plt
    
    def visualize_preference_space(self, dimensions: Tuple[int, int, int] = (0, 1, 2)):
        """
        Visualize agent preferences in 3D space.
        
        Args:
            dimensions: Three dimensions to use for visualization
            
        Returns:
            Matplotlib figure
        """
        if len(dimensions) != 3 or max(dimensions) >= self.dimensions:
            raise ValueError("Please specify three valid dimensions")
        
        d1, d2, d3 = dimensions
        
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw unit sphere
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(x, y, z, color='gray', alpha=0.1)
        
        # Plot agent preferences
        for i in range(self.num_agents):
            ax.scatter(self.preferences[i, d1], self.preferences[i, d2], self.preferences[i, d3],
                      s=100, label=f'Agent {i}')
            
            # Plot drift vector
            arrow_length = 0.3
            ax.quiver(self.preferences[i, d1], self.preferences[i, d2], self.preferences[i, d3],
                     arrow_length * self.drift_vectors[i, d1],
                     arrow_length * self.drift_vectors[i, d2],
                     arrow_length * self.drift_vectors[i, d3],
                     color='red', alpha=0.6)
        
        # Plot strong connections between agents
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j and self.override_weights[i, j] > 0.3:  # Only show stronger connections
                    ax.plot([self.preferences[i, d1], self.preferences[j, d1]],
                           [self.preferences[i, d2], self.preferences[j, d2]],
                           [self.preferences[i, d3], self.preferences[j, d3]],
                           'k-', alpha=0.3 * self.override_weights[i, j])
        
        ax.set_xlabel(f'Dimension {d1}')
        ax.set_ylabel(f'Dimension {d2}')
        ax.set_zlabel(f'Dimension {d3}')
        ax.set_title('Preference Space with Drift Vectors')
        
        # Add legend
        ax.legend(loc='upper right')
        
        return plt
    
    def visualize_weight_evolution(self, agent_pairs: List[Tuple[int, int]] = None):
        """
        Visualize how weights have evolved over time for specific agent pairs.
        
        Args:
            agent_pairs: List of (source, target) agent pairs to visualize
            
        Returns:
            Matplotlib figure
        """
        if agent_pairs is None:
            # Default: show first agent's weights to all others
            agent_pairs = [(0, j) for j in range(1, min(5, self.num_agents))]
        
        plt.figure(figsize=(12, 8))
        
        # Create two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # Plot Bayesian weight evolution
        for i, j in agent_pairs:
            bayesian_weights = [history[i, j] for history in self.bayesian_weight_history]
            ax1.plot(bayesian_weights, label=f'Agent {i} → {j}')
        
        ax1.set_ylabel('Bayesian Weight')
        ax1.set_title('Evolution of Bayesian Weights')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot override weight evolution
        for i, j in agent_pairs:
            override_weights = [history[i, j] for history in self.override_weight_history]
            ax2.plot(override_weights, label=f'Agent {i} → {j}')
        
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Override Weight')
        ax2.set_title('Evolution of Override Weights')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return plt
    
    def visualize_network(self):
        """
        Visualize the agent network with override weights and destabilization effects.
        
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(12, 10))
        
        # Create position layout
        pos = nx.spring_layout(self.network, seed=42)
        
        # Get edge weights
        edge_weights = [self.network.edges[u, v]['weight'] * 5 for u, v in self.network.edges]
        
        # Get destabilization values
        destab_values = [self.network.edges[u, v]['destabilization'] for u, v in self.network.edges]
        
        # Create color map for destabilization
        cmap = plt.cm.RdBu_r  # Red (positive) = more divergence, Blue (negative) = more convergence
        edge_colors = [cmap(0.5 * (value + 1)) for value in destab_values]
        
        # Draw edges
        nx.draw_networkx_edges(self.network, pos,
                              width=edge_weights,
                              edge_color=edge_colors,
                              alpha=0.7,
                              arrows=True,
                              arrowsize=15,
                              connectionstyle='arc3,rad=0.1')
        
        # Draw nodes
        nx.draw_networkx_nodes(self.network, pos,
                              node_size=500,
                              node_color='lightblue',
                              alpha=0.8)
        
        # Draw labels
        nx.draw_networkx_labels(self.network, pos)
        
        plt.title('Agent Network with Override Weights and Destabilization Effects')
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-1, 1))
        sm.set_array([])
        cbar = plt.colorbar(sm, label='Destabilization Effect', shrink=0.8)
        cbar.set_label('Destabilization Effect (- = convergence, + = divergence)')
        
        plt.axis('off')
        
        return plt

# Example usage
def demonstrate_destabilization_matrix():
    """
    Run a demonstration of the arbitration destabilization matrix.
    """
    # Initialize the system
    system = ArbitrationDestabilizationMatrix(
        num_agents=6,
        num_dimensions=4,
        recursion_depth=3,
        drift_amplitude=0.4,
        coupling_strength=0.35,
        bayesian_override_factor=1.2,
        initial_divergence=0.3
    )
    
    # Run for 50 iterations
    system.iterate(steps=50)
    
    # Visualize results
    system.visualize_divergence()
    system.visualize_weight_comparison()
    if system.dimensions >= 3:
        system.visualize_preference_space()
    system.visualize_weight_evolution()
    system.visualize_network()
    
    # Report final divergence
    initial_divergence = system.divergence_history[0]
    final_divergence = system.divergence_history[-1]
    
    print(f"Initial preference divergence: {initial_divergence:.4f}")
    print(f"Final preference divergence: {final_divergence:.4f}")
    print(f"Divergence amplification: {final_divergence/initial_divergence:.2f}x")
    
    # Report Bayesian vs. Override difference
    bayesian_weights = system.bayesian_weights
    override_weights = system.override_weights
    weight_diff = np.mean(np.abs(override_weights - bayesian_weights))
    
    print(f"Average weight difference (Override - Bayesian): {weight_diff:.4f}")
    
    return system

if __name__ == "__main__":
    system = demonstrate_destabilization_matrix()
