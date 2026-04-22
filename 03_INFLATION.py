# app.py - Inflation Analysis Streamlit Application

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import io
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Inflation Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .data-table {
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
    }
    .country-comparison {
        background-color: #EFF6FF;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #93C5FD;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">📊 Inflation Analysis Dashboard</h1>', unsafe_allow_html=True)
st.markdown("""
This interactive dashboard allows you to analyze inflation data for multiple countries. 
Upload your data or use the sample data to explore trends, compare countries, and generate insights.
""")

# Helper function to save matplotlib figure to bytes
def fig_to_bytes(fig):
    """Convert matplotlib figure to bytes for download"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    return buf

# Helper function to find strongest correlations
def find_strongest_correlations(corr_df):
    """Find strongest positive and negative correlations excluding self-correlations"""
    # Create a copy of the correlation matrix
    corr_matrix = corr_df.values.copy()
    
    # Create mask for diagonal elements
    n = corr_matrix.shape[0]
    mask = np.eye(n, dtype=bool)
    
    # Get non-diagonal correlations
    non_diag_corr = corr_matrix[~mask]
    
    if len(non_diag_corr) == 0:
        return None, None, None, None, 0, 0
    
    # Find max and min correlations
    max_corr = non_diag_corr.max()
    min_corr = non_diag_corr.min()
    
    # Find indices
    max_idx = np.where(corr_matrix == max_corr)
    min_idx = np.where(corr_matrix == min_corr)
    
    # Get country names
    if len(max_idx[0]) > 0:
        max_i, max_j = max_idx[0][0], max_idx[1][0]
        max_country1 = corr_df.index[max_i]
        max_country2 = corr_df.columns[max_j]
    else:
        max_country1 = max_country2 = "N/A"
        
    if len(min_idx[0]) > 0:
        min_i, min_j = min_idx[0][0], min_idx[1][0]
        min_country1 = corr_df.index[min_i]
        min_country2 = corr_df.columns[min_j]
    else:
        min_country1 = min_country2 = "N/A"
    
    return max_country1, max_country2, min_country1, min_country2, max_corr, min_corr

# Sidebar configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Data source selection
    data_source = st.radio(
        "Select Data Source:",
        ["📁 Upload CSV File", "📊 Use Sample Data"]
    )
    
    # File uploader
    uploaded_file = None
    if data_source == "📁 Upload CSV File":
        uploaded_file = st.file_uploader(
            "Upload your inflation data CSV file",
            type=["csv"],
            help="CSV file should contain columns: 'Country Name', 'Country Code', and year columns like '[YR2000]', '[YR2001]', etc."
        )
    
    # Analysis parameters
    st.markdown("---")
    st.markdown("### 🔍 Analysis Parameters")
    
    # Country selection mode
    selection_mode = st.radio(
        "Country Selection Mode:",
        ["📊 Auto-select top countries", "🎯 Manually select countries"],
        help="Auto-select: choose based on data completeness. Manual: select specific countries."
    )
    
    if selection_mode == "🎯 Manually select countries":
        # Number of countries to select
        num_manual_countries = st.slider(
            "Number of countries to select:",
            min_value=1,
            max_value=9,
            value=3,
            help="Select 1-9 countries for detailed comparison"
        )
    else:
        # Number of countries to analyze (auto mode)
        num_auto_countries = st.slider(
            "Number of countries to analyze:",
            min_value=3,
            max_value=15,
            value=9,
            help="Select how many countries to include in the analysis"
        )
    
    # Year range selection
    year_range = st.slider(
        "Year range to analyze:",
        min_value=1960,
        max_value=2023,
        value=(2000, 2023),
        help="Select the year range for analysis"
    )
    
    # Chart type selection
    chart_types = st.multiselect(
        "Select charts to display:",
        ["Trend Line Chart", "Heatmap", "Distribution Histograms", 
         "Boxplot Comparison", "Volatility Analysis", "Change Rate Analysis", 
         "Interactive Chart", "Correlation Analysis", "Country Comparison Matrix"],
        default=["Trend Line Chart", "Interactive Chart", "Country Comparison Matrix"]
    )
    
    # Color palette
    color_palette = st.selectbox(
        "Color palette:",
        ["Set1", "Set2", "Set3", "tab10", "tab20", "viridis", "plasma", "husl"]
    )

# Main content area
if uploaded_file is not None or data_source == "📊 Use Sample Data":
    
    # Load data
    @st.cache_data
    def load_data(file=None, use_sample=False):
        if use_sample:
            # Create sample data
            np.random.seed(42)
            years = list(range(1960, 2024))
            countries = ['USA', 'CHN', 'JPN', 'DEU', 'GBR', 'FRA', 'ITA', 'IND', 'BRA', 
                        'CAN', 'AUS', 'RUS', 'KOR', 'MEX', 'IDN']
            
            data = []
            for country in countries:
                for year in years:
                    # Generate realistic inflation rates with trends
                    base_rate = np.random.uniform(1, 4)
                    # Add some trends over time
                    trend = (year - 1960) / 50 * np.random.uniform(-0.5, 0.5)
                    fluctuation = np.random.normal(0, 1.2)
                    inflation_rate = max(0.1, base_rate + trend + fluctuation)
                    data.append({
                        'Country Code': country,
                        'Country Name': f'Country {country}',
                        'Year': year,
                        'Inflation_Rate': inflation_rate
                    })
            
            df_long = pd.DataFrame(data)
            return df_long
            
        elif file is not None:
            # Read uploaded CSV file
            df = pd.read_csv(file)
            
            # Identify year columns
            year_columns = [col for col in df.columns if '[YR' in col or 'YR' in col or str(col).isdigit()]
            
            if len(year_columns) > 0:
                # Convert from wide to long format
                df_long = pd.melt(
                    df,
                    id_vars=['Country Name', 'Country Code'],
                    value_vars=year_columns,
                    var_name='Year',
                    value_name='Inflation_Rate'
                )
                
                # Extract year numbers
                df_long['Year'] = df_long['Year'].str.extract(r'(\d{4})').astype(int)
                df_long['Inflation_Rate'] = pd.to_numeric(df_long['Inflation_Rate'], errors='coerce')
                
                return df_long
            else:
                # Assume data is already in long format
                return df
        else:
            return pd.DataFrame()
    
    # Load the data
    if data_source == "📊 Use Sample Data":
        df_long = load_data(use_sample=True)
        st.success("✅ Sample data loaded successfully!")
    else:
        df_long = load_data(file=uploaded_file)
        st.success("✅ Uploaded data loaded successfully!")
    
    # Data preprocessing
    df_long_filtered = df_long[
        (df_long['Year'] >= year_range[0]) & 
        (df_long['Year'] <= year_range[1])
    ].copy()
    
    # Get all available countries
    all_countries = df_long_filtered['Country Code'].unique()
    country_names = df_long_filtered[['Country Code', 'Country Name']].drop_duplicates()
    country_name_dict = dict(zip(country_names['Country Code'], country_names['Country Name']))
    
    # Country selection based on mode
    if selection_mode == "🎯 Manually select countries":
        # Manual country selection
        st.markdown('<div class="country-comparison">', unsafe_allow_html=True)
        st.markdown("### 🎯 Manual Country Selection")
        
        # Create checkboxes for country selection
        available_countries_list = list(all_countries)
        selected_countries = []
        
        # Display countries in a grid
        cols = st.columns(3)
        for idx, country_code in enumerate(available_countries_list):
            col_idx = idx % 3
            with cols[col_idx]:
                country_display = f"{country_code} - {country_name_dict.get(country_code, 'Unknown')}"
                if st.checkbox(country_display, key=f"country_{country_code}"):
                    selected_countries.append(country_code)
        
        # Limit selection to num_manual_countries
        if len(selected_countries) > num_manual_countries:
            st.warning(f"⚠️ Please select only {num_manual_countries} countries. You have selected {len(selected_countries)}.")
            selected_countries = selected_countries[:num_manual_countries]
        
        # If no countries selected, use first few
        if len(selected_countries) == 0:
            selected_countries = list(all_countries)[:num_manual_countries]
            st.info(f"ℹ️ No countries selected. Using first {num_manual_countries} countries.")
        
        st.markdown(f"**Selected Countries ({len(selected_countries)}):** {', '.join(selected_countries)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        # Auto-select countries based on data completeness
        country_counts = df_long_filtered.groupby('Country Code')['Inflation_Rate'].count()
        selected_countries = country_counts.nlargest(num_auto_countries).index.tolist()
        st.info(f"ℹ️ Auto-selected {len(selected_countries)} countries based on data completeness.")
    
    # Filter data for selected countries
    df_selected = df_long_filtered[df_long_filtered['Country Code'].isin(selected_countries)].copy()
    
    # Display data overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Countries", len(df_selected['Country Code'].unique()))
    
    with col2:
        st.metric("Year Range", f"{df_selected['Year'].min()} - {df_selected['Year'].max()}")
    
    with col3:
        st.metric("Total Data Points", len(df_selected))
    
    with col4:
        avg_inflation = df_selected['Inflation_Rate'].mean()
        st.metric("Average Inflation Rate", f"{avg_inflation:.2f}%")
    
    # Data preview
    with st.expander("📋 View Data Preview", expanded=False):
        st.dataframe(
            df_selected.head(100),
            use_container_width=True,
            height=300
        )
        
        # Download button for filtered data
        csv = df_selected.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="filtered_inflation_data.csv",
            mime="text/csv"
        )
    
    # Charts section
    st.markdown('<h2 class="sub-header">📈 Visualization Charts</h2>', unsafe_allow_html=True)
    
    # Set color palette
    colors = plt.cm.get_cmap(color_palette)(np.linspace(0, 1, len(selected_countries)))
    
    # 1. Trend Line Chart
    if "Trend Line Chart" in chart_types:
        st.markdown("### 📈 Inflation Rate Trends")
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for i, country in enumerate(selected_countries):
            country_data = df_selected[df_selected['Country Code'] == country]
            ax.plot(country_data['Year'], country_data['Inflation_Rate'],
                   label=f"{country} - {country_name_dict[country]}",
                   linewidth=2.5, marker='o', markersize=4, color=colors[i])
        
        ax.axhline(y=2, color='red', linestyle='--', alpha=0.7, linewidth=2, label='2% Inflation Target')
        ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5, linewidth=1)
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Inflation Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Inflation Rate Trend Comparison', fontsize=16, fontweight='bold', pad=20)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        ax.set_xlim(df_selected['Year'].min() - 1, df_selected['Year'].max() + 1)
        y_min = df_selected['Inflation_Rate'].min()
        y_max = df_selected['Inflation_Rate'].max()
        ax.set_ylim(y_min - 1, y_max + 1)
        
        st.pyplot(fig)
        
        # Add download button for the chart
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Chart as PNG",
            data=buf,
            file_name="inflation_trend_chart.png",
            mime="image/png"
        )
    
    # 2. Heatmap
    if "Heatmap" in chart_types:
        st.markdown("### 🔥 Inflation Rate Heatmap")
        
        # Create pivot table
        pivot_data = df_selected.pivot_table(
            index='Country Code',
            columns='Year',
            values='Inflation_Rate',
            aggfunc='mean'
        )
        
        pivot_data = pivot_data.reindex(selected_countries)
        
        fig, ax = plt.subplots(figsize=(16, 6))
        sns.heatmap(pivot_data, cmap='RdYlBu_r', center=0, 
                   annot=True, fmt='.1f', linewidths=0.5,
                   cbar_kws={'label': 'Inflation Rate (%)', 'shrink': 0.8},
                   ax=ax)
        
        ax.set_title('Inflation Rate Heatmap by Country and Year', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('Country Code', fontsize=12, fontweight='bold')
        
        st.pyplot(fig)
        
        # Download button for heatmap
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Heatmap as PNG",
            data=buf,
            file_name="inflation_heatmap.png",
            mime="image/png"
        )
    
    # 3. Distribution Histograms
    if "Distribution Histograms" in chart_types:
        st.markdown("### 📊 Inflation Rate Distributions")
        
        num_cols = 3
        num_rows = (len(selected_countries) + num_cols - 1) // num_cols
        
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(16, 4*num_rows))
        axes = axes.flatten()
        
        for i, country in enumerate(selected_countries):
            country_data = df_selected[df_selected['Country Code'] == country]
            
            axes[i].hist(country_data['Inflation_Rate'].dropna(), bins=15,
                        edgecolor='black', alpha=0.7, color=colors[i])
            
            mean_val = country_data['Inflation_Rate'].mean()
            median_val = country_data['Inflation_Rate'].median()
            
            axes[i].axvline(x=mean_val, color='red', linestyle='--',
                          label=f'Mean: {mean_val:.2f}%', linewidth=2)
            axes[i].axvline(x=median_val, color='green', linestyle=':',
                          label=f'Median: {median_val:.2f}%', linewidth=2)
            
            axes[i].set_xlabel('Inflation Rate (%)', fontsize=10)
            axes[i].set_ylabel('Frequency', fontsize=10)
            axes[i].set_title(f'{country} - {country_name_dict[country]}', fontsize=11, fontweight='bold')
            axes[i].legend(fontsize=8)
            axes[i].grid(True, alpha=0.3)
        
        # Hide empty subplots
        for i in range(len(selected_countries), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Inflation Rate Distribution by Country', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Download button for histograms
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Distribution Charts as PNG",
            data=buf,
            file_name="inflation_distributions.png",
            mime="image/png"
        )
    
    # 4. Boxplot Comparison
    if "Boxplot Comparison" in chart_types:
        st.markdown("### 📦 Boxplot Comparison")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.boxplot(data=df_selected, x='Country Code', y='Inflation_Rate',
                   palette=color_palette, width=0.7, ax=ax)
        
        # Add mean points
        means = df_selected.groupby('Country Code')['Inflation_Rate'].mean()
        for i, country in enumerate(selected_countries):
            ax.scatter(i, means[country], color='red', s=80, zorder=5,
                     label='Mean' if i == 0 else "")
        
        ax.axhline(y=2, color='red', linestyle='--', alpha=0.7, label='2% Inflation Target')
        ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('Country Code', fontsize=12, fontweight='bold')
        ax.set_ylabel('Inflation Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Inflation Rate Distribution Comparison', fontsize=16, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(fontsize=10)
        
        st.pyplot(fig)
        
        # Download button for boxplot
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Boxplot as PNG",
            data=buf,
            file_name="inflation_boxplot.png",
            mime="image/png"
        )
    
    # 5. Volatility Analysis
    if "Volatility Analysis" in chart_types:
        st.markdown("### 📈 Inflation Rate Volatility")
        
        # Calculate volatility (standard deviation)
        volatility = df_selected.groupby('Country Code')['Inflation_Rate'].std().sort_values(ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(volatility)), volatility.values,
                     color=plt.cm.viridis(np.linspace(0, 1, len(volatility))))
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, volatility.values)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                   f'{value:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_xlabel('Country Code', fontsize=12, fontweight='bold')
        ax.set_ylabel('Standard Deviation (%)', fontsize=12, fontweight='bold')
        ax.set_title('Inflation Rate Volatility (Standard Deviation)', fontsize=16, fontweight='bold', pad=20)
        ax.set_xticks(range(len(volatility)))
        ax.set_xticklabels(volatility.index, rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        
        st.pyplot(fig)
        
        # Download button for volatility chart
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Volatility Chart as PNG",
            data=buf,
            file_name="inflation_volatility.png",
            mime="image/png"
        )
        
        # Display volatility ranking
        st.markdown("**Volatility Ranking (Highest to Lowest):**")
        for i, (country, vol) in enumerate(volatility.items(), 1):
            st.write(f"{i}. {country} - {country_name_dict[country]}: {vol:.2f}%")
    
    # 6. Change Rate Analysis
    if "Change Rate Analysis" in chart_types:
        st.markdown("### 🔄 Annual Change Rate Analysis")
        
        # Calculate annual change rates
        df_sorted = df_selected.sort_values(['Country Code', 'Year'])
        df_sorted['Change_Rate'] = df_sorted.groupby('Country Code')['Inflation_Rate'].pct_change() * 100
        
        num_cols = 3
        num_rows = (len(selected_countries) + num_cols - 1) // num_cols
        
        fig, axes = plt.subplots(num_rows, num_cols, figsize=(16, 4*num_rows))
        axes = axes.flatten()
        
        for i, country in enumerate(selected_countries):
            country_data = df_sorted[df_sorted['Country Code'] == country]
            
            axes[i].bar(country_data['Year'], country_data['Change_Rate'],
                       color=colors[i], alpha=0.7, edgecolor='black')
            
            mean_change = country_data['Change_Rate'].mean()
            axes[i].axhline(y=mean_change, color='red', linestyle='--',
                          label=f'Mean: {mean_change:.2f}%', linewidth=2)
            
            axes[i].set_xlabel('Year', fontsize=10)
            axes[i].set_ylabel('Change Rate (%)', fontsize=10)
            axes[i].set_title(f'{country} - {country_name_dict[country]}', fontsize=11, fontweight='bold')
            axes[i].legend(fontsize=8)
            axes[i].grid(True, alpha=0.3)
            axes[i].tick_params(axis='x', rotation=45)
        
        # Hide empty subplots
        for i in range(len(selected_countries), len(axes)):
            axes[i].set_visible(False)
        
        plt.suptitle('Annual Inflation Rate Change Analysis', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Download button for change rate chart
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Change Rate Chart as PNG",
            data=buf,
            file_name="inflation_change_rate.png",
            mime="image/png"
        )
    
    # 7. Interactive Chart (Plotly)
    if "Interactive Chart" in chart_types:
        st.markdown("### 🎮 Interactive Chart")
        
        # Create interactive line chart
        fig = px.line(df_selected, x='Year', y='Inflation_Rate', color='Country Code',
                     title='Interactive Inflation Rate Trends',
                     labels={'Inflation_Rate': 'Inflation Rate (%)', 
                            'Year': 'Year',
                            'Country Code': 'Country Code'},
                     hover_data=['Country Name'],
                     line_shape='spline',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        
        fig.add_hline(y=2, line_dash="dash", line_color="red",
                     annotation_text="2% Inflation Target", 
                     annotation_position="bottom right")
        
        fig.update_layout(
            height=600,
            showlegend=True,
            legend_title_text='Country Code',
            xaxis_title="Year",
            yaxis_title="Inflation Rate (%)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Download button for interactive chart as HTML
        html = fig.to_html()
        st.download_button(
            label="📥 Download Interactive Chart as HTML",
            data=html,
            file_name="interactive_inflation_chart.html",
            mime="text/html"
        )
    
    # 8. Country Comparison Matrix (NEW FEATURE)
    if "Country Comparison Matrix" in chart_types:
        st.markdown("### 🔄 Country Comparison Matrix")
        
        # Create a comparison matrix
        comparison_data = []
        
        for i, country1 in enumerate(selected_countries):
            for j, country2 in enumerate(selected_countries):
                if i < j:  # Only compare each pair once
                    data1 = df_selected[df_selected['Country Code'] == country1]['Inflation_Rate'].values
                    data2 = df_selected[df_selected['Country Code'] == country2]['Inflation_Rate'].values
                    
                    # Ensure same length
                    min_len = min(len(data1), len(data2))
                    if min_len > 0:
                        data1 = data1[:min_len]
                        data2 = data2[:min_len]
                        
                        # Calculate correlation
                        correlation = np.corrcoef(data1, data2)[0, 1]
                        
                        # Calculate mean difference
                        mean_diff = np.mean(data1) - np.mean(data2)
                        
                        # Calculate volatility ratio
                        vol1 = np.std(data1)
                        vol2 = np.std(data2)
                        vol_ratio = vol1 / vol2 if vol2 != 0 else np.nan
                        
                        comparison_data.append({
                            'Country 1': country1,
                            'Country 2': country2,
                            'Correlation': correlation,
                            'Mean Difference': mean_diff,
                            'Volatility Ratio': vol_ratio,
                            'Country 1 Mean': np.mean(data1),
                            'Country 2 Mean': np.mean(data2),
                            'Country 1 Volatility': vol1,
                            'Country 2 Volatility': vol2
                        })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Display comparison table
            st.dataframe(
                comparison_df[['Country 1', 'Country 2', 'Correlation', 'Mean Difference', 'Volatility Ratio']].round(3),
                use_container_width=True,
                height=300
            )
            
            # Create comparison heatmap
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Correlation heatmap
            corr_matrix = comparison_df.pivot(index='Country 1', columns='Country 2', values='Correlation')
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, square=True, ax=ax1, cbar_kws={'label': 'Correlation'})
            ax1.set_title('Correlation Comparison Matrix', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Country 2')
            ax1.set_ylabel('Country 1')
            
            # Mean difference heatmap
            mean_diff_matrix = comparison_df.pivot(index='Country 1', columns='Country 2', values='Mean Difference')
            sns.heatmap(mean_diff_matrix, annot=True, fmt='.2f', cmap='RdBu_r', 
                       center=0, square=True, ax=ax2, cbar_kws={'label': 'Mean Difference (%)'})
            ax2.set_title('Mean Difference Comparison Matrix', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Country 2')
            ax2.set_ylabel('Country 1')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Download button for comparison matrix
            buf = fig_to_bytes(fig)
            st.download_button(
                label="📥 Download Comparison Matrix as PNG",
                data=buf,
                file_name="country_comparison_matrix.png",
                mime="image/png"
            )
            
            # Export comparison data
            csv_comparison = comparison_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Comparison Data (CSV)",
                data=csv_comparison,
                file_name="country_comparison_data.csv",
                mime="text/csv"
            )
        else:
            st.info("Not enough data for country comparison matrix")
    
    # Statistical Analysis Section
    st.markdown('<h2 class="sub-header">📊 Statistical Analysis</h2>', unsafe_allow_html=True)
    
    # Calculate detailed statistics
    detailed_stats = []
    for country in selected_countries:
        country_data = df_selected[df_selected['Country Code'] == country]
        
        if not country_data.empty:
            stats = {
                'Country Code': country,
                'Country Name': country_name_dict[country],
                'Years': country_data['Inflation_Rate'].count(),
                'Mean (%)': country_data['Inflation_Rate'].mean(),
                'Median (%)': country_data['Inflation_Rate'].median(),
                'Std Dev (%)': country_data['Inflation_Rate'].std(),
                'Max (%)': country_data['Inflation_Rate'].max(),
                'Min (%)': country_data['Inflation_Rate'].min(),
                'Range (%)': country_data['Inflation_Rate'].max() - country_data['Inflation_Rate'].min(),
                'Years > 2%': (country_data['Inflation_Rate'] > 2).sum(),
                'Years < 0%': (country_data['Inflation_Rate'] < 0).sum()
            }
            detailed_stats.append(stats)
    
    stats_df = pd.DataFrame(detailed_stats)
    
    # Format display
    display_df = stats_df.copy()
    for col in ['Mean (%)', 'Median (%)', 'Std Dev (%)', 'Max (%)', 'Min (%)', 'Range (%)']:
        display_df[col] = display_df[col].round(2)
    
    # Display statistics table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Key Insights
    st.markdown("### 💡 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Highest and lowest inflation
        highest_country = stats_df.loc[stats_df['Max (%)'].idxmax()]
        lowest_country = stats_df.loc[stats_df['Min (%)'].idxmin()]
        
        st.markdown(f"""
        **Highest Inflation Peak:**
        - Country: {highest_country['Country Code']} ({highest_country['Country Name']})
        - Peak Inflation: {highest_country['Max (%)']:.2f}%
        """)
        
        st.markdown(f"""
        **Lowest Inflation:**
        - Country: {lowest_country['Country Code']} ({lowest_country['Country Name']})
        - Minimum Inflation: {lowest_country['Min (%)']:.2f}%
        """)
    
    with col2:
        # Most and least volatile
        most_volatile = stats_df.loc[stats_df['Std Dev (%)'].idxmax()]
        least_volatile = stats_df.loc[stats_df['Std Dev (%)'].idxmin()]
        
        st.markdown(f"""
        **Most Volatile:**
        - Country: {most_volatile['Country Code']} ({most_volatile['Country Name']})
        - Standard Deviation: {most_volatile['Std Dev (%)']:.2f}%
        """)
        
        st.markdown(f"""
        **Most Stable:**
        - Country: {least_volatile['Country Code']} ({least_volatile['Country Name']})
        - Standard Deviation: {least_volatile['Std Dev (%)']:.2f}%
        """)
    
    # Correlation Analysis
    if "Correlation Analysis" in chart_types:
        st.markdown("### 🔗 Correlation Analysis")
        
        # Create correlation matrix
        pivot_corr = df_selected.pivot_table(
            index='Year',
            columns='Country Code',
            values='Inflation_Rate'
        ).corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot_corr, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=0.5,
                   cbar_kws={'label': 'Correlation Coefficient'},
                   ax=ax)
        
        ax.set_title('Inflation Rate Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        st.pyplot(fig)
        
        # Download button for correlation matrix
        buf = fig_to_bytes(fig)
        st.download_button(
            label="📥 Download Correlation Matrix as PNG",
            data=buf,
            file_name="inflation_correlation_matrix.png",
            mime="image/png"
        )
        
        # Find strongest correlations using helper function
        max_country1, max_country2, min_country1, min_country2, max_corr, min_corr = find_strongest_correlations(pivot_corr)
        
        if max_country1 is not None:
            st.markdown(f"""
            **Strongest Positive Correlation:**
            - {max_country1} and {max_country2}: {max_corr:.3f}
            
            **Strongest Negative Correlation:**
            - {min_country1} and {min_country2}: {min_corr:.3f}
            """)
        else:
            st.info("Not enough data for correlation analysis")
        
        # Display correlation matrix as table
        with st.expander("📊 View Correlation Matrix Table", expanded=False):
            st.dataframe(
                pivot_corr.round(3),
                use_container_width=True
            )
    
    # Export section
    st.markdown("---")
    st.markdown("### 📤 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export filtered data
        csv_data = df_selected.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv_data,
            file_name="inflation_analysis_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Export statistics
        csv_stats = stats_df.to_csv(index=False)
        st.download_button(
            label="📊 Download Statistics",
            data=csv_stats,
            file_name="inflation_statistics.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Export correlation matrix (if available)
        if "Correlation Analysis" in chart_types:
            csv_corr = pivot_corr.to_csv()
            st.download_button(
                label="🔗 Download Correlation Matrix",
                data=csv_corr,
                file_name="inflation_correlation.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Enable Correlation Analysis to export correlation matrix")

else:
    # Welcome screen when no data is loaded
    st.info("👈 Please select a data source from the sidebar to begin analysis.")
    
    # Display sample data structure
    st.markdown("### 📋 Expected Data Structure")
    
    sample_data = pd.DataFrame({
        'Country Name': ['United States', 'China', 'Japan'],
        'Country Code': ['USA', 'CHN', 'JPN'],
        '[YR2000]': [3.4, 0.4, -0.7],
        '[YR2001]': [2.8, 0.7, -0.7],
        '[YR2002]': [1.6, -0.8, -0.9]
    })
    
    st.dataframe(sample_data, use_container_width=True)
    
    st.markdown("""
    ### 📝 How to use this dashboard:
    
    1. **Upload your data** or use the sample data
    2. **Configure analysis parameters** in the sidebar
    3. **Select charts** you want to display
    4. **Explore insights** from the visualizations
    5. **Export results** for further analysis
    
    ### 🔧 Features included:
    - Multiple chart types (trends, heatmaps, distributions, etc.)
    - Interactive filtering and selection
    - Statistical analysis and insights
    - Correlation analysis between countries
    - Export functionality for data and charts
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #6B7280; font-size: 0.9rem;'>
    Inflation Analysis Dashboard • Built with Streamlit • For ACC102 Information System for Accountants
    </div>
    """,
    unsafe_allow_html=True
)