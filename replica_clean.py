import pandas as pd
import numpy as np
from calculator import Calculator

cal = Calculator()


class ReplicaAlgorithm:
    def __init__(self, log_file, DN_count=10):
        self.log_file = log_file
        self.DN_count = DN_count  # Total number of active data nodes
        self.df = None
        
        
        self.current_rf = {}

    def run(self):
        
        
        
        print("Algorithm Started\n")
        
        # 1. Set time interval
        time_interval = self.set_time_interval()
        
        # 2. for each time interval
        for interval_idx, (start_time, end_time) in enumerate(time_interval, 1):
            print(f"\n{'='*60}")
            print(f"Processing Time Interval {interval_idx}")
            print(f"From: {start_time}")
            print(f"To: {end_time}")
            print(f"{'='*60}")
            
            # i. read logfile
            interval_logs = self.read_logfile(start_time, end_time)
            
            # ii. for each file f_i
            file_metrics = self.process_files(interval_logs)
            
            # iii. Calculate the threshold
            T = cal.calculate_threshold(file_metrics, self.DN_count)
            print(f"\nThreshold T = {T:.4f}")
            
            # iv. for each file f_i - Compare threshold T and w_i
            HD, WD, CD = self.classify_files(file_metrics, T)
            
            # v. for each f_i in HD and WD
            self.calculate_new_rf_for_hot_warm(HD, WD)
            
            # vi. for each f_i in CD
            self.process_cold_data(CD)
            
            # NEW: Save results for this interval to CSV
            self.save_interval_results(interval_idx, start_time, end_time, 
                                      HD, WD, CD, T)
            
       
        print("\n\nAlgorithm Completed")
        print(f"✓ Generated {len(time_interval)} interval result files")


    def set_time_interval(self):
        
        # Read the log file to determine time intervals
        self.df = pd.read_csv(self.log_file)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])

        min_time = self.df['timestamp'].min()
        max_time = self.df['timestamp'].max()
        
        
        intervals = []
        current = min_time
        interval_duration = pd.Timedelta(minutes=60)
        
        while current < max_time:
            end = current + interval_duration
            intervals.append((current, end))
            current = end
            
        print(f"Total intervals: {len(intervals)}")
        return intervals
    

    def read_logfile(self, start_time, end_time):
        mask = (self.df['timestamp'] >= start_time) & (self.df['timestamp'] < end_time)
        return self.df[mask]
    
    def process_files(self, interval_logs):
        """ii. for each file f_i"""
        
        files = []
        
        for filename in interval_logs['filename'].unique():
            file_logs = interval_logs[interval_logs['filename'] == filename]
            
            # a. Find ac_i, dnc_i, rf_i
            ac_i = len(file_logs)  # access count
            dnc_i = file_logs['node_id'].nunique()  # distinct node count
            
            # IMPORTANT: Use the updated replication factor from previous interval
            # If this is the first time we see this file, use the value from CSV
            if filename in self.current_rf:
                crf_i = self.current_rf[filename]
            else:
                # First interval: use initial replication factor from log
                crf_i = file_logs['current_replication_factor'].iloc[0]
                self.current_rf[filename] = crf_i
            
            # b. Calculate the weight w_i for each file
            w_i = cal.calculate_weight(dnc_i,self.DN_count)
            
            # c. Calculate popularity index (PD_i) of each file
            PD_i = cal.calculate_popularity_degree(ac_i, dnc_i, w_i, crf_i)
            
            files.append({
                'filename': filename,
                'ac_i': ac_i,
                'dnc_i': dnc_i,
                'crf_i': crf_i,
                'w_i': w_i,
                'PD_i': PD_i
            })
            
        return pd.DataFrame(files)

    

    def classify_files(self, file_metrics, T):
        """
       for each file f_i
        Compare threshold T and w_i
        """
        HD = []  # Hot Data
        WD = []  # Warm Data
        CD = []  # Cold Data
        
        for _, row in file_metrics.iterrows():
            PD_i = row['PD_i']
            w_i = row['w_i']
            
            # Convert row to dict for easier handling
            file_dict = row.to_dict()
            file_dict['classification'] = None
            
            # if (PD_i >= T && w_i = 3 or 4)
            if PD_i >= T and w_i in [3, 4]:
                file_dict['classification'] = 'HOT'
                HD.append(file_dict)
            # else if (PD_i >= T && w_i = 1 or 2)
            elif PD_i >= T and w_i in [1, 2]:
                file_dict['classification'] = 'WARM'
                WD.append(file_dict)
            # else if (PD_i < T && w_i = 3 or 4)
            elif PD_i < T and w_i in [3, 4]:
                file_dict['classification'] = 'WARM'
                WD.append(file_dict)
            # else if (PD_i < T && w_i = 1 or 2)
            else:  # PD_i < T and w_i in [1, 2]
                file_dict['classification'] = 'COLD'
                CD.append(file_dict)
        
        print(f"\nClassification Results:")
        print(f"  Hot Data (HD): {len(HD)} files")
        print(f"  Warm Data (WD): {len(WD)} files")
        print(f"  Cold Data (CD): {len(CD)} files")
        
        return HD, WD, CD
    
    def calculate_new_rf_for_hot_warm(self, HD, WD):
        """
         for each f_i in HD and WD
        nrf_i = (crf_i * dnc_i) / DN_count
        """
        print(f"\nCalculating new replication factors for Hot and Warm data:")
        
        for file_data in HD + WD:
            filename = file_data['filename']
            crf_i = file_data['crf_i']
            dnc_i = file_data['dnc_i']
            classification = file_data['classification']
            
            nrf_i = (crf_i * dnc_i) / self.DN_count
            nrf_i = max(1, int(round(nrf_i)))  # Minimum is 1
            
            # UPDATE: Store the new replication factor for next interval
            self.current_rf[filename] = nrf_i
            
            # Store the new RF in the file_data dict for CSV export
            file_data['nrf_i'] = nrf_i
            
            print(f"  {filename} [{classification}]: RF {crf_i} → {nrf_i}")
    
    def process_cold_data(self, CD):
        """
         for each f_i in CD
        Set rf_i to 1
        Encode f_i using Reed-Solomon erasure code
        """
        print(f"\nProcessing Cold Data:")
        
        for file_data in CD:
            filename = file_data['filename']
            crf_i = file_data['crf_i']
            
            
            nrf_i = 1
            
            # UPDATE: Store the new replication factor for next interval
            self.current_rf[filename] = nrf_i
            
            # Store the new RF in the file_data dict for CSV export
            file_data['nrf_i'] = nrf_i
            
            # Encode f_i using Reed-Solomon erasure code
            print(f"  {filename} [COLD]: RF {crf_i} → {nrf_i} + Erasure Coding (10,4)")
    
    
        
    def save_interval_results(self, interval_idx, start_time, end_time, 
                             HD, WD, CD, threshold):
        """
        Save detailed results for this time interval to a CSV file
        
        """
        
        # Combine all files from HD, WD, CD
        all_files = HD + WD + CD
        
        # Add erasure coding flag
        for file_data in all_files:
            # Erasure coding is applied if nrf_i = 1
            file_data['erasure_coding'] = (file_data['nrf_i'] == 1)
            file_data['threshold'] = threshold
            file_data['interval_start'] = start_time
            file_data['interval_end'] = end_time
        
        # Create DataFrame
        df = pd.DataFrame(all_files)
        
        # Select and order columns
        columns = [
            'filename',
            'ac_i',
            'dnc_i', 
            'w_i',
            'crf_i',
            'PD_i',
            'threshold',
            'classification',
            'nrf_i',
            'erasure_coding',
            'interval_start',
            'interval_end'
        ]
        
        df = df[columns]
        
        # Sort by classification (Hot -> Warm -> Cold) and then by filename
        classification_order = {'HOT': 0, 'WARM': 1, 'COLD': 2}
        df['sort_key'] = df['classification'].map(classification_order)
        df = df.sort_values(['sort_key', 'filename']).drop('sort_key', axis=1)
        
        # Save to CSV
        output_file = f'interval_{interval_idx}_results.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n Saved results to: {output_file}")
        print(f"  Files in this interval: {len(df)}")
        print(f"  Columns: {', '.join(columns)}")


if __name__ == "__main__":
    algorithm = ReplicaAlgorithm(
        log_file='access_logs.csv',
        DN_count=10
    )
    
    algorithm.run()