import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import signal
from scipy.stats import entropy
import networkx as nx
from collections import deque
import seaborn as sns
from tqdm import tqdm

class Agent:
    """
    Agent class representing a participant in the arbitration system.
    Each agent has its own compliance dynamics and decision-making process.
    """
    def __init__(self, agent_id, compliance_tendency=0.8, 
                 drift_rate=0.05, noise_level=0.1, 
                 phase_coupling_strength=0.3, memory_length=10):
        self.agent_id = agent_id
        self.compliance_tendency = compliance_tendency  # Base tendency to comply
        self.compliance_state = compliance_tendency     # Current compliance state
        self.drift_rate = drift_rate                    # Rate of natural drift
        self.noise_level = noise_level                  # Random noise in decisions
        self.phase_coupling_strength = phase_coupling_strength  # Influence from other agents
        self.decision_history = deque(maxlen=memory_length)    # Recent decisions
        self.phase = np.random.uniform(0, 2*np.pi)            # Current phase in decision cycle
        self.natural_frequency = np.random.uniform(0.05, 0.15)  # Natural decision frequency
        
    def update_phase(self, mean_phase, dt=1.0):
        """Update the agent's phase in the decision cycle"""
        # Kuramoto model for phase synchronization
        phase_diff = np.sin(mean_phase - self.phase)
        self.phase += dt * (self.natural_frequency + self.phase_coupling_strength * phase_diff)
        self.phase = self.phase % (2*np.pi)  # Keep phase between 0 and 2π
        
    def make_decision(self, external_influence=0, arbitration_strength=0.5):
        """
        Make a compliance decision (1 = comply, 0 = non-comply)
        influenced by internal state, external factors, and arbitration
        """
        # Apply natural drift
        self.compliance_state -= self.drift_rate
        
        # Apply external influence and arbitration
        effective_compliance = (1 - arbitration_strength) * self.compliance_state + \
                               arbitration_strength * (self.compliance_tendency + external_influence)
        
        # Ensure bounds
        effective_compliance = max(0, min(1, effective_compliance))
        
        # Make probabilistic decision
        noise = self.noise_level * np.random.randn()
        probability = effective_compliance + noise
        decision = 1 if np.random.random() < probability else 0
        
        # Record decision
        self.decision_history.append(decision)
        
        return decision
    
    def get_recent_compliance_rate(self):
        """Get the compliance rate over recent decisions"""
        if not self.decision_history:
            return self.compliance_tendency
        return sum(self.decision_history) / len(self.decision_history)


class ArbitrationSystem:
    """
    Arbitration system that monitors and influences agent decisions
    to maintain compliance in a phase-locked decision environment.
    """
    def __init__(self, n_agents=10, 
                 network_type='small-world',
                 phase_lock_threshold=0.7,
                 arbitration_strength=0.5,
                 drift_mitigation_factor=0.3,
                 compliance_target=0.8):
        
        # Initialize agent population
        self.n_agents = n_agents
        self.agents = [Agent(i) for i in range(n_agents)]
        
        # Create interaction network
        self.network = self._create_network(network_type)
        
        # Arbitration parameters
        self.phase_lock_threshold = phase_lock_threshold  # Threshold for phase coherence
        self.arbitration_strength = arbitration_strength  # How strongly arbitration affects decisions
        self.drift_mitigation_factor = drift_mitigation_factor  # How aggressively to counter drift
        self.compliance_target = compliance_target  # Target compliance level
        
        # Monitoring variables
        self.phase_coherence_history = []
        self.compliance_rate_history = []
        self.arbitration_actions_history = []
        self.drift_measurements = []
        
    def _create_network(self, network_type):
        """Create agent interaction network of specified type"""
        if network_type == 'fully-connected':
            G = nx.complete_graph(self.n_agents)
        elif network_type == 'small-world':
            G = nx.watts_strogatz_graph(self.n_agents, 4, 0.3)
        elif network_type == 'scale-free':
            G = nx.barabasi_albert_graph(self.n_agents, 2)
        elif network_type == 'random':
            G = nx.erdos_renyi_graph(self.n_agents, 0.2)
        else:
            G = nx.watts_strogatz_graph(self.n_agents, 4, 0.3)  # Default to small-world
            
        return G
    
    def calculate_phase_coherence(self):
        """Calculate the Kuramoto order parameter (phase coherence)"""
        phases = np.array([agent.phase for agent in self.agents])
        complex_op = np.mean(np.exp(1j * phases))
        return np.abs(complex_op)
    
    def calculate_mean_phase(self):
        """Calculate the mean phase across all agents"""
        phases = np.array([agent.phase for agent in self.agents])
        complex_op = np.mean(np.exp(1j * phases))
        return np.angle(complex_op)
    
    def measure_compliance_drift(self, window_size=10):
        """Measure compliance drift over recent history"""
        if len(self.compliance_rate_history) < window_size:
            return 0
            
        recent = np.array(self.compliance_rate_history[-window_size:])
        if len(recent) < 2:
            return 0
            
        # Calculate drift as slope of linear regression
        x = np.arange(len(recent))
        A = np.vstack([x, np.ones(len(x))]).T
        slope, _ = np.linalg.lstsq(A, recent, rcond=None)[0]
        return slope
    
    def calculate_external_influence(self, agent_id):
        """Calculate external influence from connected agents"""
        neighbors = list(self.network.neighbors(agent_id))
        if not neighbors:
            return 0
            
        # Get compliance states of neighbors
        neighbor_compliance = [self.agents[n].get_recent_compliance_rate() for n in neighbors]
        return np.mean(neighbor_compliance) - self.agents[agent_id].get_recent_compliance_rate()
    
    def apply_arbitration(self):
        """Apply arbitration based on phase coherence and compliance drift"""
        # Get current phase coherence
        coherence = self.calculate_phase_coherence()
        self.phase_coherence_history.append(coherence)
        
        # Measure drift
        drift = self.measure_compliance_drift()
        self.drift_measurements.append(drift)
        
        # Calculate desired arbitration response to drift
        if drift < 0:  # If compliance is decreasing
            drift_response = -self.drift_mitigation_factor * drift
        else:
            drift_response = 0  # Don't act on positive drift (increasing compliance)
        
        # Adjust arbitration based on phase coherence
        if coherence > self.phase_lock_threshold:
            # High coherence - apply stronger arbitration
            effective_arbitration = self.arbitration_strength + drift_response
        else:
            # Low coherence - apply weaker arbitration
            effective_arbitration = 0.8 * self.arbitration_strength + drift_response
            
        # Ensure bounds
        effective_arbitration = max(0, min(1, effective_arbitration))
        self.arbitration_actions_history.append(effective_arbitration)
        
        return effective_arbitration
    
    def step(self):
        """Advance the system by one time step"""
        # Update phases
        mean_phase = self.calculate_mean_phase()
        for agent in self.agents:
            agent.update_phase(mean_phase)
        
        # Apply arbitration
        arbitration_strength = self.apply_arbitration()
        
        # Collect agent decisions
        decisions = []
        for i, agent in enumerate(self.agents):
            external_influence = self.calculate_external_influence(i)
            decision = agent.make_decision(external_influence, arbitration_strength)
            decisions.append(decision)
        
        # Record compliance rate
        compliance_rate = sum(decisions) / len(decisions)
        self.compliance_rate_history.append(compliance_rate)
        
        return decisions, compliance_rate, arbitration_strength
    
    def run_simulation(self, n_steps=1000):
        """Run simulation for specified number of steps"""
        results = {
            'compliance_rates': [],
            'phase_coherence': [],
            'arbitration_strength': [],
            'drift_measurements': []
        }
        
        for _ in tqdm(range(n_steps)):
            _, compliance_rate, arbitration = self.step()
            results['compliance_rates'].append(compliance_rate)
            results['phase_coherence'].append(self.phase_coherence_history[-1])
            results['arbitration_strength'].append(arbitration)
            results['drift_measurements'].append(self.drift_measurements[-1] if self.drift_measurements else 0)
            
        return pd.DataFrame(results)


class ExperimentSuite:
    """
    A suite of experiments to test different arbitration strategies 
    against various compliance drift scenarios.
    """
    def __init__(self):
        self.results = {}
        
    def run_scenario(self, scenario_name, n_agents=20, n_steps=500, **kwargs):
        """Run a specific scenario with given parameters"""
        print(f"Running scenario: {scenario_name}")
        system = ArbitrationSystem(n_agents=n_agents, **kwargs)
        results = system.run_simulation(n_steps)
        
        # Add to results
        self.results[scenario_name] = {
            'dataframe': results,
            'system': system,
            'parameters': kwargs
        }
        
        return results
    
    def compare_phase_lock_thresholds(self, thresholds=[0.3, 0.5, 0.7, 0.9], n_steps=500):
        """Compare different phase lock thresholds"""
        for threshold in thresholds:
            self.run_scenario(
                f"Phase Threshold {threshold}", 
                phase_lock_threshold=threshold,
                n_steps=n_steps
            )
        self.plot_comparison('phase_lock_threshold', thresholds)
    
    def compare_arbitration_strengths(self, strengths=[0.2, 0.4, 0.6, 0.8], n_steps=500):
        """Compare different arbitration strengths"""
        for strength in strengths:
            self.run_scenario(
                f"Arbitration Strength {strength}", 
                arbitration_strength=strength,
                n_steps=n_steps
            )
        self.plot_comparison('arbitration_strength', strengths)
    
    def compare_network_types(self, types=['fully-connected', 'small-world', 
                                           'scale-free', 'random'], n_steps=500):
        """Compare different network structures"""
        for network_type in types:
            self.run_scenario(
                f"Network {network_type}", 
                network_type=network_type,
                n_steps=n_steps
            )
        self.plot_comparison('network_type', types)
    
    def plot_comparison(self, varied_parameter, values):
        """Plot comparison of results across different parameter values"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Determine scenario names
        if varied_parameter == 'phase_lock_threshold':
            scenarios = [f"Phase Threshold {v}" for v in values]
        elif varied_parameter == 'arbitration_strength':
            scenarios = [f"Arbitration Strength {v}" for v in values]
        elif varied_parameter == 'network_type':
            scenarios = [f"Network {v}" for v in values]
        else:
            scenarios = list(self.results.keys())[-len(values):]
            
        # Plot compliance rates
        for scenario in scenarios:
            if scenario in self.results:
                df = self.results[scenario]['dataframe']
                axes[0, 0].plot(df['compliance_rates'], label=scenario)
        axes[0, 0].set_title('Compliance Rates')
        axes[0, 0].set_xlabel('Time Step')
        axes[0, 0].set_ylabel('Compliance Rate')
        axes[0, 0].legend()
        
        # Plot phase coherence
        for scenario in scenarios:
            if scenario in self.results:
                df = self.results[scenario]['dataframe']
                axes[0, 1].plot(df['phase_coherence'], label=scenario)
        axes[0, 1].set_title('Phase Coherence')
        axes[0, 1].set_xlabel('Time Step')
        axes[0, 1].set_ylabel('Coherence')
        axes[0, 1].legend()
        
        # Plot arbitration strength
        for scenario in scenarios:
            if scenario in self.results:
                df = self.results[scenario]['dataframe']
                axes[1, 0].plot(df['arbitration_strength'], label=scenario)
        axes[1, 0].set_title('Arbitration Strength')
        axes[1, 0].set_xlabel('Time Step')
        axes[1, 0].set_ylabel('Strength')
        axes[1, 0].legend()
        
        # Plot drift measurements
        for scenario in scenarios:
            if scenario in self.results:
                df = self.results[scenario]['dataframe']
                axes[1, 1].plot(df['drift_measurements'], label=scenario)
        axes[1, 1].set_title('Compliance Drift')
        axes[1, 1].set_xlabel('Time Step')
        axes[1, 1].set_ylabel('Drift Rate')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.show()
    
    def visualize_phase_distribution(self, scenario_name, time_step=-1):
        """Visualize the distribution of phases across agents"""
        if scenario_name not in self.results:
            print(f"Scenario {scenario_name} not found")
            return
            
        system = self.results[scenario_name]['system']
        
        # Get phases
        phases = np.array([agent.phase for agent in system.agents])
        
        # Create polar plot
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='polar')
        
        # Plot phases
        ax.scatter(phases, np.ones(len(phases)), c=np.array([
            agent.get_recent_compliance_rate() for agent in system.agents
        ]), cmap='coolwarm', s=100, alpha=0.7)
        
        # Add mean phase
        mean_phase = system.calculate_mean_phase()
        ax.arrow(mean_phase, 0, 0, 0.8, alpha=0.8, width=0.05, 
                 edgecolor='black', facecolor='green', lw=2, zorder=5)
        
        # Add coherence info
        coherence = system.calculate_phase_coherence()
        plt.title(f"Phase Distribution (R={coherence:.2f})")
        
        plt.show()
    
    def visualize_agent_network(self, scenario_name):
        """Visualize the agent interaction network"""
        if scenario_name not in self.results:
            print(f"Scenario {scenario_name} not found")
            return
            
        system = self.results[scenario_name]['system']
        G = system.network
        
        # Get compliance rates as node colors
        compliance_rates = [agent.get_recent_compliance_rate() 
                           for agent in system.agents]
        
        # Create plot
        plt.figure(figsize=(10, 8))
        pos = nx.spring_layout(G, seed=42)
        nx.draw_networkx_nodes(G, pos, node_size=200, 
                              node_color=compliance_rates, 
                              cmap='coolwarm', vmin=0, vmax=1)
        nx.draw_networkx_edges(G, pos, alpha=0.3)
        nx.draw_networkx_labels(G, pos, font_size=10)
        
        plt.title(f"Agent Interaction Network - {scenario_name}")
        plt.colorbar(plt.cm.ScalarMappable(cmap='coolwarm', 
                    norm=plt.Normalize(0, 1)), 
                    label='Compliance Rate')
        plt.axis('off')
        plt.show()


class ComplianceDriftScenario:
    """
    Class to configure specific compliance drift scenarios 
    to test arbitration effectiveness
    """
    @staticmethod
    def create_sudden_shift(system, magnitude=-0.3, time_step=100, affected_agents=0.5):
        """
        Create a scenario with sudden compliance shift
        
        Args:
            system: ArbitrationSystem to modify
            magnitude: Size of compliance shift (-1 to 1)
            time_step: When the shift occurs
            affected_agents: Fraction of agents affected (0 to 1)
        """
        original_step = system.step
        
        def modified_step():
            step_count = len(system.compliance_rate_history)
            
            # If this is the shift time step
            if step_count == time_step:
                # Apply sudden shift to a subset of agents
                n_affected = int(affected_agents * system.n_agents)
                affected_indices = np.random.choice(
                    range(system.n_agents), n_affected, replace=False)
                
                for idx in affected_indices:
                    new_compliance = system.agents[idx].compliance_tendency + magnitude
                    new_compliance = max(0.1, min(0.9, new_compliance))
                    system.agents[idx].compliance_tendency = new_compliance
                    system.agents[idx].compliance_state = new_compliance
                    
                print(f"Applied sudden shift of {magnitude} to {n_affected} agents at step {time_step}")
                
            return original_step()
            
        system.step = modified_step
        return system
    
    @staticmethod
    def create_gradual_drift(system, rate=-0.001, start_step=50, end_step=300):
        """
        Create a scenario with gradual compliance drift
        
        Args:
            system: ArbitrationSystem to modify
            rate: Rate of compliance change per step
            start_step: When drift begins
            end_step: When drift ends
        """
        original_step = system.step
        
        def modified_step():
            step_count = len(system.compliance_rate_history)
            
            # If in drift period
            if start_step <= step_count < end_step:
                # Apply gradual drift to all agents
                for agent in system.agents:
                    new_compliance = agent.compliance_tendency + rate
                    new_compliance = max(0.1, min(0.9, new_compliance))
                    agent.compliance_tendency = new_compliance
                    
            return original_step()
            
        system.step = modified_step
        return system
    
    @staticmethod
    def create_oscillating_environment(system, period=50, amplitude=0.2):
        """
        Create a scenario with oscillating compliance environment
        
        Args:
            system: ArbitrationSystem to modify
            period: Period of oscillation in time steps
            amplitude: Amplitude of oscillation (0 to 1)
        """
        original_step = system.step
        
        def modified_step():
            step_count = len(system.compliance_rate_history)
            
            # Calculate oscillation effect
            oscillation = amplitude * np.sin(2 * np.pi * step_count / period)
            
            # Apply oscillation to environment (affects all agents)
            for agent in system.agents:
                # Store original tendency if not already stored
                if not hasattr(agent, 'original_compliance_tendency'):
                    agent.original_compliance_tendency = agent.compliance_tendency
                
                # Apply oscillation to base tendency
                agent.compliance_tendency = agent.original_compliance_tendency + oscillation
                agent.compliance_tendency = max(0.1, min(0.9, agent.compliance_tendency))
                
            return original_step()
            
        system.step = modified_step
        return system


def run_drift_experiments():
    """Run a comprehensive set of experiments on compliance drift"""
    
    # Initialize experiment suite
    suite = ExperimentSuite()
    
    # Baseline scenario (no drift)
    baseline = suite.run_scenario("Baseline", n_steps=300)
    
    # Sudden compliance shift scenarios
    system = ArbitrationSystem(n_agents=30)
    shifted_system = ComplianceDriftScenario.create_sudden_shift(
        system, magnitude=-0.3, time_step=100)
    shifted_results = shifted_system.run_simulation(n_steps=300)
    suite.results["Sudden Shift"] = {
        'dataframe': shifted_results,
        'system': shifted_system,
        'parameters': {'scenario': 'sudden_shift'}
    }
    
    # Gradual drift scenarios
    system = ArbitrationSystem(n_agents=30)
    drift_system = ComplianceDriftScenario.create_gradual_drift(
        system, rate=-0.001, start_step=50, end_step=200)
    drift_results = drift_system.run_simulation(n_steps=300)
    suite.results["Gradual Drift"] = {
        'dataframe': drift_results,
        'system': drift_system,
        'parameters': {'scenario': 'gradual_drift'}
    }
    
    # Oscillating environment
    system = ArbitrationSystem(n_agents=30)
    oscillating_system = ComplianceDriftScenario.create_oscillating_environment(
        system, period=50, amplitude=0.2)
    oscillating_results = oscillating_system.run_simulation(n_steps=300)
    suite.results["Oscillating"] = {
        'dataframe': oscillating_results,
        'system': oscillating_system,
        'parameters': {'scenario': 'oscillating'}
    }
    
    # Compare drift scenarios
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 2, 1)
    plt.plot(suite.results["Baseline"]['dataframe']['compliance_rates'], label="Baseline")
    plt.plot(suite.results["Sudden Shift"]['dataframe']['compliance_rates'], label="Sudden Shift")
    plt.plot(suite.results["Gradual Drift"]['dataframe']['compliance_rates'], label="Gradual Drift")
    plt.plot(suite.results["Oscillating"]['dataframe']['compliance_rates'], label="Oscillating")
    plt.title("Compliance Rates Across Scenarios")
    plt.xlabel("Time Steps")
    plt.ylabel("Compliance Rate")
    plt.legend()
    
    plt.subplot(2, 2, 2)
    plt.plot(suite.results["Baseline"]['dataframe']['phase_coherence'], label="Baseline")
    plt.plot(suite.results["Sudden Shift"]['dataframe']['phase_coherence'], label="Sudden Shift")
    plt.plot(suite.results["Gradual Drift"]['dataframe']['phase_coherence'], label="Gradual Drift")
    plt.plot(suite.results["Oscillating"]['dataframe']['phase_coherence'], label="Oscillating")
    plt.title("Phase Coherence Across Scenarios")
    plt.xlabel("Time Steps")
    plt.ylabel("Coherence")
    plt.legend()
    
    plt.subplot(2, 2, 3)
    plt.plot(suite.results["Baseline"]['dataframe']['arbitration_strength'], label="Baseline")
    plt.plot(suite.results["Sudden Shift"]['dataframe']['arbitration_strength'], label="Sudden Shift")
    plt.plot(suite.results["Gradual Drift"]['dataframe']['arbitration_strength'], label="Gradual Drift")
    plt.plot(suite.results["Oscillating"]['dataframe']['arbitration_strength'], label="Oscillating")
    plt.title("Arbitration Response Across Scenarios")
    plt.xlabel("Time Steps")
    plt.ylabel("Arbitration Strength")
    plt.legend()
    
    plt.subplot(2, 2, 4)
    plt.plot(suite.results["Baseline"]['dataframe']['drift_measurements'], label="Baseline")
    plt.plot(suite.results["Sudden Shift"]['dataframe']['drift_measurements'], label="Sudden Shift")
    plt.plot(suite.results["Gradual Drift"]['dataframe']['drift_measurements'], label="Gradual Drift")
    plt.plot(suite.results["Oscillating"]['dataframe']['drift_measurements'], label="Oscillating")
    plt.title("Measured Drift Across Scenarios")
    plt.xlabel("Time Steps")
    plt.ylabel("Drift Rate")
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    # Compare network topologies for drift resilience
    suite.compare_network_types()
    
    # Compare arbitration strategies
    suite.compare_arbitration_strengths([0.2, 0.5, 0.8])
    suite.compare_phase_lock_thresholds([0.3, 0.6, 0.9])
    
    # Visualize agent networks
    suite.visualize_agent_network("Baseline")
    suite.visualize_agent_network("Sudden Shift")
    
    # Visualize phase distributions
    suite.visualize_phase_distribution("Baseline")
    suite.visualize_phase_distribution("Sudden Shift")
    
    return suite


if __name__ == "__main__":
    suite = run_drift_experiments()
    
    # Additional analysis of results could be added here
    print("Experiment suite complete. Results available in the 'suite.results' dictionary.")
