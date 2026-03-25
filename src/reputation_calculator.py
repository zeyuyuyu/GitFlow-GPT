import math
from datetime import datetime, timezone

class ReputationCalculator:
    def __init__(self):
        self.trust_scores = {}
        self.interaction_history = {}
        self.decay_factor = 0.1  # Controls how quickly old interactions lose weight
        
    def record_interaction(self, from_node: str, to_node: str, score: float, timestamp=None):
        """Record a trust interaction between nodes with temporal tracking"""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
            
        if from_node not in self.interaction_history:
            self.interaction_history[from_node] = []
            
        self.interaction_history[from_node].append({
            'target': to_node,
            'score': max(min(score, 1.0), -1.0),  # Bound scores between -1 and 1
            'timestamp': timestamp
        })
        
        self._update_trust_scores(from_node)
        
    def _calculate_temporal_weight(self, timestamp):
        """Calculate weight based on time elapsed"""
        age = (datetime.now(timezone.utc) - timestamp).total_seconds()
        return math.exp(-self.decay_factor * age / (24 * 60 * 60))  # Daily decay
        
    def _update_trust_scores(self, node: str):
        """Update aggregate trust scores with temporal decay"""
        if not self.interaction_history.get(node):
            return
            
        weighted_scores = {}
        total_weight = {}
        
        for interaction in self.interaction_history[node]:
            target = interaction['target']
            weight = self._calculate_temporal_weight(interaction['timestamp'])
            
            if target not in weighted_scores:
                weighted_scores[target] = 0
                total_weight[target] = 0
                
            weighted_scores[target] += interaction['score'] * weight
            total_weight[target] += weight
            
        # Calculate normalized trust scores
        self.trust_scores[node] = {
            target: weighted_scores[target] / total_weight[target]
            for target in weighted_scores
            if total_weight[target] > 0
        }
        
    def get_trust_score(self, from_node: str, to_node: str) -> float:
        """Get the current trust score between two nodes"""
        if from_node not in self.trust_scores:
            return 0.0
        return self.trust_scores[from_node].get(to_node, 0.0)
        
    def get_aggregate_reputation(self, node: str) -> float:
        """Calculate aggregate reputation across all observers"""
        if not self.trust_scores:
            return 0.0
            
        total_score = 0.0
        count = 0
        
        for observer in self.trust_scores:
            if node in self.trust_scores[observer]:
                total_score += self.trust_scores[observer][node]
                count += 1
                
        return total_score / count if count > 0 else 0.0
        
    def get_network_trust_ranks(self) -> dict:
        """Return sorted reputation rankings for all nodes"""
        nodes = set()
        for scores in self.trust_scores.values():
            nodes.update(scores.keys())
            
        return {
            node: self.get_aggregate_reputation(node)
            for node in nodes
        }