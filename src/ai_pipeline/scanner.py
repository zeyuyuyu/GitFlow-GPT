import os
import time
import random
from typing import List

class ScannerNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.targets = []
        self.results = []

    def scan_target(self, target: str):
        # Simulate scanning a target
        time.sleep(random.uniform(0.5, 2.0))
        result = f"Node {self.node_id} scanned {target} successfully"
        self.results.append(result)
        return result

class ScannerSwarm:
    def __init__(self, num_nodes: int):
        self.nodes: List[ScannerNode] = [ScannerNode(f"node-{i}") for i in range(num_nodes)]

    def add_target(self, target: str):
        for node in self.nodes:
            node.targets.append(target)

    def run_scan(self):
        for node in self.nodes:
            for target in node.targets:
                node.scan_target(target)

    def get_results(self) -> List[str]:
        results = []
        for node in self.nodes:
            results.extend(node.results)
        return results

if __name__ == "__main__":
    swarm = ScannerSwarm(5)
    swarm.add_target("example.com")
    swarm.add_target("google.com")
    swarm.add_target("github.com")
    swarm.run_scan()
    print("\n".join(swarm.get_results()))
