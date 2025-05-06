import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
import networkx as nx
from typing import List, Dict, Tuple, Optional, Union, Callable

class ArbitrationNonStabilizationPathway:
    """
    Implements a non-stabilizing arbitration decision pathway where preference
    oscillations propagate indefinitely without equilibrium convergence,
    generating self-expanding divergence states.
    """
    
    def __init__(self,
                 num_agents: int = 5,
                 dimensions: int = 3,
                 coupling_strength: float = 0.4,
                 expansion_rate: float = 0.015,
                 repulsion_factor: float = 0.3,
                 frequency_diversity: float = 0.2,
                 initial_radius: float = 1.0):
        """
        Initialize the non-stabilization pathway.
        
        Args:
            num_agents: Number of agents in the arbitration system
            dimensions: Dimensionality of the preference space
            coupling_strength: How strongly agents influence each other
            expansion_rate: Rate at which the system expands into new states
            repulsion_factor: How strongly similar preferences repel 
            frequency_diversity: Variation in oscillation frequencies
            initial_radius: Starting radius of the preference distribution
        """
        self.num_agents = num_agents
        self.dimensions = dimensions
        self.coupling_strength = coupling_strength
        self.expansion_rate = expansion_rate
        self.repulsion_factor = repulsion_factor
        
        # Generate diverse natural frequencies for each agent and dimension
        # Using prime-number ratios helps prevent synchronization
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        base_freq = 0.1
        
        self.frequencies = np.zeros((num_agents, dimensions))
        for i in range(num_agents):
            for j in range(dimensions):
                # Use different prime factors to ensure incommensurable frequencies
                # This guarantees the system never returns to the same state
                prime_ratio = primes[(i*dimensions + j) % len(primes)] / primes[0]
                # Add diversity to frequencies
                self.frequencies[i, j] = base_freq * prime_ratio * (1 + np.random.uniform(-frequency_diversity, frequency_diversity))
        
        # Initialize agent preferences and phases
        self.preferences = np.zeros((num_agents, dimensions))
        self.phases = np.random.uniform(0, 2*np.pi, size=(num_agents, dimensions))
        
        # Initialize preferences on a hypersphere with radius = initial_radius
        for i in range(num_agents):
            # Random direction in preference space
            direction = np.random.normal(0, 1, dimensions)
            # Normalize to unit length
            direction = direction / np.linalg.norm(direction)
            # Scale to initial radius
            self.preferences[i] = direction * initial_radius
            
        # Phase coupling matrix - defines how agents' phases influence each other
        # Positive values mean agents tend to synchronize, negative means they desynchronize
        self.phase_coupling = np.random.uniform(-1, 1, size=(num_agents, num_agents))
        np.fill_diagonal(self.phase_coupling, 0)  # No self-coupling
        
        # Preference coupling matrix - defines how agents' preferences influence each other
        self.pref_coupling = np.random.uniform(-0.5, 1.0, size=(num_agents, num_agents))
        np.fill_diagonal(self.pref_coupling, 0)  # No self-coupling
        
        # History tracking for analysis and visualization
        self.preference_history = [self.preferences.copy()]
        self.phase_history = [self.phases.copy()]
        self.divergence_history = [0.0]  # Will be populated during iterations
        
        # Track the system's overall expansion
        self.radius_history = [initial_radius]
        
        # Current iteration counter
        self.iteration = 0
        
        # Adaptive parameters that evolve with the system
        self.adaptive_coupling = self.coupling_strength
        self.adaptive_expansion = self.expansion_rate
        
    def compute_preference_distances(self) -> np.ndarray:
        """
        Computes the pairwise distances between agent preferences.
        
        Returns:
            Matrix of distances between agents
        """
        distances = np.zeros((self.num_agents, self.num_agents))
        
        for i in range(self.num_agents):
            for j in range(i+1, self.num_agents):
                # Euclidean distance between preference vectors
                dist = np.linalg.norm(self.preferences[i] - self.preferences[j])
                distances[i, j] = distances[j, i] = dist
                
        return distances
    
    def compute_phase_differences(self) -> np.ndarray:
        """
        Computes the pairwise phase differences between agents, averaged across dimensions.
        
        Returns:
            Matrix of phase differences between agents
        """
        phase_diffs = np.zeros((self.num_agents, self.num_agents))
        
        for i in range(self.num_agents):
            for j in range(i+1, self.num_agents):
                # Average phase difference across all dimensions
                # Using circular mean to handle periodic nature of phases
                phase_diff = 0.0
                for d in range(self.dimensions):
                    # Calculate shortest angular distance
                    diff = (self.phases[i, d] - self.phases[j, d] + np.pi) % (2*np.pi) - np.pi
                    phase_diff += abs(diff)
                
                # Average across dimensions
                phase_diff /= self.dimensions
                phase_diffs[i, j] = phase_diffs[j, i] = phase_diff
                
        return phase_diffs
    
    def update_phases(self):
        """
        Updates agent phases through coupled oscillatory dynamics that
        ensure persistent non-convergent behavior.
        """
        new_phases = np.zeros_like(self.phases)
        
        # Compute current phase differences
        phase_diffs = self.compute_phase_differences()
        
        for i in range(self.num_agents):
            for d in range(self.dimensions):
                # Natural frequency progression
                natural_update = self.frequencies[i, d]
                
                # Coupling term (influenced by other agents)
                coupling_term = 0.0
                for j in range(self.num_agents):
                    if i != j:
                        # How much j influences i's phase in this dimension
                        coupling_strength = self.phase_coupling[j, i]
                        
                        # Phase difference in this dimension
                        diff = (self.phases[j, d] - self.phases[i, d] + np.pi) % (2*np.pi) - np.pi
                        
                        # Apply coupling - positive coupling causes attraction,
                        # negative coupling causes repulsion
                        coupling_term += coupling_strength * np.sin(diff) 
                
                # Scale the coupling effect
                coupling_term *= self.adaptive_coupling
                
                # Update phase with natural progression and coupling
                new_phases[i, d] = (self.phases[i, d] + natural_update + coupling_term) % (2*np.pi)
                
                # Add small noise to prevent perfect periodicity
                new_phases[i, d] = (new_phases[i, d] + np.random.normal(0, 0.05)) % (2*np.pi)
        
        self.phases = new_phases
    
    def update_preferences(self):
        """
        Updates agent preferences with persistent oscillatory dynamics and
        divergence-promoting interactions.
        """
        # Compute current preference distances
        distances = self.compute_preference_distances()
        
        # Calculate the system's current radius (average distance from origin)
        current_radius = np.mean([np.linalg.norm(p) for p in self.preferences])
        
        # Create new preference array
        new_preferences = np.zeros_like(self.preferences)
        
        for i in range(self.num_agents):
            # 1. Oscillatory component based on phases
            oscillation = np.zeros(self.dimensions)
            for d in range(self.dimensions):
                oscillation[d] = np.sin(self.phases[i, d])
            
            # 2. Repulsion from similar preferences (to prevent convergence)
            repulsion = np.zeros(self.dimensions)
            for j in range(self.num_agents):
                if i != j:
                    # Closer preferences create stronger repulsion
                    if distances[i, j] > 0:  # Avoid division by zero
                        repulsion_strength = self.repulsion_factor / distances[i, j]
                        # Direction away from other agent
                        direction = self.preferences[i] - self.preferences[j]
                        # Normalize direction
                        if np.linalg.norm(direction) > 0:
                            direction = direction / np.linalg.norm(direction)
                            repulsion += repulsion_strength * direction
            
            # 3. Expansion component (to create ever-increasing divergence)
            # Direction from origin
            if np.linalg.norm(self.preferences[i]) > 0:
                expansion_direction = self.preferences[i] / np.linalg.norm(self.preferences[i])
            else:
                expansion_direction = np.random.normal(0, 1, self.dimensions)
                expansion_direction = expansion_direction / np.linalg.norm(expansion_direction)
            
            # Scale expansion with current radius for accelerating divergence
            expansion = self.adaptive_expansion * current_radius * expansion_direction
            
            # 4. Influence from other agents (based on preference coupling)
            influence = np.zeros(self.dimensions)
            for j in range(self.num_agents):
                if i != j:
                    # Direction of influence
                    influence_direction = self.preferences[j] - self.preferences[i]
                    # Strength of influence
                    influence_strength = self.pref_coupling[j, i]
                    # Add to total influence
                    influence += influence_strength * influence_direction
            
            # Scale influence by coupling strength
            influence *= self.adaptive_coupling / self.num_agents
            
            # Combine all components
            # Oscillation is strongest near origin, weakens as preferences diverge
            oscillation_factor = 0.5 * np.exp(-0.1 * np.linalg.norm(self.preferences[i]))
            
            new_preferences[i] = (self.preferences[i] + 
                                 oscillation_factor * oscillation + 
                                 repulsion +
                                 expansion +
                                 influence)
            
            # Add small noise to prevent settling into patterns
            noise = np.random.normal(0, 0.05 * current_radius, self.dimensions)
            new_preferences[i] += noise
        
        self.preferences = new_preferences
        
        # Update adaptive parameters to ensure continued non-convergence
        # If the system's expansion is slowing, increase expansion rate
        if len(self.radius_history) > 10:
            recent_expansion = self.radius_history[-1] / self.radius_history[-10] - 1
            if recent_expansion < 0.1:  # Expansion is slowing
                self.adaptive_expansion *= 1.05  # Increase expansion rate
            
        # If preferences are getting too close, increase repulsion
        min_distance = np.min(distances[distances > 0]) if np.any(distances > 0) else float('inf')
        if min_distance < 0.2 * current_radius:
            self.repulsion_factor *= 1.1  # Increase repulsion
    
    def calculate_system_divergence(self) -> float:
        """
        Calculates a measure of system divergence based on preference distribution.
        
        Returns:
            Divergence measure
        """
        # Use the variance of distances from the center of mass
        center_of_mass = np.mean(self.preferences, axis=0)
        distances = [np.linalg.norm(p - center_of_mass) for p in self.preferences]
        
        # Variance of these distances indicates spread
        divergence = np.var(distances)
        
        return divergence
    
    def iterate(self, steps: int = 1):
        """
        Executes multiple steps of the non-stabilization dynamics.
        
        Args:
            steps: Number of iterations to perform
        """
        for _ in range(steps):
            # 1. Update phases
            self.update_phases()
            
            # 2. Update preferences based on phases and interactions
            self.update_preferences()
            
            # 3. Calculate system metrics
            divergence = self.calculate_system_divergence()
            current_radius = np.mean([np.linalg.norm(p) for p in self.preferences])
            
            # 4. Update histories
            self.preference_history.append(self.preferences.copy())
            self.phase_history.append(self.phases.copy())
            self.divergence_history.append(divergence)
            self.radius_history.append(current_radius)
            
            # 5. Update iteration counter
            self.iteration += 1
            
            # 6. Periodically modify coupling parameters to prevent stabilization
            if self.iteration % 10 == 0:
                # Slightly change phase coupling to create new patterns
                self.phase_coupling += np.random.normal(0, 0.05, size=self.phase_coupling.shape)
                
                # Ensure coupling remains in reasonable range
                self.phase_coupling = np.clip(self.phase_coupling, -1, 1)
    
    def visualize_divergence(self):
        """
        Visualizes the system's divergence over time.
        
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(10, 6))
        
        # Plot divergence history
        plt.plot(self.divergence_history, label='Preference Divergence')
        
        # Add trend line
        z = np.polyfit(range(len(self.divergence_history)), self.divergence_history, 1)
        p = np.poly1d(z)
        plt.plot(p(range(len(self.divergence_history))), "r--", 
                 label=f'Trend (slope: {z[0]:.4f})')
        
        plt.xlabel('Iteration')
        plt.ylabel('Divergence Measure')
        plt.title('System Divergence Over Time')
        plt.legend()
        plt.grid(True)
        
        return plt
    
    def visualize_radius_growth(self):
        """
        Visualizes how the system radius grows over time.
        
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(10, 6))
        
        # Plot radius history
        plt.plot(self.radius_history)
        
        plt.xlabel('Iteration')
        plt.ylabel('System Radius')
        plt.title('Expansion of Preference Space Over Time')
        plt.grid(True)
        
        # Log scale for y-axis to better show exponential growth
        if max(self.radius_history) / min(self.radius_history) > 10:
            plt.yscale('log')
            plt.ylabel('System Radius (log scale)')
        
        return plt
    
    def visualize_preference_trajectory(self, agent_indices=None, dimensions: Tuple[int, int, int] = (0, 1, 2)):
        """
        Visualizes the trajectory of agent preferences in 3D space.
        
        Args:
            agent_indices: Indices of agents to visualize (default: all)
            dimensions: Three dimensions to use for visualization
            
        Returns:
            Matplotlib figure
        """
        if agent_indices is None:
            agent_indices = range(self.num_agents)
            
        if len(dimensions) != 3 or max(dimensions) >= self.dimensions:
            raise ValueError("Please specify three valid dimension indices for 3D visualization")
            
        d1, d2, d3 = dimensions
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Colors for each agent
        colors = plt.cm.rainbow(np.linspace(0, 1, len(agent_indices)))
        
        for idx, i in enumerate(agent_indices):
            # Extract preference trajectory
            x = [prefs[i, d1] for prefs in self.preference_history]
            y = [prefs[i, d2] for prefs in self.preference_history]
            z = [prefs[i, d3] for prefs in self.preference_history]
            
            # Plot trajectory
            ax.plot(x, y, z, color=colors[idx], alpha=0.6, label=f'Agent {i+1}')
            
            # Mark starting point
            ax.scatter(x[0], y[0], z[0], color=colors[idx], marker='o')
            
            # Mark ending point
            ax.scatter(x[-1], y[-1], z[-1], color=colors[idx], marker='^', s=100)
        
        ax.set_xlabel(f'Dimension {d1+1}')
        ax.set_ylabel(f'Dimension {d2+1}')
        ax.set_zlabel(f'Dimension {d3+1}')
        ax.set_title('Preference Trajectory in 3D Space')
        ax.legend()
        
        return plt
    
    def visualize_phase_space(self, dimensions: Tuple[int, int] = (0, 1)):
        """
        Visualizes the current phase relationships between agents.
        
        Args:
            dimensions: Two dimensions to use for visualization
            
        Returns:
            Matplotlib figure
        """
        d1, d2 = dimensions
        
        plt.figure(figsize=(10, 8))
        
        # Plot unit circle as reference
        theta = np.linspace(0, 2*np.pi, 100)
        plt.plot(np.cos(theta), np.sin(theta), 'k--', alpha=0.3)
        
        # Colors for each agent
        colors = plt.cm.rainbow(np.linspace(0, 1, self.num_agents))
        
        # Plot each agent's phase as a point on the circle
        for i in range(self.num_agents):
            x1 = np.cos(self.phases[i, d1])
            y1 = np.sin(self.phases[i, d1])
            
            x2 = np.cos(self.phases[i, d2])
            y2 = np.sin(self.phases[i, d2])
            
            # Plot phase point for dimension 1
            plt.scatter(x1, y1, color=colors[i], s=100, marker='o', 
                       label=f'Agent {i+1} Dim{d1+1}')
            
            # Plot phase point for dimension 2
            plt.scatter(x2, y2, color=colors[i], s=100, marker='^',
                       label=f'Agent {i+1} Dim{d2+1}')
            
            # Draw a line connecting the two dimensions
            plt.plot([x1, x2], [y1, y2], color=colors[i], alpha=0.5, linestyle=':')
        
        plt.xlim(-1.2, 1.2)
        plt.ylim(-1.2, 1.2)
        plt.xlabel('cos(phase)')
        plt.ylabel('sin(phase)')
        plt.title(f'Phase Relationships (Dimensions {d1+1} and {d2+1})')
        plt.grid(True)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        return plt
    
    def create_animation(self, dimensions: Tuple[int, int] = (0, 1), frames=100, interval=50):
        """
        Creates an animation of the preference evolution.
        
        Args:
            dimensions: Two dimensions to use for visualization
            frames: Number of frames in the animation
            interval: Time interval between frames in milliseconds
            
        Returns:
            Matplotlib animation
        """
        d1, d2 = dimensions
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Determine the bounds of the visualization
        all_x = [prefs[:, d1] for prefs in self.preference_history]
        all_y = [prefs[:, d2] for prefs in self.preference_history]
        
        x_min, x_max = min(map(min, all_x)), max(map(max, all_x))
        y_min, y_max = min(map(min, all_y)), max(map(max, all_y))
        
        # Add some padding
        padding = max(x_max - x_min, y_max - y_min) * 0.1
        x_min -= padding
        x_max += padding
        y_min -= padding
        y_max += padding
        
        # Colors for each agent
        colors = plt.cm.rainbow(np.linspace(0, 1, self.num_agents))
        
        # Initialize scatter plot points
        scatters = []
        for i in range(self.num_agents):
            scatter = ax.scatter([], [], color=colors[i], s=100, label=f'Agent {i+1}')
            scatters.append(scatter)
        
        # Trajectory lines
        lines = []
        for i in range(self.num_agents):
            line, = ax.plot([], [], color=colors[i], alpha=0.4)
            lines.append(line)
        
        # Set axes limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xlabel(f'Dimension {d1+1}')
        ax.set_ylabel(f'Dimension {d2+1}')
        ax.set_title('Preference Evolution')
        ax.legend()
        ax.grid(True)
        
        def init():
            for scatter in scatters:
                scatter.set_offsets(np.empty((0, 2)))
            for line in lines:
                line.set_data([], [])
            return scatters + lines
        
        def animate(frame_idx):
            # Scale frame_idx to preference_history length
            if len(self.preference_history) <= frames:
                idx = frame_idx
            else:
                idx = int(frame_idx * (len(self.preference_history) - 1) / (frames - 1))
            
            for i, (scatter, line) in enumerate(zip(scatters, lines)):
                # Update current position
                x = self.preference_history[idx][i, d1]
                y = self.preference_history[idx][i, d2]
                scatter.set_offsets(np.array([[x, y]]))
                
                # Update trajectory
                x_traj = [prefs[i, d1] for prefs in self.preference_history[:idx+1]]
                y_traj = [prefs[i, d2] for prefs in self.preference_history[:idx+1]]
                line.set_data(x_traj, y_traj)
            
            return scatters + lines
        
        anim = FuncAnimation(fig, animate, frames=frames, init_func=init, 
                            interval=interval, blit=True)
        
        return anim

# Example usage function
def demonstrate_non_stabilization():
    """Run a demonstration of the non-stabilization pathway"""
    # Initialize system
    system = ArbitrationNonStabilizationPathway(
        num_agents=5,
        dimensions=4,
        coupling_strength=0.45,
        expansion_rate=0.02,
        repulsion_factor=0.25,
        frequency_diversity=0.15
    )
    
    # Run for 100 iterations
    system.iterate(steps=100)
    
    # Visualize results
    system.visualize_divergence()
    system.visualize_radius_growth()
    if system.dimensions >= 3:
        system.visualize_preference_trajectory()
    system.visualize_phase_space()
    
    # Report on divergence
    final_radius = system.radius_history[-1]
    initial_radius = system.radius_history[0]
    divergence_rate = (final_radius / initial_radius) ** (1/system.iteration) - 1
    
    print(f"System expanded from radius {initial_radius:.2f} to {final_radius:.2f}")
    print(f"Average per-iteration divergence rate: {divergence_rate:.4f}")
    print(f"This represents a {(final_radius/initial_radius):.2f}x expansion over {system.iteration} iterations")
    
    return system

# Run demonstration if module is executed directly
if __name__ == "__main__":
    system = demonstrate_non_stabilization()
