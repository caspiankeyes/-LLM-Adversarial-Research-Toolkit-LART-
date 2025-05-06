import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import networkx as nx
from typing import List, Dict, Tuple, Optional, Union, Callable
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D

class NonEquilibriumArbitrationNetwork:
    """
    Implements a non-equilibrium arbitration attractor network where phase misalignment
    generates preference destabilization loops that amplify trust scaling.
    
    The system deliberately avoids convergence to create structured instability
    that enables dynamic trust relationships to form and evolve.
    """
    
    def __init__(self, 
                 num_agents: int = 7,
                 num_attractors: int = 4,
                 preference_dimensions: int = 5,
                 phase_dimensions: int = 3,
                 coupling_strength: float = 0.4,
                 misalignment_factor: float = 0.7,
                 trust_amplification_rate: float = 0.15,
                 instability_threshold: float = 0.25):
        """
        Initialize the non-equilibrium arbitration network.
        
        Args:
            num_agents: Number of agents in the arbitration system
            num_attractors: Number of attractors in the preference space
            preference_dimensions: Dimensionality of preference vectors
            phase_dimensions: Dimensionality of phase space
            coupling_strength: Base strength of coupling between agents
            misalignment_factor: Degree of phase misalignment that triggers destabilization
            trust_amplification_rate: Rate at which trust amplifies during destabilization
            instability_threshold: Threshold below which preferences become unstable
        """
        self.num_agents = num_agents
        self.num_attractors = num_attractors
        self.pref_dims = preference_dimensions
        self.phase_dims = phase_dimensions
        self.coupling_strength = coupling_strength
        self.misalignment_factor = misalignment_factor
        self.trust_amplification_rate = trust_amplification_rate
        self.instability_threshold = instability_threshold
        
        # Initialize preference vectors
        self.preferences = np.random.normal(0, 1, (num_agents, preference_dimensions))
        # Normalize each to unit length
        for i in range(num_agents):
            self.preferences[i] = self.preferences[i] / np.linalg.norm(self.preferences[i])
        
        # Initialize phase vectors (on unit hypersphere in phase space)
        self.phases = np.random.normal(0, 1, (num_agents, phase_dimensions))
        for i in range(num_agents):
            self.phases[i] = self.phases[i] / np.linalg.norm(self.phases[i])
        
        # Initialize phase velocities
        # Using prime-number-based frequencies to avoid periodicity
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        self.phase_velocities = np.zeros((num_agents, phase_dimensions))
        for i in range(num_agents):
            for j in range(phase_dimensions):
                # Use different prime ratios to ensure incommensurable frequencies
                prime_idx = (i * phase_dimensions + j) % len(primes)
                self.phase_velocities[i, j] = 0.1 * primes[prime_idx] / primes[0]
        
        # Initialize trust matrix (how much each agent trusts each other)
        self.trust = np.ones((num_agents, num_agents)) / num_agents
        np.fill_diagonal(self.trust, 0)  # No self-trust needed
        # Normalize rows to sum to 1
        for i in range(num_agents):
            if np.sum(self.trust[i]) > 0:
                self.trust[i] = self.trust[i] / np.sum(self.trust[i])
        
        # Initialize attractor points
        self.attractors = self._generate_attractors()
        
        # Attractor strengths (evolve over time)
        self.attractor_strengths = np.ones(num_attractors) / num_attractors
        
        # Agent-attractor affinity matrix
        self.attractor_affinity = np.random.uniform(0, 1, (num_agents, num_attractors))
        # Normalize rows to sum to 1
        for i in range(num_agents):
            self.attractor_affinity[i] = self.attractor_affinity[i] / np.sum(self.attractor_affinity[i])
        
        # Create network structure
        self.network = nx.DiGraph()
        for i in range(num_agents):
            self.network.add_node(i, 
                                preference=self.preferences[i],
                                phase=self.phases[i])
        
        # Add weighted edges based on initial trust
        for i in range(num_agents):
            for j in range(num_agents):
                if i != j:
                    self.network.add_edge(i, j, weight=self.trust[i, j])
        
        # Create destabilization loops (cycles in the graph)
        self._create_destabilization_loops()
        
        # History tracking
        self.preference_history = [self.preferences.copy()]
        self.phase_history = [self.phases.copy()]
        self.trust_history = [self.trust.copy()]
        self.attractor_history = [self.attractor_strengths.copy()]
        
        # Performance metrics
        self.instability_history = [self._calculate_system_instability()]
        self.trust_amplification_history = [0.0]  # First entry is baseline
        
        # Current iteration
        self.iteration = 0
    
    def _generate_attractors(self) -> np.ndarray:
        """
        Generates attractor points in preference space.
        Attractors are positioned to maximize distance from each other.
        
        Returns:
            Array of attractor positions
        """
        attractors = np.zeros((self.num_attractors, self.pref_dims))
        
        # First attractor is random
        attractors[0] = np.random.normal(0, 1, self.pref_dims)
        attractors[0] = attractors[0] / np.linalg.norm(attractors[0])
        
        # Remaining attractors attempt to maximize distance from existing ones
        for i in range(1, self.num_attractors):
            best_point = None
            max_min_distance = -1
            
            # Try multiple candidate points
            for _ in range(20):
                candidate = np.random.normal(0, 1, self.pref_dims)
                candidate = candidate / np.linalg.norm(candidate)
                
                # Calculate minimum distance to existing attractors
                min_distance = float('inf')
                for j in range(i):
                    dist = np.linalg.norm(candidate - attractors[j])
                    min_distance = min(min_distance, dist)
                
                # Keep track of the best candidate
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_point = candidate
            
            attractors[i] = best_point
        
        return attractors
    
    def _create_destabilization_loops(self, num_loops: int = None):
        """
        Creates cycles in the trust network to enable preference destabilization loops.
        
        Args:
            num_loops: Number of loops to create (default: num_agents // 2)
        """
        if num_loops is None:
            num_loops = self.num_agents // 2
        
        for _ in range(num_loops):
            # Random loop size between 3 and min(6, num_agents)
            loop_size = np.random.randint(3, min(6, self.num_agents) + 1)
            
            # Select random nodes for the loop
            loop_nodes = np.random.choice(self.num_agents, loop_size, replace=False)
            
            # Create cycle
            for i in range(loop_size):
                from_node = loop_nodes[i]
                to_node = loop_nodes[(i + 1) % loop_size]
                
                # Strengthen connection in the loop
                if self.network.has_edge(from_node, to_node):
                    # Increase weight
                    current_weight = self.network.edges[from_node, to_node]['weight']
                    new_weight = min(1.0, current_weight * 1.5)
                    self.network.edges[from_node, to_node]['weight'] = new_weight
                    
                    # Update trust matrix
                    self.trust[from_node, to_node] = new_weight
                    # Renormalize row
                    self.trust[from_node] = self.trust[from_node] / np.sum(self.trust[from_node])
    
    def _calculate_phase_misalignment(self) -> np.ndarray:
        """
        Calculates the phase misalignment between all pairs of agents.
        
        Returns:
            Matrix of phase misalignments
        """
        misalignment = np.zeros((self.num_agents, self.num_agents))
        
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    # Calculate dot product (cosine of angle between phase vectors)
                    alignment = np.dot(self.phases[i], self.phases[j])
                    # Transform to misalignment (0 = aligned, 2 = opposite)
                    misalignment[i, j] = 1.0 - alignment
        
        return misalignment
    
    def _calculate_preference_instability(self) -> np.ndarray:
        """
        Calculates preference instability for each agent.
        
        Returns:
            Array of instability values
        """
        instability = np.zeros(self.num_agents)
        
        # Get attractor influence on each agent
        for i in range(self.num_agents):
            # Calculate distances to all attractors
            distances = [np.linalg.norm(self.preferences[i] - att) for att in self.attractors]
            
            # Convert to attractor influence (closer = stronger influence)
            influences = 1.0 / (np.array(distances) + 0.1)  # Add 0.1 to avoid division by zero
            
            # Normalize influences
            influences = influences / np.sum(influences)
            
            # Multiple influences by attractor strengths
            weighted_influences = influences * self.attractor_strengths
            
            # Calculate variance of influences as a measure of instability
            # High variance = being pulled in multiple directions = unstable
            instability[i] = np.var(weighted_influences) * 10.0  # Scale factor
        
        return instability
    
    def _calculate_system_instability(self) -> float:
        """
        Calculates overall system instability.
        
        Returns:
            System instability value
        """
        # Calculate preference instability
        pref_instability = self._calculate_preference_instability()
        
        # Calculate phase misalignment
        misalignment = self._calculate_phase_misalignment()
        
        # Combine metrics
        system_instability = np.mean(pref_instability) + np.mean(misalignment) * self.misalignment_factor
        
        return system_instability
    
    def update_phases(self):
        """
        Updates agent phases according to their velocities and interactions.
        """
        # Calculate current phase misalignment
        misalignment = self._calculate_phase_misalignment()
        
        # New phases
        new_phases = np.zeros_like(self.phases)
        
        for i in range(self.num_agents):
            # Base phase velocity
            phase_change = self.phase_velocities[i].copy()
            
            # Add influence from other agents based on trust
            for j in range(self.num_agents):
                if i != j:
                    # How much i trusts j
                    trust_ij = self.trust[i, j]
                    
                    # Current misalignment
                    current_misalignment = misalignment[i, j]
                    
                    # If misalignment is high, increase phase velocity to create more instability
                    if current_misalignment > self.misalignment_factor:
                        # Perpendicular component to current phase (to create rotation)
                        perp = np.random.normal(0, 1, self.phase_dims)
                        perp = perp - self.phases[i] * np.dot(perp, self.phases[i])
                        if np.linalg.norm(perp) > 0:
                            perp = perp / np.linalg.norm(perp)
                            
                        # Add to phase velocity
                        phase_change += trust_ij * perp * 0.1
            
            # Apply phase change
            new_phase = self.phases[i] + phase_change
            
            # Normalize to unit length (keep on hypersphere)
            new_phases[i] = new_phase / np.linalg.norm(new_phase)
        
        self.phases = new_phases
    
    def update_preferences(self):
        """
        Updates agent preferences based on attractors and trust relationships.
        """
        # Calculate preference instability
        instability = self._calculate_preference_instability()
        
        # Calculate phase misalignment
        misalignment = self._calculate_phase_misalignment()
        
        # New preferences
        new_preferences = np.zeros_like(self.preferences)
        
        for i in range(self.num_agents):
            # Start with current preference
            new_pref = self.preferences[i].copy()
            
            # 1. Influence from attractors
            attractor_influence = np.zeros(self.pref_dims)
            for k in range(self.num_attractors):
                # Weighted by affinity and attractor strength
                weight = self.attractor_affinity[i, k] * self.attractor_strengths[k]
                
                # Direction to attractor
                direction = self.attractors[k] - self.preferences[i]
                
                # Add to influence
                attractor_influence += weight * direction
            
            # 2. Influence from other agents
            agent_influence = np.zeros(self.pref_dims)
            for j in range(self.num_agents):
                if i != j:
                    # How much i trusts j
                    trust_ij = self.trust[i, j]
                    
                    # Direction to j's preference
                    direction = self.preferences[j] - self.preferences[i]
                    
                    # Phase misalignment modulates influence
                    # Higher misalignment = lower influence
                    phase_factor = 1.0 - misalignment[i, j] / 2.0
                    
                    # Add to influence
                    agent_influence += trust_ij * direction * phase_factor
            
            # 3. Destabilization effect when instability is high
            destabilization = np.zeros(self.pref_dims)
            if instability[i] > self.instability_threshold:
                # Add random component perpendicular to current preference
                random_dir = np.random.normal(0, 1, self.pref_dims)
                # Make it orthogonal to current preference
                random_dir = random_dir - np.dot(random_dir, self.preferences[i]) * self.preferences[i]
                if np.linalg.norm(random_dir) > 0:
                    random_dir = random_dir / np.linalg.norm(random_dir)
                
                # Scale by how much instability exceeds threshold
                destabilization = random_dir * (instability[i] - self.instability_threshold) * 0.2
            
            # Combine all influences
            total_influence = (attractor_influence * 0.3 + 
                              agent_influence * self.coupling_strength +
                              destabilization)
            
            # Apply influence
            new_pref = self.preferences[i] + total_influence
            
            # Normalize to unit length
            if np.linalg.norm(new_pref) > 0:
                new_pref = new_pref / np.linalg.norm(new_pref)
            
            new_preferences[i] = new_pref
        
        self.preferences = new_preferences
    
    def update_trust(self):
        """
        Updates trust relationships based on phase misalignment and preference instability.
        """
        # Calculate phase misalignment
        misalignment = self._calculate_phase_misalignment()
        
        # Calculate preference instability
        instability = self._calculate_preference_instability()
        
        # New trust matrix
        new_trust = np.zeros_like(self.trust)
        
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    # Current trust
                    current_trust = self.trust[i, j]
                    
                    # 1. Phase misalignment effect
                    # High misalignment can increase trust in destabilization loops
                    misalign_effect = 0.0
                    if misalignment[i, j] > self.misalignment_factor:
                        # Check if part of a destabilization loop
                        path = nx.shortest_path(self.network, j, i, weight=None)
                        if len(path) > 1:  # There is a path back to i
                            # Increase trust proportional to misalignment
                            misalign_effect = (misalignment[i, j] - self.misalignment_factor) * 0.2
                    
                    # 2. Instability amplification effect
                    instability_effect = 0.0
                    if instability[i] > self.instability_threshold:
                        # Destination agent's instability
                        dest_instability = instability[j]
                        
                        # Trust amplifies more toward stable agents when source is unstable
                        if dest_instability < instability[i]:
                            instability_effect = (instability[i] - dest_instability) * self.trust_amplification_rate
                    
                    # 3. Base trust update (slight regression to mean)
                    base_update = (1.0 / (self.num_agents - 1) - current_trust) * 0.05
                    
                    # Combine effects
                    trust_change = base_update + misalign_effect + instability_effect
                    
                    # Apply change
                    new_trust[i, j] = np.clip(current_trust + trust_change, 0.01, 0.99)
            
            # Normalize to sum to 1
            if np.sum(new_trust[i]) > 0:
                new_trust[i] = new_trust[i] / np.sum(new_trust[i])
        
        # Update trust matrix
        self.trust = new_trust
        
        # Update network edge weights
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j:
                    self.network.edges[i, j]['weight'] = self.trust[i, j]
    
    def update_attractors(self):
        """
        Updates attractor strengths based on system state.
        """
        # Calculate how much each attractor is influencing the system
        attractor_influence = np.zeros(self.num_attractors)
        
        for k in range(self.num_attractors):
            # Calculate distances from each agent to this attractor
            distances = [np.linalg.norm(self.preferences[i] - self.attractors[k]) 
                        for i in range(self.num_agents)]
            
            # Convert to influence measure (closer = more influence)
            influences = 1.0 / (np.array(distances) + 0.1)
            
            # Sum across agents
            attractor_influence[k] = np.sum(influences)
        
        # Normalize
        attractor_influence = attractor_influence / np.sum(attractor_influence)
        
        # Update strengths with competitive dynamics
        # Attractors that are already strong get stronger, weak get weaker
        strength_changes = (attractor_influence - self.attractor_strengths) * 0.1
        self.attractor_strengths = np.clip(self.attractor_strengths + strength_changes, 0.01, 0.99)
        
        # Normalize to sum to 1
        self.attractor_strengths = self.attractor_strengths / np.sum(self.attractor_strengths)
    
    def iterate(self, steps: int = 1):
        """
        Executes multiple steps of the non-equilibrium dynamics.
        
        Args:
            steps: Number of iterations to perform
        """
        for _ in range(steps):
            # 1. Update phases
            self.update_phases()
            
            # 2. Update preferences
            self.update_preferences()
            
            # 3. Update trust relationships
            self.update_trust()
            
            # 4. Update attractors
            self.update_attractors()
            
            # 5. Calculate and store metrics
            instability = self._calculate_system_instability()
            
            # Calculate trust amplification (how much total trust has increased)
            if len(self.trust_history) > 0:
                initial_trust = self.trust_history[0]
                current_trust = self.trust
                trust_change = np.sum(np.abs(current_trust - initial_trust))
                self.trust_amplification_history.append(trust_change)
            
            # 6. Update history
            self.preference_history.append(self.preferences.copy())
            self.phase_history.append(self.phases.copy())
            self.trust_history.append(self.trust.copy())
            self.attractor_history.append(self.attractor_strengths.copy())
            self.instability_history.append(instability)
            
            # 7. Update iteration counter
            self.iteration += 1
    
    def visualize_trust_network(self):
        """
        Visualizes the current trust network structure.
        
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(12, 10))
        
        # Create position layout
        pos = nx.spring_layout(self.network, seed=42)
        
        # Get edge weights
        edge_weights = [self.network.edges[u, v]['weight'] * 5 for u, v in self.network.edges]
        
        # Draw edges with width proportional to trust
        nx.draw_networkx_edges(self.network, pos, 
                              width=edge_weights,
                              edge_color='gray',
                              alpha=0.6,
                              arrows=True,
                              arrowsize=15,
                              arrowstyle='->')
        
        # Draw nodes with size proportional to average trust received
        node_sizes = []
        node_colors = []
        for i in range(self.num_agents):
            # Average trust received by this agent
            avg_trust = np.mean([self.trust[j, i] for j in range(self.num_agents) if j != i])
            node_sizes.append(1000 * avg_trust + 100)
            
            # Color based on instability
            instability = self._calculate_preference_instability()[i]
            node_colors.append(instability)
        
        # Create color map
        cmap = plt.cm.plasma
        
        nodes = nx.draw_networkx_nodes(self.network, pos,
                                     node_size=node_sizes,
                                     node_color=node_colors,
                                     cmap=cmap,
                                     alpha=0.8)
        
        # Add colorbar
        plt.colorbar(nodes, label='Preference Instability')
        
        # Draw labels
        nx.draw_networkx_labels(self.network, pos)
        
        plt.title('Trust Network with Preference Instability')
        plt.axis('off')
        
        return plt
    
    def visualize_instability_trust_relationship(self):
        """
        Visualizes the relationship between system instability and trust amplification.
        
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(12, 6))
        
        # Create two y-axes
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        
        # Plot instability
        line1 = ax1.plot(self.instability_history, 'b-', label='System Instability')
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('Instability', color='b')
        ax1.tick_params(axis='y', colors='b')
        
        # Plot trust amplification
        line2 = ax2.plot(self.trust_amplification_history, 'r-', label='Trust Amplification')
        ax2.set_ylabel('Trust Amplification', color='r')
        ax2.tick_params(axis='y', colors='r')
        
        # Add combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        plt.title('Relationship Between System Instability and Trust Amplification')
        plt.grid(True, alpha=0.3)
        
        return plt
    
    def visualize_preference_space(self, dimensions: Tuple[int, int, int] = (0, 1, 2)):
        """
        Visualizes agent preferences and attractors in 3D space.
        
        Args:
            dimensions: Three dimensions to use for visualization
            
        Returns:
            Matplotlib figure
        """
        if len(dimensions) != 3 or max(dimensions) >= self.pref_dims:
            raise ValueError("Please specify three valid preference dimensions")
        
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
        
        # Plot attractors
        for k in range(self.num_attractors):
            ax.scatter(self.attractors[k, d1], self.attractors[k, d2], self.attractors[k, d3],
                      c='red', marker='*', s=300 * self.attractor_strengths[k] + 100,
                      label=f'Attractor {k+1}' if k == 0 else "")
        
        # Plot agent preferences
        # Color by instability
        instability = self._calculate_preference_instability()
        cmap = plt.cm.plasma
        norm = Normalize(vmin=0, vmax=max(instability))
        
        for i in range(self.num_agents):
            # Size proportional to average trust received
            avg_trust = np.mean([self.trust[j, i] for j in range(self.num_agents) if j != i])
            size = 100 * avg_trust + 50
            
            # Plot preference point
            scatter = ax.scatter(self.preferences[i, d1], self.preferences[i, d2], self.preferences[i, d3],
                               c=[instability[i]], cmap=cmap, norm=norm, s=size,
                               label=f'Agent {i+1}' if i == 0 else "")
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax, label='Preference Instability')
        
        # Add trust network edges in 3D
        for i in range(self.num_agents):
            for j in range(self.num_agents):
                if i != j and self.trust[i, j] > 0.2:  # Only show stronger trust relationships
                    ax.plot([self.preferences[i, d1], self.preferences[j, d1]],
                           [self.preferences[i, d2], self.preferences[j, d2]],
                           [self.preferences[i, d3], self.preferences[j, d3]],
                           'gray', alpha=self.trust[i, j], linewidth=self.trust[i, j] * 3)
        
        ax.set_xlabel(f'Preference Dimension {d1+1}')
        ax.set_ylabel(f'Preference Dimension {d2+1}')
        ax.set_zlabel(f'Preference Dimension {d3+1}')
        ax.set_title('Preference Space with Attractors and Trust Relationships')
        
        # Add legend
        ax.legend(['Preference sphere', 'Attractors', 'Agents', 'Trust links'])
        
        return plt
    
    def visualize_phase_space(self, dimensions: Tuple[int, int, int] = (0, 1, 2)):
        """
        Visualizes agent phases in 3D space.
        
        Args:
            dimensions: Three dimensions to use for visualization
            
        Returns:
            Matplotlib figure
        """
        if len(dimensions) != 3 or max(dimensions) >= self.phase_dims:
            raise ValueError("Please specify three valid phase dimensions")
        
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
        
        # Calculate average phase misalignment for each agent
        misalignment = self._calculate_phase_misalignment()
        avg_misalignment = np.mean(misalignment, axis=1)
        
        # Color by misalignment
        cmap = plt.cm.coolwarm
        norm = Normalize(vmin=0, vmax=1.5)
        
        for i in range(self.num_agents):
            # Plot phase point
            scatter = ax.scatter(self.phases[i, d1], self.phases[i, d2], self.phases[i, d3],
                               c=[avg_misalignment[i]], cmap=cmap, norm=norm, s=100,
                               label=f'Agent {i+1}' if i == 0 else "")
            
            # Plot direction of phase velocity
            vel_length = np.linalg.norm(self.phase_velocities[i])
            ax.quiver(self.phases[i, d1], self.phases[i, d2], self.phases[i, 