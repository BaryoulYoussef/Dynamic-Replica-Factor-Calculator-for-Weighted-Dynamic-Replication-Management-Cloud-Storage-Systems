# 💾 Dynamic Replica Management System

A Python implementation of an intelligent data replication strategy based on **temporal locality** and **access frequency analysis**. This system automatically optimizes replica factors for distributed storage systems by classifying files as Hot, Warm, or Cold based on their access patterns.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Algorithm](#algorithm)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Web Interface](#web-interface)
- [Output Format](#output-format)
- [Implementation Details](#implementation-details)
- [Research Paper](#research-paper)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project implements a **Weighted Dynamic Data Replication Algorithm** that analyzes file access logs to automatically determine optimal replication factors. The system continuously monitors access patterns and adjusts replica counts to:

- ✅ **Maximize availability** for frequently accessed files (Hot data)
- 💰 **Minimize storage costs** by reducing replicas for rarely accessed files (Cold data)
- ⚖️ **Balance performance and efficiency** for moderately accessed files (Warm data)
- 🔒 **Ensure data safety** through Reed-Solomon erasure coding for cold data

### Key Concepts

- **Temporal Locality**: Recent access patterns predict future access behavior
- **Dynamic Thresholds**: Automatically calculated based on system-wide access patterns
- **Iterative Optimization**: Replication factors evolve over time as access patterns change

---

## ✨ Features

### Core Functionality

- 🔄 **Automatic Time Interval Detection**: Analyzes logs in configurable time windows (default: 60 minutes)
- 📊 **Dynamic Classification**: Files are categorized as Hot, Warm, or Cold based on:
  - Access frequency (`ac_i`)
  - Number of accessing nodes (`dnc_i`)
  - Node coverage weight (`w_i`)
  - Popularity degree (`PD_i`)
- 📈 **Adaptive Replication**: RF adjusts automatically based on file popularity
- 🛡️ **Erasure Coding**: Reed-Solomon (10,4) encoding for cold data protection
- 💾 **Persistent State**: Replication factors carry over between intervals

### Web Interface

- 🌐 **Streamlit Web UI**: Beautiful, interactive dashboard
- 📁 **Drag & Drop Upload**: Easy CSV file upload
- 📊 **Real-time Metrics**: Live statistics and progress tracking
- 📥 **Batch Download**: Export all results as ZIP
- 📑 **Multi-tab Results**: Separate view for each time interval

---

## 🧮 Algorithm

The system implements the following algorithm from the research paper:

### Step-by-Step Process

```
1. Set time interval (t)
2. For each time interval:
   a. Read access logs for interval t
   b. For each file fi:
      - Calculate access count (ac_i)
      - Calculate distinct node count (dnc_i)
      - Calculate weight (w_i) based on node coverage
      - Calculate popularity degree: PD_i = (ac_i × dnc_i × w_i) / crf_i
   c. Calculate dynamic threshold: T = mean(PD) / DN_count
   d. Classify files:
      - Hot: PD_i ≥ T AND w_i ∈ {3, 4}
      - Warm: (PD_i ≥ T AND w_i ∈ {1, 2}) OR (PD_i < T AND w_i ∈ {3, 4})
      - Cold: PD_i < T AND w_i ∈ {1, 2}
   e. Calculate new replication factors:
      - Hot/Warm: nrf_i = (crf_i × dnc_i) / DN_count
      - Cold: nrf_i = 1 + Erasure Coding
   f. Update system state for next interval
```

### Weight Calculation

| Node Coverage | Weight (w_i) |
|--------------|--------------|
| ≥ 75% nodes  | 4            |
| ≥ 50% nodes  | 3            |
| ≥ 25% nodes  | 2            |
| < 25% nodes  | 1            |

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/replica-management-system.git
cd replica-management-system
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
```

---

## 📖 Usage

### Option 1: Web Interface (Recommended)

Run the Streamlit web application:

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Option 2: Command Line

Run directly with Python:

```bash
python replica_clean.py
```

**Note**: You'll need to modify the `__main__` block in `replica_clean.py` to specify your log file and node count.

### Option 3: Python Script

```python
from replica_clean import ReplicaAlgorithm

# Initialize the algorithm
algorithm = ReplicaAlgorithm(
    log_file='access_logs.csv',
    DN_count=10  # Total number of data nodes
)

# Run the analysis
algorithm.run()
```

---

## 📁 Project Structure

```
replica-management-system/
│
├── app.py                      # Streamlit web interface
├── replica_clean.py            # Core algorithm implementation
├── calculator.py               # Calculation utilities (weight, PD, threshold)
├── data_generator.py           # Sample data generator (optional)
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── access_logs.csv             # Input: Access log file
│
└── interval_X_results.csv      # Output: Results for each interval
```

### File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web interface for user interaction |
| `replica_clean.py` | Main algorithm implementation |
| `calculator.py` | Mathematical calculations (weight, PD, threshold) |
| `data_generator.py` | Generates sample access logs for testing |

---

## 🌐 Web Interface

### Features

1. **Upload Section** (Left Sidebar)
   - Drag & drop CSV file upload
   - Configure number of data nodes
   - View system information

2. **Data Preview**
   - View first 10 rows of uploaded data
   - Statistics: Total records, unique files, unique nodes

3. **Analysis**
   - One-click analysis execution
   - Real-time progress bar
   - Status updates

4. **Results Display**
   - Multi-tab interface (one per interval)
   - Metrics cards: Hot/Warm/Cold counts, Average RF
   - Interactive data tables
   - Download buttons for each interval
   - Bulk download as ZIP

---

## 📊 Output Format

### Input CSV Format

Your access log CSV must contain these columns:

```csv
filename,node_id,timestamp,current_replication_factor
file_A.txt,1,2024-01-01 00:15:30,3
file_A.txt,2,2024-01-01 00:18:45,3
file_B.pdf,3,2024-01-01 00:22:10,3
```

**Column Descriptions:**
- `filename`: Name of the accessed file
- `node_id`: ID of the node that accessed the file
- `timestamp`: Access timestamp (ISO 8601 format)
- `current_replication_factor`: Initial replication factor (typically 3)

### Output CSV Format

The system generates `interval_X_results.csv` for each time interval:

```csv
filename,ac_i,dnc_i,w_i,crf_i,PD_i,threshold,classification,nrf_i,erasure_coding,interval_start,interval_end
file_A.txt,75,9,4,3,90.0,22.3458,HOT,3,False,2024-01-01 00:00:00,2024-01-01 01:00:00
file_C.mp4,68,8,4,3,90.67,22.3458,HOT,3,False,2024-01-01 00:00:00,2024-01-01 01:00:00
file_B.pdf,12,2,1,3,8.0,22.3458,COLD,1,True,2024-01-01 00:00:00,2024-01-01 01:00:00
```

**Column Descriptions:**

| Column | Description |
|--------|-------------|
| `filename` | Name of the file |
| `ac_i` | Access count (number of times accessed) |
| `dnc_i` | Distinct node count (unique nodes that accessed) |
| `w_i` | Weight (1-4 based on node coverage) |
| `crf_i` | Current replication factor (from previous interval) |
| `PD_i` | Popularity degree (calculated metric) |
| `threshold` | Dynamic threshold for this interval |
| `classification` | HOT, WARM, or COLD |
| `nrf_i` | New replication factor (used in next interval) |
| `erasure_coding` | True if erasure coding is applied |
| `interval_start` | Start timestamp of interval |
| `interval_end` | End timestamp of interval |

---

## 🔬 Implementation Details

### Core Classes

#### `ReplicaAlgorithm` (replica_clean.py)

Main algorithm controller that orchestrates the entire process.

**Key Methods:**
- `run()`: Main execution loop
- `set_time_interval()`: Divides logs into time intervals
- `process_files()`: Calculates metrics for each file
- `classify_files()`: Categorizes files as Hot/Warm/Cold
- `calculate_new_rf_for_hot_warm()`: Computes new RF for Hot/Warm files
- `process_cold_data()`: Handles cold data with erasure coding
- `save_interval_results()`: Exports results to CSV

#### `Calculator` (calculator.py)

Mathematical computation utilities.

**Methods:**
- `calculate_weight()`: Computes w_i based on node coverage
- `calculate_popularity_degree()`: Computes PD_i using formula
- `calculate_threshold()`: Computes dynamic threshold T

### State Management

The system maintains state across intervals using `self.current_rf`:

```python
# Interval 1
file_A.txt: crf=3 → nrf=2

# Interval 2 (uses previous nrf as crf)
file_A.txt: crf=2 → nrf=3

# Interval 3
file_A.txt: crf=3 → nrf=1
```

This ensures the **iterative nature** described in the paper, where replication factors evolve dynamically.

---

## 📚 Research Paper

This implementation is based on the following research paper:

**Title:** [A Dynamic Replica Factor Calculator for Weighted Dynamic Replication Management in Cloud Storage Systems](https://www.sciencedirect.com/science/article/pii/S187705091830886X)

**Authors:** Suji Gopinath, Elizabeth Sherly

**Publication:** Procedia Computer Science 132 (2018) 1771–1780  
**Conference:** International Conference on Computational Intelligence and Data Science (ICCIDS 2018)

**Abstract:**
> Data replication is a widely-used technique in cloud storage systems to ensure availability of data. In static replication policies, the number of replicas to be created is decided statically at the time of cloud system setup. The replication of data needs to be dynamic considering changing pattern in user request and storage capacity. This will ensure that storage space is not wasted by keeping unnecessary replicas for least used data. In this work, a strategy is proposed to dynamically set the replica factor for each data item considering the popularity of data, its current replication factor and the number of active nodes present in the cloud storage.

**Key Contributions:**
- Weighted dynamic data replication algorithm
- 4-point weightage scheme for node coverage
- Dynamic threshold calculation based on popularity degree
- Reed-Solomon (10,4) erasure coding integration
- Temporal locality-based classification (Hot/Warm/Cold)

### Citation

```bibtex
@article{gopinath2018dynamic,
  title={A Dynamic Replica Factor Calculator for Weighted Dynamic Replication Management in Cloud Storage Systems},
  author={Gopinath, Suji and Sherly, Elizabeth},
  journal={Procedia Computer Science},
  volume={132},
  pages={1771--1780},
  year={2018},
  publisher={Elsevier},
  doi={10.1016/j.procs.2018.05.137},
  url={https://www.sciencedirect.com/science/article/pii/S187705091830886X}
}
```

📄 **[Read the full paper on ScienceDirect →](https://www.sciencedirect.com/science/article/pii/S187705091830886X)**

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Contribution

- 📊 Additional visualization options
- 🔧 Configuration file support
- 📈 Performance optimizations
- 🧪 Unit tests
- 📖 Documentation improvements
- 🌍 Internationalization

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Research Authors:** Suji Gopinath and Elizabeth Sherly for their groundbreaking work on dynamic replication management
- **Original Paper:** [A Dynamic Replica Factor Calculator for Weighted Dynamic Replication Management in Cloud Storage Systems](https://www.sciencedirect.com/science/article/pii/S187705091830886X)
- **Streamlit Team:** For the amazing web framework that powers our interface
- **Pandas & NumPy Communities:** For essential data processing libraries

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact:

- **Email:** baryouly@gmail.com / salimkhaskhoussi@gmail.com / 	Dabbech.rihab2019@gmail.com
- **LinkedIn:** [Youssef Baryoul](https://www.linkedin.com/in/youssef-baryoul/)  [Salim Khaskhoussi](https://www.linkedin.com/in/salim-khaskhoussi/) [Rihab Dabbech](https://www.linkedin.com/in/dabbech-rihab/?originalSubdomain=tn)

---

## 🎓 Learn More

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [HDFS Architecture](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html)
- [Reed-Solomon Error Correction](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)

---

<div align="center">

**Made with ❤️ for distributed systems optimization**

⭐ Star this repository if you found it helpful!

</div>