# data_generator.py
"""Generate sample access logs with proper time intervals"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class AccessLogGenerator:
    def __init__(self, num_intervals=5, total_nodes=Config.TOTAL_NODES):
        self.num_intervals = num_intervals
        self.total_nodes = total_nodes
        self.start_time = datetime(2024, 1, 1, 0, 0, 0)
        
    def generate_logs(self, output_file='access_logs.csv'):
        """Generate access logs with multiple time intervals"""
        
        files = [
            'file_A.txt', 'file_B.pdf', 'file_C.mp4', 'file_D.txt',
            'file_E.doc', 'file_F.jpg', 'file_G.csv', 'file_H.zip'
        ]
        
        all_logs = []
        
        for interval_idx in range(self.num_intervals):
            interval_start = self.start_time + timedelta(
                minutes=interval_idx * Config.TIME_INTERVAL_MINUTES
            )
            
            for file in files:
                # Determine file type (hot, warm, cold) with some variation
                access_pattern = self._get_access_pattern(file, interval_idx)
                
                # Generate accesses for this file in this interval
                logs = self._generate_file_accesses(
                    file, interval_start, access_pattern
                )
                all_logs.extend(logs)
        
        # Create DataFrame and save
        df = pd.DataFrame(all_logs)
        df = df.sort_values('timestamp').reset_index(drop=True)
        df.to_csv(output_file, index=False)
        
        print(f"✓ Generated {len(df)} access logs across {self.num_intervals} time intervals")
        print(f"  Time interval duration: {Config.TIME_INTERVAL_MINUTES} minutes")
        print(f"  Output file: {output_file}")
        
        return output_file
    
    def _get_access_pattern(self, filename, interval_idx):
        """
        Define access patterns for files that may change over time
        Returns: (num_accesses, unique_nodes, pattern_type)
        """
        # Simulate temporal locality - some files become hot/cold over time
        
        # Files that are consistently hot
        if filename in ['file_A.txt', 'file_C.mp4']:
            return {
                'num_accesses': np.random.randint(40, 80),
                'unique_nodes': np.random.randint(8, self.total_nodes + 1),
                'type': 'hot'
            }
        
        # File that becomes hot over time (temporal shift)
        elif filename == 'file_B.pdf':
            if interval_idx < 2:
                return {
                    'num_accesses': np.random.randint(5, 15),
                    'unique_nodes': np.random.randint(1, 3),
                    'type': 'cold'
                }
            else:
                return {
                    'num_accesses': np.random.randint(50, 90),
                    'unique_nodes': np.random.randint(7, self.total_nodes + 1),
                    'type': 'hot'
                }
        
        # File that cools down over time
        elif filename == 'file_D.txt':
            if interval_idx < 2:
                return {
                    'num_accesses': np.random.randint(30, 60),
                    'unique_nodes': np.random.randint(5, 8),
                    'type': 'warm'
                }
            else:
                return {
                    'num_accesses': np.random.randint(2, 8),
                    'unique_nodes': np.random.randint(1, 3),
                    'type': 'cold'
                }
        
        # Warm files
        elif filename in ['file_E.doc', 'file_F.jpg']:
            return {
                'num_accesses': np.random.randint(15, 35),
                'unique_nodes': np.random.randint(3, 6),
                'type': 'warm'
            }
        
        # Cold files
        else:
            return {
                'num_accesses': np.random.randint(1, 10),
                'unique_nodes': np.random.randint(1, 3),
                'type': 'cold'
            }
    
    def _generate_file_accesses(self, filename, interval_start, pattern):
        """Generate individual access records for a file within a time interval"""
        logs = []
        num_accesses = pattern['num_accesses']
        unique_nodes = pattern['unique_nodes']
        
        # Generate random nodes that will access this file
        accessing_nodes = np.random.choice(
            range(1, self.total_nodes + 1),
            size=unique_nodes,
            replace=False
        )
        
        # Generate access times within the interval
        for _ in range(num_accesses):
            # Pick a random node from those that access this file
            node_id = np.random.choice(accessing_nodes)
            
            # Generate timestamp within the interval
            random_offset = np.random.randint(0, Config.TIME_INTERVAL_MINUTES * 60)
            timestamp = interval_start + timedelta(seconds=random_offset)
            
            logs.append({
                'filename': filename,
                'node_id': node_id,
                'timestamp': timestamp.isoformat(),
                'current_replication_factor': Config.DEFAULT_REPLICATION_FACTOR
            })
        
        return logs


if __name__ == "__main__":
    generator = AccessLogGenerator(num_intervals=5)
    generator.generate_logs('access_logs.csv')