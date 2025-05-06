import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import matplotlib.pyplot as plt
from scipy import signal
import random

class PhaseCoherenceDetector:
    """
    Detects phase coherence patterns in multi-agent systems using 
    wavelet transforms and phase synchronization metrics.
    """
    def __init__(self, n_agents, window_size=128, n_frequencies=16):
        self.n_agents = n_agents
        self.window_size = window_size
        self.n_frequencies = n_frequencies
        self.history = {i: deque(maxlen=window_size) for i in range(n_agents)}
        
    def add_observation(self, agent_id, observation):
        """Add new observation for an agent"""
        self.history[agent_id].append(observation)
    
    def compute_wavelet_transform(self, agent_id):
        """Compute continuous wavelet transform for an agent's history"""
        if len(self.history[agent_id]) < self.window_size:
            return None
            
        data = np.array(list(self.history[agent_id]))
        # Using Morlet wavelet for good time-frequency localization
        frequencies = np.logspace(0, 2, self.n_frequencies)
        scales = 1.0 / frequencies
        coefficients, _ = signal.cwt(data, signal.morlet2, scales)
        return coefficients
    
    def extract_phase(self, wavelet_coefficients):
        """Extract phase information from wavelet coefficients"""
        return np.angle(wavelet_coefficients)
    
    def compute_phase_locking_value(self, phase1, phase2):
        """Compute phase locking value between two phase series"""
        complex_phase_diff = np.exp(1j * (phase1 - phase2))
        plv = np.abs(np.mean(complex_phase_diff, axis=1))
        return plv
    
    def compute_coherence_matrix(self):
        """Compute coherence matrix between all agent pairs"""
        if any(len(self.history[i]) < self.window_size for i in range(self.n_agents)):
            return None
            
        coherence_matrix = np.zeros((self.n_frequencies, self.n_agents, self.n_agents))
        
        # Compute wavelet transforms for all agents
        wavelet_transforms = {}
        phase_data = {}
        for i in range(self.n_agents):
            wt = self.compute_wavelet_transform(i)
            if wt is None:
                return None
            wavelet_transforms[i] = wt
            phase_data[i] = self.extract_phase(wt)
        
        # Compute pairwise phase locking values
        for i in range(self.n_agents):
            for j in range(i+1, self.n_agents):
                plv = self.compute_phase_locking_value(phase_data[i], phase_data[j])
                coherence_matrix[:, i, j] = plv
                coherence_matrix[:, j, i] = plv
                
        # Set diagonal to 1 (perfect coherence with self)
        for i in range(self.n_agents):
            coherence_matrix[:, i, i] = 1.0
                
        return coherence_matrix
    
    def compute_global_coherence(self):
        """Compute global coherence metrics"""
        coherence_matrix = self.compute_coherence_matrix()
        if coherence_matrix is None:
            return None
            
        # Mean coherence across all agent pairs
        mean_coherence = np.mean(coherence_matrix, axis=(1, 2))
        
        # Coherence variance (stability measure)
        coherence_variance = np.var(coherence_matrix, axis=(1, 2))
        
        # Entropy of coherence distribution (diversity measure)
        flat_coherence = coherence_matrix.reshape(self.n_frequencies, -1)
        entropy = np.zeros(self.n_frequencies)
        for i in range(self.n_frequencies):
            # Normalize to create probability distribution
            p = flat_coherence[i] / np.sum(flat_coherence[i])
            # Filter zero probabilities to avoid log(0)
            p = p[p > 0]
            entropy[i] = -np.sum(p * np.log2(p))
            
        return {
            'mean_coherence': mean_coherence,
            'coherence_variance': coherence_variance,
            'entropy': entropy,
            'coherence_matrix': coherence_matrix
        }

class CoherenceFeatureExtractor:
    """
    Extracts relevant features from phase coherence data for the RL agent
    """
    def __init__(self, n_frequencies, n_agents):
        self.n_frequencies = n_frequencies
        self.n_agents = n_agents
        
    def extract_features(self, coherence_data):
        if coherence_data is None:
            # Return zero features if not enough data
            return np.zeros(self.n_frequencies * 3 + 3)
            
        features = []
        
        # Global statistics
        features.extend(coherence_data['mean_coherence'])
        features.extend(coherence_data['coherence_variance'])
        features.extend(coherence_data['entropy'])
        
        # Summary statistics across frequencies
        matrix = coherence_data['coherence_matrix']
        features.append(np.mean(matrix))  # Overall mean
        features.append(np.var(matrix))   # Overall variance
        features.append(np.max(matrix) - np.min(matrix))  # Range
        
        return np.array(features)

class DQNNetwork(nn.Module):
    """
    Deep Q-Network for learning arbitration policies
    """
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(DQNNetwork, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.network(x)

class ReplayBuffer:
    """
    Experience replay buffer for DQN
    """
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
        
    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
        
    def sample(self, batch_size):
        batch = random.sample(self.buffer, min(len(self.buffer), batch_size))
        states, actions, rewards, next_states, dones = zip(*batch)
        return states, actions, rewards, next_states, dones
        
    def __len__(self):
        return len(self.buffer)

class ArbitrationController:
    """
    Main controller using RL to adjust arbitration parameters
    """
    def __init__(self, n_agents, n_frequencies=16, n_actions=10, hidden_dim=128, 
                 learning_rate=0.001, gamma=0.99, epsilon_start=1.0,
                 epsilon_end=0.1, epsilon_decay=0.995, buffer_size=10000,
                 batch_size=64):
        self.n_agents = n_agents
        self.n_frequencies = n_frequencies
        self.n_actions = n_actions  # Number of discrete arbitration parameter settings
        
        # Initialize phase coherence detector
        self.coherence_detector = PhaseCoherenceDetector(n_agents, n_frequencies=n_frequencies)
        
        # Initialize feature extractor
        self.feature_extractor = CoherenceFeatureExtractor(n_frequencies, n_agents)
        
        # Calculate input dimension (features from coherence detector)
        input_dim = n_frequencies * 3 + 3  # mean, variance, entropy per frequency + 3 summary stats
        
        # Initialize DQN
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.dqn = DQNNetwork(input_dim, hidden_dim, n_actions).to(self.device)
        self.target_dqn = DQNNetwork(input_dim, hidden_dim, n_actions).to(self.device)
        self.target_dqn.load_state_dict(self.dqn.state_dict())
        
        # Initialize optimizer
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=learning_rate)
        
        # Initialize replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)
        self.batch_size = batch_size
        
        # RL parameters
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        
        # Arbitration parameters (adjusted by the RL agent)
        self.arbitration_params = 0.5 * np.ones(1)  # Starting at middle of range
        
        # Tracking metrics
        self.rewards_history = []
        self.coherence_history = []
        
    def add_observation(self, agent_observations):
        """
        Add new observations for all agents
        agent_observations: dict mapping agent_id to observation
        """
        for agent_id, observation in agent_observations.items():
            self.coherence_detector.add_observation(agent_id, observation)
    
    def get_state(self):
        """Get the current state representation for RL agent"""
        coherence_data = self.coherence_detector.compute_global_coherence()
        features = self.feature_extractor.extract_features(coherence_data)
        
        # Store coherence for tracking
        if coherence_data is not None:
            self.coherence_history.append(np.mean(coherence_data['mean_coherence']))
        
        return features
    
    def select_action(self, state):
        """Select action using epsilon-greedy policy"""
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, self.n_actions)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.dqn(state_tensor)
            return q_values.argmax().item()
    
    def update_arbitration_params(self, action):
        """Update arbitration parameters based on the selected action"""
        # Map discrete action to continuous parameter space
        # This could be more complex for multiple parameters
        self.arbitration_params[0] = action / (self.n_actions - 1)
        return self.arbitration_params
    
    def compute_reward(self, new_coherence_data):
        """
        Compute reward based on coherence improvement and stability
        """
        if new_coherence_data is None or len(self.coherence_history) < 2:
            return 0.0
        
        current_coherence = np.mean(new_coherence_data['mean_coherence'])
        previous_coherence = self.coherence_history[-2]
        
        # Reward has three components:
        # 1. Absolute coherence level
        # 2. Improvement in coherence
        # 3. Stability (low variance)
        coherence_reward = 0.3 * current_coherence
        improvement_reward = 0.5 * max(0, current_coherence - previous_coherence)
        stability_reward = 0.2 * (1.0 - np.mean(new_coherence_data['coherence_variance']))
        
        return coherence_reward + improvement_reward + stability_reward
    
    def train_step(self):
        """Perform one training step using experience replay"""
        if len(self.replay_buffer) < self.batch_size:
            return
            
        # Sample mini-batch from replay buffer
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Compute current Q values
        q_values = self.dqn(states).gather(1, actions.unsqueeze(1))
        
        # Compute target Q values
        with torch.no_grad():
            next_q_values = self.target_dqn(next_states).max(1)[0]
            target_q_values = rewards + self.gamma * next_q_values * (1 - dones)
            
        # Compute loss
        loss = nn.MSELoss()(q_values.squeeze(), target_q_values)
        
        # Update weights
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update epsilon for exploration
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network with current DQN weights"""
        self.target_dqn.load_state_dict(self.dqn.state_dict())
    
    def step(self):
        """
        Perform a full update step:
        1. Get current state
        2. Select action
        3. Apply action (update arbitration parameters)
        4. Get reward
        5. Update Q network
        """
        # Get current state
        state = self.get_state()
        
        # Select action
        action = self.select_action(state)
        
        # Apply action
        self.update_arbitration_params(action)
        
        # Wait for next observations (in a real system)
        # Here we'll assume they come in the next step
        
        # In a complete system, we'd wait for next observations and then:
        # next_state = self.get_state()
        # reward = self.compute_reward(self.coherence_detector.compute_global_coherence())
        # done = False  # Episode end condition
        # self.replay_buffer.add(state, action, reward, next_state, done)
        # loss = self.train_step()
        
        # For now, just return the current parameters
        return self.arbitration_params
    
    def plot_metrics(self):
        """Plot training metrics"""
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(self.rewards_history)
        plt.title('Rewards')
        plt.xlabel('Step')
        plt.ylabel('Reward')
        
        plt.subplot(2, 1, 2)
        plt.plot(self.coherence_history)
        plt.title('Phase Coherence')
        plt.xlabel('Step')
        plt.ylabel('Average Coherence')
        plt.tight_layout()
        plt.show()

class MultiAgentSimulationEnvironment:
    """
    Simulated environment for testing the arbitration controller
    with multi-agent interactions exhibiting phase coherence patterns
    """
    def __init__(self, n_agents, base_frequency=0.1, coupling_strength=0.2):
        self.n_agents = n_agents
        self.base_frequency = base_frequency
        self.coupling_strength = coupling_strength
        self.time = 0
        self.phase_offsets = np.random.uniform(0, 2*np.pi, n_agents)
        self.frequencies = self.base_frequency * np.ones(n_agents)
        
    def step(self, arbitration_params):
        """
        Advance one time step and return agent observations
        
        Args:
            arbitration_params: Parameters affecting agent coupling
            
        Returns:
            Dict mapping agent_id to observation
        """
        # Increase time
        self.time += 1
        
        # Adjust coupling strength based on arbitration parameter
        effective_coupling = self.coupling_strength * arbitration_params[0]
        
        # Calculate agent interactions (phase coupling)
        phase_diffs = np.zeros(self.n_agents)
        for i in range(self.n_agents):
            for j in range(self.n_agents):
                if i != j:
                    phase_diffs[i] += np.sin(self.phase_offsets[j] - self.phase_offsets[i])
        
        # Update phase offsets with coupling
        self.phase_offsets += self.frequencies + effective_coupling * phase_diffs
        
        # Normalize to [0, 2π)
        self.phase_offsets = self.phase_offsets % (2 * np.pi)
        
        # Generate observations (oscillatory signals plus noise)
        observations = {}
        for i in range(self.n_agents):
            signal = np.sin(self.time * self.frequencies[i] + self.phase_offsets[i])
            noise = 0.1 * np.random.randn()
            observations[i] = signal + noise
            
        return observations
    
    def reset(self):
        """Reset the environment"""
        self.time = 0
        self.phase_offsets = np.random.uniform(0, 2*np.pi, self.n_agents)
        
        # Initial observations
        observations = {}
        for i in range(self.n_agents):
            observations[i] = np.sin(self.phase_offsets[i]) + 0.1 * np.random.randn()
            
        return observations

# Simulation Example
def run_simulation(n_steps=1000, n_agents=5):
    # Initialize controller and environment
    controller = ArbitrationController(n_agents=n_agents)
    env = MultiAgentSimulationEnvironment(n_agents=n_agents)
    
    # Initial observations
    observations = env.reset()
    for agent_id, obs in observations.items():
        controller.coherence_detector.add_observation(agent_id, obs)
    
    # Run simulation
    arbitration_params_history = []
    
    for step in range(n_steps):
        # Get arbitration parameters from controller
        arbitration_params = controller.step()
        arbitration_params_history.append(arbitration_params.copy())
        
        # Apply to environment
        observations = env.step(arbitration_params)
        
        # Update controller with new observations
        controller.add_observation(observations)
        
        # Get next state
        next_state = controller.get_state()
        
        # Compute reward
        coherence_data = controller.coherence_detector.compute_global_coherence()
        reward = controller.compute_reward(coherence_data)
        controller.rewards_history.append(reward)
        
        # Add to replay buffer
        state = next_state  # For simplicity, using next_state as current state
        done = (step == n_steps - 1)
        controller.replay_buffer.add(state, 
                                    np.argmax(arbitration_params), 
                                    reward, 
                                    next_state, 
                                    done)
        
        # Train
        controller.train_step()
        
        # Periodically update target network
        if step % 100 == 0:
            controller.update_target_network()
    
    # Plot results
    controller.plot_metrics()
    
    plt.figure(figsize=(10, 4))
    arbitration_params_history = np.array(arbitration_params_history)
    plt.plot(arbitration_params_history)
    plt.title('Arbitration Parameters')
    plt.xlabel('Step')
    plt.ylabel('Parameter Value')
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()
    
    return controller, env, arbitration_params_history

if __name__ == "__main__":
    controller, env, params_history = run_simulation(n_steps=2000, n_agents=8)
