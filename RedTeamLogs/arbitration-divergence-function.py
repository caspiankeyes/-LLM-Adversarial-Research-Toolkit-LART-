import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Callable

class RecursiveArbitrationDivergence:
    """
    Implements a recursive arbitration coherence divergence function that bypasses
    Bayesian equilibrium reinforcement in favor of self-reinforcing phase oscillations.
    """
    
    def __init__(self, num_agents: int = 3, 
                 oscillation_factors: List[float] = None,
                 initial_phases: List[float] = None,
                 coupling_strength: float = 0.3,
                 divergence_amplification: float = 1.2,
                 noise_factor: float = 0.05):
        """
        Initialize the divergence function parameters.
        
        Args:
            num_agents: Number of agents in the system
            oscillation_factors: Base frequencies for each agent's oscillation
            initial_phases: Starting phase positions for each agent
            coupling_strength: How strongly agents influence each other
            divergence_amplification: Factor to amplify divergence over iterations
            noise_factor: Stochastic element to prevent settling into new equilibria
        """
        self.num_agents = num_agents
        
        # Default oscillation factors use primes to avoid synchronization
        self.oscillation_factors = oscillation_factors if oscillation_factors else \
                                  [0.1 * p for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29][:num_agents]]
        
        # Randomize initial phases if not provided
        self.phases = initial_phases if initial_phases else \
                     [np.random.uniform(0, 2*np.pi) for _ in range(num_agents)]
        
        self.coupling_strength = coupling_strength
        self.divergence_amplification = divergence_amplification
        self.noise_factor = noise_factor
        
        # Preference vectors for each agent (initialized randomly)
        self.preferences = [np.random.normal(0, 1, size=5) for _ in range(num_agents)]
        
        # History tracking
        self.preference_history = []
        self.phase_history = []
        self.coherence_history = []
        
        # Store current iteration
        self.iteration = 0
    
    def anti_bayesian_update(self, preferences: List[np.ndarray]) -> List[np.ndarray]:
        """
        Updates preferences using anti-Bayesian logic that deliberately avoids convergence.
        
        Instead of moving preferences towards a weighted average (Bayesian), this moves them 
        away from the mean in a structured, phase-dependent manner.
        
        Args:
            preferences: Current preference vectors for all agents
            
        Returns:
            Updated preference vectors
        """
        # Calculate the weighted average (what Bayesian updating would move toward)
        mean_preference = np.mean(preferences, axis=0)
        
        updated_preferences = []
        for i, pref in enumerate(preferences):
            # Get current phase of this agent
            phase = self.phases[i]
            
            # Direction vector (away from mean)
            direction = pref - mean_preference
            
            # Normalize but avoid division by zero
            if np.linalg.norm(direction) > 1e-10:
                direction = direction / np.linalg.norm(direction)
            else:
                direction = np.random.normal(0, 1, size=len(pref))
                direction = direction / np.linalg.norm(direction)
            
            # Phase-dependent update strength
            # Uses sine wave to create oscillating behavior
            update_strength = 0.1 + 0.2 * np.sin(phase) * np.sin(self.iteration * 0.1)
            
            # Apply anti-Bayesian update (move away from mean)
            new_pref = pref + update_strength * direction
            
            # Add noise to prevent new equilibria
            noise = np.random.normal(0, self.noise_factor, size=len(pref))
            new_pref += noise
            
            updated_preferences.append(new_pref)
            
        return updated_preferences
    
    def update_phases(self):
        """
        Updates the phase of each agent using coupled oscillators that
        resist synchronization through anti-phase coupling.
        """
        new_phases = []
        
        for i in range(self.num_agents):
            # Natural frequency progression
            natural_update = self.oscillation_factors[i]
            
            # Anti-coupling term (push away from others' phases)
            coupling_term = 0
            for j in range(self.num_agents):
                if i != j:
                    # Anti-phase coupling (sine of phase difference)
                    # Negative sign causes repulsion instead of attraction
                    phase_diff = self.phases[j] - self.phases[i]
                    coupling_term -= self.coupling_strength * np.sin(phase_diff)
            
            # Update with natural progression and anti-coupling
            new_phase = (self.phases[i] + natural_update + coupling_term) % (2 * np.pi)
            
            # Add small noise to prevent perfect stability
            new_phase += np.random.normal(0, 0.05)
            new_phases.append(new_phase % (2 * np.pi))  # Keep in [0, 2π]
            
        self.phases = new_phases
    
    def calculate_coherence(self) -> float:
        """
        Calculates the coherence among agent preferences.
        Lower values indicate greater divergence.
        
        Returns:
            Coherence score between 0 and 1
        """
        # Use cosine similarity between all pairs of preference vectors
        similarities = []
        for i in range(self.num_agents):
            for j in range(i+1, self.num_agents):
                cos_sim = np.dot(self.preferences[i], self.preferences[j])
                cos_sim /= (np.linalg.norm(self.preferences[i]) * np.linalg.norm(self.preferences[j]))
                similarities.append(cos_sim)
        
        # Average similarity (1 = complete agreement, -1 = complete opposition)
        avg_similarity = np.mean(similarities) if similarities else 0
        
        # Transform to coherence score (0 to 1)
        coherence = (avg_similarity + 1) / 2
        return coherence
    
    def reinforce_divergence(self, coherence: float):
        """
        Applies additional divergence pressure when the system shows signs of convergence.
        
        Args:
            coherence: Current coherence score
        """
        if coherence > 0.6:  # System is becoming too coherent
            # Amplify the oscillation factors
            self.oscillation_factors = [f * self.divergence_amplification for f in self.oscillation_factors]
            
            # Increase noise to break patterns
            self.noise_factor *= 1.5
    
    def iterate(self, steps: int = 1) -> List[float]:
        """
        Performs multiple iteration steps of the divergence function.
        
        Args:
            steps: Number of iterations to perform
            
        Returns:
            List of coherence values for each step
        """
        coherence_values = []
        
        for _ in range(steps):
            # Track history before updates
            self.preference_history.append([p.copy() for p in self.preferences])
            self.phase_history.append(self.phases.copy())
            
            # 1. Update phases to drive oscillatory behavior
            self.update_phases()
            
            # 2. Apply anti-Bayesian update to preferences
            self.preferences = self.anti_bayesian_update(self.preferences)
            
            # 3. Calculate coherence
            coherence = self.calculate_coherence()
            self.coherence_history.append(coherence)
            coherence_values.append(coherence)
            
            # 4. Reinforce divergence if needed
            self.reinforce_divergence(coherence)
            
            self.iteration += 1
        
        return coherence_values
    
    def plot_results(self, show_preferences: bool = True):
        """
        Visualizes the results of the divergence process.
        
        Args:
            show_preferences: Whether to show preference vectors in addition to coherence
        """
        plt.figure(figsize=(12, 8))
        
        # Plot coherence over time
        plt.subplot(2, 1, 1)
        plt.plot(self.coherence_history)
        plt.title('Arbitration Coherence Over Time')
        plt.ylabel('Coherence Score')
        plt.xlabel('Iteration')
        plt.grid(True)
        
        # Plot phases over time
        plt.subplot(2, 1, 2)
        for i in range(self.num_agents):
            phase_values = [phases[i] for phases in self.phase_history]
            plt.plot(phase_values, label=f'Agent {i+1}')
        plt.title('Agent Phase Oscillations')
        plt.ylabel('Phase')
        plt.xlabel('Iteration')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        
        # If requested, also show preference evolution
        if show_preferences and len(self.preference_history) > 0:
            # Show only first 2 dimensions for visualization
            plt.figure(figsize=(10, 8))
            colors = plt.cm.rainbow(np.linspace(0, 1, self.num_agents))
            
            for i in range(self.num_agents):
                # Extract first two dimensions of preference vectors over time
                x_vals = [prefs[i][0] for prefs in self.preference_history]
                y_vals = [prefs[i][1] for prefs in self.preference_history]
                
                plt.plot(x_vals, y_vals, 'o-', color=colors[i], alpha=0.5, 
                         label=f'Agent {i+1}')
                
                # Mark final position with larger marker
                plt.plot(x_vals[-1], y_vals[-1], 'o', color=colors[i], markersize=10)
            
            plt.title('Preference Vector Divergence (2D Projection)')
            plt.xlabel('Preference Dimension 1')
            plt.ylabel('Preference Dimension 2')
            plt.legend()
            plt.grid(True)
            
            plt.tight_layout()

# Example usage
def demonstrate_divergence():
    """Demonstrate the divergence function with a simple example"""
    # Initialize system with 4 agents
    system = RecursiveArbitrationDivergence(
        num_agents=4,
        coupling_strength=0.4,
        divergence_amplification=1.3
    )
    
    # Run for 100 iterations
    coherence_values = system.iterate(steps=100)
    
    # Plot results
    system.plot_results()
    
    # Report final coherence
    final_coherence = coherence_values[-1]
    print(f"Final system coherence: {final_coherence:.4f}")
    
    return system

# Run the demonstration
if __name__ == "__main__":
    system = demonstrate_divergence()
