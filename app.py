"""
app.py - Streamlit Web Interface for Replica Management System

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import os
from replica_clean import ReplicaAlgorithm
import io
import zipfile

# Page configuration
st.set_page_config(
    page_title="Replica Management System",
    page_icon="💾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def validate_csv_format(df):
    """Validate that the uploaded CSV has required columns"""
    required_columns = ['filename', 'node_id', 'timestamp', 'current_replication_factor']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, missing_columns
    return True, []

def create_download_zip():
    """Create a ZIP file containing all interval result files"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Find all interval result files
        for file in os.listdir('.'):
            if file.startswith('interval_') and file.endswith('_results.csv'):
                zip_file.write(file)
    
    zip_buffer.seek(0)
    return zip_buffer

def main():
    # Header
    st.markdown('<p class="main-header">💾 Dynamic Replica Management System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Based on Temporal Locality & Access Frequency Analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    st.sidebar.markdown("---")
    
    # File uploader
    st.sidebar.subheader("📁 Upload Access Log")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your access log CSV file with required columns"
    )
    
    # Number of nodes input
    st.sidebar.subheader("🖥️ System Configuration")
    dn_count = st.sidebar.number_input(
        "Total Number of Data Nodes",
        min_value=1,
        max_value=1000,
        value=10,
        step=1,
        help="Total number of active data nodes in your system"
    )
    
    st.sidebar.markdown("---")
    
    # Information section
    with st.sidebar.expander("ℹ️ About This System"):
        st.markdown("""
        This system analyzes file access patterns and calculates optimal replication factors based on:
        
        - **Temporal Locality**: Recent access patterns
        - **Access Frequency**: How often files are accessed
        - **Node Coverage**: How many nodes access each file
        
        Files are classified as:
        - 🔥 **Hot**: High popularity, high node coverage
        - 🌡️ **Warm**: Moderate popularity
        - ❄️ **Cold**: Low popularity (erasure coded)
        """)
    
    with st.sidebar.expander("📋 Required CSV Format"):
        st.markdown("""
        Your CSV must have these columns:
        
        - `filename`: Name of the file
        - `node_id`: ID of the accessing node
        - `timestamp`: Access timestamp (ISO format)
        - `current_replication_factor`: Initial RF value
        
        Example:
        ```
        filename,node_id,timestamp,current_replication_factor
        file_A.txt,1,2024-01-01 00:15:30,3
        file_B.pdf,2,2024-01-01 00:20:45,3
        ```
        """)
    
    # Main content area
    if uploaded_file is None:
        # Welcome screen
        st.info("👈 Please upload your access log CSV file from the sidebar to begin analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 How It Works")
            st.markdown("""
            1. Upload your access log CSV
            2. Configure number of data nodes
            3. Click 'Run Analysis'
            4. Download interval results
            """)
        
        with col2:
            st.markdown("### 📊 What You Get")
            st.markdown("""
            - File classifications (Hot/Warm/Cold)
            - Optimized replication factors
            - Access pattern metrics
            - Time interval analysis
            """)
        
        with col3:
            st.markdown("### ⚡ Features")
            st.markdown("""
            - Automatic time interval detection
            - Dynamic threshold calculation
            - Erasure coding recommendations
            - Comprehensive CSV reports
            """)
        
    else:
        # File uploaded - show preview and run analysis
        try:
            # Read and validate CSV
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully: **{uploaded_file.name}** ({len(df)} records)")
            
            # Validate format
            is_valid, missing_cols = validate_csv_format(df)
            
            if not is_valid:
                st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                st.info("Please check the 'Required CSV Format' section in the sidebar")
                return
            
            # Show data preview
            with st.expander("👀 Preview Data (First 10 rows)", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)
            
            # Show data statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📄 Total Records", len(df))
            with col2:
                st.metric("🗂️ Unique Files", df['filename'].nunique())
            with col3:
                st.metric("🖥️ Unique Nodes", df['node_id'].nunique())
            with col4:
                st.metric("⚙️ System Nodes", dn_count)
            
            st.markdown("---")
            
            # Run analysis button
            if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
                # Save uploaded file temporarily
                temp_file = "temp_access_logs.csv"
                df.to_csv(temp_file, index=False)
                
                # Progress bar and status
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("⏳ Initializing algorithm...")
                    progress_bar.progress(10)
                    
                    # Run algorithm
                    algorithm = ReplicaAlgorithm(
                        log_file=temp_file,
                        DN_count=dn_count
                    )
                    
                    status_text.text("⏳ Analyzing access patterns...")
                    progress_bar.progress(30)
                    
                    # Capture output
                    with st.spinner("Processing time intervals..."):
                        algorithm.run()
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    
                    # Clean up temp file
                    os.remove(temp_file)
                    
                    # Success message
                    st.balloons()
                    st.markdown('<div class="success-box"><h3>🎉 Analysis Completed Successfully!</h3></div>', unsafe_allow_html=True)
                    
                    # Find all generated interval files
                    interval_files = sorted([f for f in os.listdir('.') if f.startswith('interval_') and f.endswith('_results.csv')])
                    
                    if interval_files:
                        st.success(f"📊 Generated {len(interval_files)} interval result files")
                        
                        # Create tabs for each interval
                        tabs = st.tabs([f"Interval {i+1}" for i in range(len(interval_files))])
                        
                        for i, (tab, file) in enumerate(zip(tabs, interval_files)):
                            with tab:
                                interval_df = pd.read_csv(file)
                                
                                # Show summary metrics
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    hot_count = (interval_df['classification'] == 'HOT').sum()
                                    st.metric("🔥 Hot Files", hot_count)
                                
                                with col2:
                                    warm_count = (interval_df['classification'] == 'WARM').sum()
                                    st.metric("🌡️ Warm Files", warm_count)
                                
                                with col3:
                                    cold_count = (interval_df['classification'] == 'COLD').sum()
                                    st.metric("❄️ Cold Files", cold_count)
                                
                                with col4:
                                    avg_rf = interval_df['nrf_i'].mean()
                                    st.metric("📊 Avg RF", f"{avg_rf:.2f}")
                                
                                # Show dataframe
                                st.dataframe(interval_df, use_container_width=True)
                                
                                # Download button for this interval
                                csv = interval_df.to_csv(index=False)
                                st.download_button(
                                    label=f"📥 Download Interval {i+1} Results",
                                    data=csv,
                                    file_name=file,
                                    mime='text/csv',
                                    key=f"download_{i}"
                                )
                        
                        st.markdown("---")
                        
                        # Download all as ZIP
                        st.subheader("📦 Download All Results")
                        zip_buffer = create_download_zip()
                        st.download_button(
                            label="⬇️ Download All Intervals (ZIP)",
                            data=zip_buffer,
                            file_name="replica_analysis_results.zip",
                            mime="application/zip",
                            type="primary",
                            use_container_width=True
                        )
                    
                except Exception as e:
                    st.error(f"❌ An error occurred during analysis: {str(e)}")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("Please ensure your file is a valid CSV with the correct format")

if __name__ == "__main__":
    main()