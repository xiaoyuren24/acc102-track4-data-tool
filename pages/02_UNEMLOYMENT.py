"""
UNEMPLOYMENT RATE ANALYSIS DASHBOARD
Complete Streamlit application for analyzing unemployment data
Save as: unemployment_dashboard.py
Run with: streamlit run unemployment_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Unemployment Rate Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS STYLES ====================
st.markdown("""
<style>
    /* Main header style */
    .main-header {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric card style */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #2a5298;
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Unemployment rate color coding */
    .very-low { color: #27ae60; font-weight: bold; }
    .low { color: #2ecc71; font-weight: bold; }
    .medium { color: #f39c12; font-weight: bold; }
    .high { color: #e67e22; font-weight: bold; }
    .very-high { color: #e74c3c; font-weight: bold; }
    
    /* Button style */
    .stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Tab style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: #f8f9fa;
    }
    
    /* Data table style */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== DATA LOADING AND PROCESSING ====================
@st.cache_data
def load_and_transform_data():
    """Load and transform unemployment data"""
    try:
        # First try to create sample data
        df_long = create_sample_data()
        return df_long
        
    except Exception as e:
        st.error(f"Data loading failed: {str(e)}")
        return create_sample_data()

def convert_to_long_format(df_wide):
    """Convert wide format data to long format"""
    # Identify year columns - handle different column name patterns
    year_columns = []
    for col in df_wide.columns:
        if any(str_pattern in str(col) for str_pattern in ['[YR', 'YR', '19', '20']):
            try:
                # Try to extract year
                year = int(str(col).split()[-1].replace('[', '').replace(']', ''))
                if 1900 <= year <= 2100:
                    year_columns.append(col)
            except:
                # If not a year column, check if it's a year
                try:
                    year = int(col)
                    if 1900 <= year <= 2100:
                        year_columns.append(col)
                except:
                    continue
    
    id_columns = ['Series Name', 'Series Code', 'Country Name', 'Country Code']
    
    # Convert to long format
    df_long = pd.melt(
        df_wide,
        id_vars=id_columns,
        value_vars=year_columns,
        var_name='Year_Column',
        value_name='Unemployment_Rate'
    )
    
    # Extract year from Year_Column
    df_long['Year'] = df_long['Year_Column'].astype(str).str.extract(r'(\d{4})').astype(int)
    
    # Handle missing values
    df_long['Unemployment_Rate'] = pd.to_numeric(df_long['Unemployment_Rate'], errors='coerce')
    
    # Rename columns
    df_long = df_long.rename(columns={
        'Series Name': 'Indicator_Name',
        'Series Code': 'Indicator_Code',
        'Country Name': 'Country_Name',
        'Country Code': 'Country_Code'
    })
    
    # Select required columns
    df_long = df_long[['Indicator_Name', 'Indicator_Code', 'Country_Name', 'Country_Code', 'Year', 'Unemployment_Rate']]
    
    return df_long

def create_sample_data():
    """Create comprehensive sample data for demonstration"""
    years = list(range(1990, 2026))
    
    # Define countries with realistic unemployment patterns
    countries = {
        'AUS': {'name': 'Australia', 'base_rate': 8.0, 'trend': 'stable', 'volatility': 0.5},
        'CHN': {'name': 'China', 'base_rate': 3.0, 'trend': 'declining', 'volatility': 0.3},
        'DEU': {'name': 'Germany', 'base_rate': 6.0, 'trend': 'declining', 'volatility': 0.4},
        'FIN': {'name': 'Finland', 'base_rate': 7.0, 'trend': 'stable', 'volatility': 0.6},
        'FRA': {'name': 'France', 'base_rate': 9.0, 'trend': 'stable', 'volatility': 0.5},
        'GBR': {'name': 'United Kingdom', 'base_rate': 7.0, 'trend': 'declining', 'volatility': 0.7},
        'ITA': {'name': 'Italy', 'base_rate': 10.0, 'trend': 'stable', 'volatility': 0.8},
        'JPN': {'name': 'Japan', 'base_rate': 3.0, 'trend': 'stable', 'volatility': 0.3},
        'USA': {'name': 'United States', 'base_rate': 6.0, 'trend': 'declining', 'volatility': 0.9}
    }
    
    data = []
    for country_code, country_info in countries.items():
        country_name = country_info['name']
        base_rate = country_info['base_rate']
        volatility = country_info['volatility']
        
        for i, year in enumerate(years):
            # Base trend
            time_factor = (i / len(years)) * 10
            
            # Apply country-specific trend
            if country_info['trend'] == 'declining':
                trend = -0.05 * time_factor
            elif country_info['trend'] == 'increasing':
                trend = 0.05 * time_factor
            else:
                trend = 0
            
            # Add business cycle effects
            cycle = np.sin(2 * np.pi * i / 8) * 1.5
            
            # Add economic shocks
            shock = 0
            if year == 2008:  # Financial crisis
                shock = 3.0
            elif year == 2020:  # COVID-19 pandemic
                shock = 4.0
            elif year == 2021:  # Recovery
                shock = -2.0
            
            # Calculate unemployment rate
            unemployment_rate = base_rate + trend + cycle + shock + np.random.normal(0, volatility)
            
            # Ensure reasonable bounds
            unemployment_rate = max(1.0, min(20.0, unemployment_rate))
            
            data.append({
                'Indicator_Name': 'Unemployment, total (% of total labor force)',
                'Indicator_Code': 'SL.UEM.TOTL.ZS',
                'Country_Name': country_name,
                'Country_Code': country_code,
                'Year': year,
                'Unemployment_Rate': round(unemployment_rate, 3)
            })
    
    df = pd.DataFrame(data)
    return df

# ==================== ANALYSIS FUNCTIONS ====================
def data_overview(df):
    """Provide comprehensive data overview"""
    stats = {}
    
    # Basic information
    stats['Total Records'] = f"{len(df):,}"
    stats['Number of Countries'] = df['Country_Code'].nunique()
    stats['Year Range'] = f"{df['Year'].min()} - {df['Year'].max()}"
    stats['Unique Indicators'] = len(df['Indicator_Name'].unique())
    
    # Countries information
    countries_df = df[['Country_Name', 'Country_Code']].drop_duplicates()
    stats['Countries Covered'] = ", ".join([f"{row['Country_Code']}: {row['Country_Name']}" 
                                           for _, row in countries_df.iterrows()])
    
    # Data quality
    total_records = len(df)
    missing_records = df['Unemployment_Rate'].isnull().sum()
    valid_records = total_records - missing_records
    stats['Valid Records'] = f"{valid_records:,} ({valid_records/total_records*100:.1f}%)"
    stats['Missing Records'] = f"{missing_records:,} ({missing_records/total_records*100:.1f}%)"
    
    # Statistical summary
    valid_rates = df['Unemployment_Rate'].dropna()
    if len(valid_rates) > 0:
        stats['Mean Unemployment Rate'] = f"{valid_rates.mean():.2f}%"
        stats['Median Unemployment Rate'] = f"{valid_rates.median():.2f}%"
        stats['Standard Deviation'] = f"{valid_rates.std():.2f}%"
        stats['Minimum Rate'] = f"{valid_rates.min():.2f}%"
        stats['Maximum Rate'] = f"{valid_rates.max():.2f}%"
        stats['25th Percentile'] = f"{valid_rates.quantile(0.25):.2f}%"
        stats['75th Percentile'] = f"{valid_rates.quantile(0.75):.2f}%"
    
    return stats

def analyze_country(df, country_code):
    """Analyze specific country's unemployment data"""
    country_data = df[df['Country_Code'] == country_code].copy()
    
    if country_data.empty:
        return {}, None
    
    valid_data = country_data.dropna(subset=['Unemployment_Rate'])
    if len(valid_data) == 0:
        return {}, None
    
    country_name = country_data['Country_Name'].iloc[0]
    valid_data = valid_data.sort_values('Year')
    
    # Calculate statistics
    stats = {}
    stats['Country Name'] = country_name
    stats['Country Code'] = country_code
    stats['Years Covered'] = f"{valid_data['Year'].min()} - {valid_data['Year'].max()}"
    stats['Data Points'] = len(valid_data)
    stats['Average Unemployment Rate'] = f"{valid_data['Unemployment_Rate'].mean():.2f}%"
    
    # Get current rate
    latest_year = valid_data['Year'].max()
    latest_data = valid_data[valid_data['Year'] == latest_year]
    if not latest_data.empty:
        stats['Current Rate'] = f"{latest_data['Unemployment_Rate'].values[0]:.2f}%"
    else:
        stats['Current Rate'] = "N/A"
    
    stats['Historical Maximum'] = f"{valid_data['Unemployment_Rate'].max():.2f}%"
    stats['Historical Minimum'] = f"{valid_data['Unemployment_Rate'].min():.2f}%"
    stats['Volatility (Std Dev)'] = f"{valid_data['Unemployment_Rate'].std():.2f}%"
    
    # Determine unemployment level
    avg_rate = valid_data['Unemployment_Rate'].mean()
    if avg_rate < 3:
        level = "Very Low"
        level_class = "very-low"
    elif avg_rate < 5:
        level = "Low"
        level_class = "low"
    elif avg_rate < 8:
        level = "Medium"
        level_class = "medium"
    elif avg_rate < 12:
        level = "High"
        level_class = "high"
    else:
        level = "Very High"
        level_class = "very-high"
    
    stats['Unemployment Level'] = level
    stats['Level Class'] = level_class
    
    # Trend analysis
    if len(valid_data) >= 10:
        valid_data['5_Year_MA'] = valid_data['Unemployment_Rate'].rolling(window=5, min_periods=1).mean()
        valid_data['10_Year_MA'] = valid_data['Unemployment_Rate'].rolling(window=10, min_periods=1).mean()
        valid_data['Annual_Change'] = valid_data['Unemployment_Rate'].diff()
        
        stats['Last 10-Year Average'] = f"{valid_data['Unemployment_Rate'].tail(10).mean():.2f}%"
        stats['Last 5-Year Average'] = f"{valid_data['Unemployment_Rate'].tail(5).mean():.2f}%"
        if 'Annual_Change' in valid_data.columns:
            stats['Maximum Annual Increase'] = f"{valid_data['Annual_Change'].max():.2f}%"
            stats['Maximum Annual Decrease'] = f"{valid_data['Annual_Change'].min():.2f}%"
        
        # Trend direction
        if len(valid_data) > 5:
            recent_trend = "Improving" if valid_data['Unemployment_Rate'].iloc[-1] < valid_data['Unemployment_Rate'].iloc[-6] else "Worsening"
            stats['Recent Trend (5 years)'] = recent_trend
    
    return stats, valid_data

def calculate_trend_analysis(df, country_code):
    """Calculate trend analysis for a country"""
    country_data = df[df['Country_Code'] == country_code].copy()
    valid_data = country_data.dropna(subset=['Unemployment_Rate']).sort_values('Year')
    
    if len(valid_data) < 10:
        return {}, None
    
    # Calculate moving averages
    valid_data['5_Year_MA'] = valid_data['Unemployment_Rate'].rolling(window=5, min_periods=1).mean()
    valid_data['10_Year_MA'] = valid_data['Unemployment_Rate'].rolling(window=10, min_periods=1).mean()
    valid_data['Annual_Change'] = valid_data['Unemployment_Rate'].diff()
    valid_data['Cumulative_Change'] = valid_data['Unemployment_Rate'] - valid_data['Unemployment_Rate'].iloc[0]
    
    trend_stats = {
        'Starting Rate': f"{valid_data['Unemployment_Rate'].iloc[0]:.2f}%",
        'Ending Rate': f"{valid_data['Unemployment_Rate'].iloc[-1]:.2f}%",
        'Total Change': f"{valid_data['Cumulative_Change'].iloc[-1]:.2f}%",
        'Average Annual Change': f"{valid_data['Annual_Change'].mean():.3f}%",
        'Volatility (Std of Annual Changes)': f"{valid_data['Annual_Change'].std():.3f}%",
        'Last 10-Year Average': f"{valid_data['Unemployment_Rate'].tail(10).mean():.2f}%",
        'Last 5-Year Average': f"{valid_data['Unemployment_Rate'].tail(5).mean():.2f}%"
    }
    
    return trend_stats, valid_data

def perform_advanced_analysis(df, selected_countries):
    """Perform advanced statistical analysis"""
    results = {}
    
    # Get latest year data
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year].dropna(subset=['Unemployment_Rate'])
    latest_data = latest_data[latest_data['Country_Code'].isin(selected_countries)]
    
    if len(latest_data) < 2:
        return results
    
    # 1. ANOVA test
    from scipy.stats import f_oneway
    groups = []
    for country in selected_countries:
        country_rates = latest_data[latest_data['Country_Code'] == country]['Unemployment_Rate']
        if len(country_rates) > 0:
            groups.append(country_rates)
    
    if len(groups) >= 2:
        f_stat, p_value = f_oneway(*groups)
        results['ANOVA F-statistic'] = f"{f_stat:.3f}"
        results['ANOVA p-value'] = f"{p_value:.4f}"
        results['ANOVA Interpretation'] = "Significant differences exist between countries" if p_value < 0.05 else "No significant differences between countries"
    
    # 2. Regression analysis (time trend)
    all_data = df.dropna(subset=['Unemployment_Rate'])
    all_data = all_data[all_data['Country_Code'].isin(selected_countries)]
    
    if len(all_data) > 0:
        from scipy.stats import linregress
        slope, intercept, r_value, p_value, std_err = linregress(
            all_data['Year'], all_data['Unemployment_Rate']
        )
        
        results['Time Trend Slope'] = f"{slope:.4f}"
        results['R-squared'] = f"{r_value**2:.4f}"
        results['Trend p-value'] = f"{p_value:.4f}"
        results['Trend Direction'] = f"{'Increasing' if slope > 0 else 'Decreasing'}"
        results['Trend Significance'] = "Significant" if p_value < 0.05 else "Not Significant"
    
    # 3. Correlation matrix
    pivot_df = df.pivot_table(
        index='Year',
        columns='Country_Code',
        values='Unemployment_Rate'
    )
    pivot_df = pivot_df[selected_countries].dropna()
    
    if len(pivot_df.columns) >= 2:
        corr_matrix = pivot_df.corr()
        results['Correlation Matrix'] = corr_matrix
    
    return results

# ==================== VISUALIZATION FUNCTIONS ====================
def plot_unemployment_trend_matplotlib(df, countries, start_year, end_year):
    """Plot unemployment rate trends using Matplotlib"""
    filtered_df = df[
        (df['Country_Code'].isin(countries)) & 
        (df['Year'] >= start_year) & 
        (df['Year'] <= end_year)
    ].dropna(subset=['Unemployment_Rate'])
    
    if filtered_df.empty:
        return None
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    
    # Plot 1: Line chart
    ax1 = axes[0]
    colors = ['#FF6B6B', '#FF8E53', '#FFC154', '#FFE66D', '#A8E6CF', '#6A0572', '#AB83A1', '#3B8EA5', '#F5B700']
    
    for i, country in enumerate(countries):
        country_data = filtered_df[filtered_df['Country_Code'] == country]
        if not country_data.empty:
            ax1.plot(country_data['Year'], country_data['Unemployment_Rate'], 
                    marker='o', linewidth=2, markersize=4, label=country, color=colors[i % len(colors)])
    
    ax1.set_title(f'Unemployment Rate Trends ({start_year}-{end_year})', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Unemployment Rate (%)', fontsize=12)
    ax1.legend(title='Countries', fontsize=10, title_fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Add reference lines
    ax1.axhline(y=5, color='green', linestyle='--', alpha=0.5, label='5% - Low')
    ax1.axhline(y=8, color='orange', linestyle='--', alpha=0.5, label='8% - Medium')
    ax1.axhline(y=12, color='red', linestyle='--', alpha=0.5, label='12% - High')
    
    # Plot 2: Bar chart for latest year
    ax2 = axes[1]
    latest_year = filtered_df['Year'].max()
    latest_data = filtered_df[filtered_df['Year'] == latest_year]
    latest_data = latest_data.sort_values('Unemployment_Rate', ascending=False)
    
    # Color coding
    bar_colors = []
    for rate in latest_data['Unemployment_Rate']:
        if rate < 5:
            bar_colors.append('#2ecc71')
        elif rate < 8:
            bar_colors.append('#f39c12')
        else:
            bar_colors.append('#e74c3c')
    
    bars = ax2.bar(latest_data['Country_Code'], latest_data['Unemployment_Rate'], 
                   color=bar_colors, alpha=0.7)
    ax2.set_title(f'{latest_year} Unemployment Rates by Country', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Country Code', fontsize=11)
    ax2.set_ylabel('Unemployment Rate (%)', fontsize=11)
    ax2.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    return fig

def plot_country_comparison_matplotlib(df, year):
    """Create comparison bar chart using Matplotlib"""
    year_data = df[df['Year'] == year].dropna(subset=['Unemployment_Rate'])
    
    if year_data.empty:
        return None
    
    year_data = year_data.sort_values('Unemployment_Rate', ascending=False)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Color coding
    colors = []
    for rate in year_data['Unemployment_Rate']:
        if rate < 5:
            colors.append('#2ecc71')
        elif rate < 8:
            colors.append('#f39c12')
        elif rate < 12:
            colors.append('#e67e22')
        else:
            colors.append('#e74c3c')
    
    bars = ax.bar(year_data['Country_Name'], year_data['Unemployment_Rate'], 
                  color=colors, alpha=0.8)
    
    ax.set_title(f'Unemployment Rate Comparison - {year}', fontsize=16, fontweight='bold')
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Unemployment Rate (%)', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    
    # Add reference lines
    ax.axhline(y=5, color='green', linestyle='--', alpha=0.5)
    ax.axhline(y=8, color='orange', linestyle='--', alpha=0.5)
    ax.axhline(y=12, color='red', linestyle='--', alpha=0.5)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # Add legend
    import matplotlib.patches as mpatches
    legend_elements = [
        mpatches.Patch(color='#2ecc71', label='Very Low (<5%)'),
        mpatches.Patch(color='#f39c12', label='Low (5-8%)'),
        mpatches.Patch(color='#e67e22', label='Medium (8-12%)'),
        mpatches.Patch(color='#e74c3c', label='High (>12%)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    return fig

def plot_correlation_heatmap_matplotlib(df, countries):
    """Create correlation heatmap using Matplotlib"""
    pivot_df = df.pivot_table(
        index='Year',
        columns='Country_Code',
        values='Unemployment_Rate'
    )
    
    pivot_df = pivot_df[countries].dropna()
    
    if len(pivot_df.columns) < 2:
        return None
    
    corr_matrix = pivot_df.corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1)
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Correlation Coefficient', rotation=-90, va="bottom")
    
    # Set ticks
    ax.set_xticks(np.arange(len(corr_matrix.columns)))
    ax.set_yticks(np.arange(len(corr_matrix.index)))
    ax.set_xticklabels(corr_matrix.columns)
    ax.set_yticklabels(corr_matrix.index)
    
    # Rotate x-axis labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add correlation values in cells
    for i in range(len(corr_matrix.index)):
        for j in range(len(corr_matrix.columns)):
            text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                          ha="center", va="center", color="w" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black",
                          fontsize=9)
    
    ax.set_title('Unemployment Rate Correlation Heatmap', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig

def plot_distribution_analysis_matplotlib(df):
    """Create distribution analysis plots using Matplotlib"""
    latest_year = df['Year'].max()
    latest_data = df[df['Year'] == latest_year].dropna(subset=['Unemployment_Rate'])
    
    if latest_data.empty:
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Histogram
    ax1 = axes[0, 0]
    ax1.hist(latest_data['Unemployment_Rate'], bins=15, edgecolor='black', alpha=0.7, color='skyblue')
    ax1.set_title(f'Distribution of Unemployment Rates ({latest_year})', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Unemployment Rate (%)', fontsize=11)
    ax1.set_ylabel('Frequency', fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Add mean and median lines
    mean_rate = latest_data['Unemployment_Rate'].mean()
    median_rate = latest_data['Unemployment_Rate'].median()
    ax1.axvline(mean_rate, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_rate:.2f}%')
    ax1.axvline(median_rate, color='green', linestyle='--', linewidth=2, label=f'Median: {median_rate:.2f}%')
    ax1.legend()
    
    # Plot 2: Box plot
    ax2 = axes[0, 1]
    box_data = [latest_data['Unemployment_Rate']]
    box_labels = [f'{latest_year}']
    bp = ax2.boxplot(box_data, labels=box_labels, patch_artist=True)
    
    for box in bp['boxes']:
        box.set(facecolor='lightblue', alpha=0.7)
    
    ax2.set_title('Box Plot of Unemployment Rates', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Unemployment Rate (%)', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Violin plot
    ax3 = axes[1, 0]
    violin_parts = ax3.violinplot(latest_data['Unemployment_Rate'], showmeans=True, showmedians=True)
    
    violin_parts['bodies'][0].set_facecolor('lightcoral')
    violin_parts['bodies'][0].set_alpha(0.7)
    violin_parts['cbars'].set_color('black')
    violin_parts['cmins'].set_color('black')
    violin_parts['cmaxes'].set_color('black')
    violin_parts['cmeans'].set_color('red')
    violin_parts['cmedians'].set_color('green')
    
    ax3.set_title('Violin Plot of Unemployment Rates', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Unemployment Rate (%)', fontsize=11)
    ax3.set_xticks([1])
    ax3.set_xticklabels([f'{latest_year}'])
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: QQ plot for normality test
    ax4 = axes[1, 1]
    stats.probplot(latest_data['Unemployment_Rate'], dist="norm", plot=ax4)
    ax4.set_title('Q-Q Plot (Normality Test)', fontsize=14, fontweight='bold')
    ax4.set_xlabel('Theoretical Quantiles', fontsize=11)
    ax4.set_ylabel('Sample Quantiles', fontsize=11)
    ax4.grid(True, alpha=0.3)
    
    # Calculate normality test
    from scipy.stats import shapiro
    stat, p_value = shapiro(latest_data['Unemployment_Rate'])
    ax4.text(0.05, 0.95, f'Shapiro-Wilk Test:\np-value = {p_value:.4f}', 
             transform=ax4.transAxes, fontsize=10,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig

def plot_time_series_analysis_matplotlib(df, country_code):
    """Create detailed time series analysis using Matplotlib"""
    country_data = df[df['Country_Code'] == country_code].copy()
    country_data = country_data.dropna(subset=['Unemployment_Rate']).sort_values('Year')
    
    if country_data.empty or len(country_data) < 10:
        return None
    
    country_name = country_data['Country_Name'].iloc[0]
    
    # Calculate moving averages
    country_data['5_Year_MA'] = country_data['Unemployment_Rate'].rolling(window=5, min_periods=1).mean()
    country_data['10_Year_MA'] = country_data['Unemployment_Rate'].rolling(window=10, min_periods=1).mean()
    country_data['Annual_Change'] = country_data['Unemployment_Rate'].diff()
    country_data['Cumulative_Change'] = country_data['Unemployment_Rate'] - country_data['Unemployment_Rate'].iloc[0]
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Plot 1: Original data with moving averages
    ax1 = axes[0]
    ax1.plot(country_data['Year'], country_data['Unemployment_Rate'], 
             'b-', linewidth=1.5, alpha=0.5, label='Original Data')
    ax1.plot(country_data['Year'], country_data['5_Year_MA'], 
             'g-', linewidth=2, label='5-Year Moving Average')
    ax1.plot(country_data['Year'], country_data['10_Year_MA'], 
             'r-', linewidth=2.5, label='10-Year Moving Average')
    
    ax1.set_title(f'{country_name} ({country_code}) - Unemployment Rate Analysis', 
                  fontsize=16, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Unemployment Rate (%)', fontsize=12)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Add reference lines
    ax1.axhline(y=5, color='green', linestyle='--', alpha=0.3)
    ax1.axhline(y=8, color='orange', linestyle='--', alpha=0.3)
    ax1.axhline(y=12, color='red', linestyle='--', alpha=0.3)
    
    # Plot 2: Annual changes
    ax2 = axes[1]
    bar_colors = ['green' if x > 0 else 'red' for x in country_data['Annual_Change']]
    bars = ax2.bar(country_data['Year'], country_data['Annual_Change'], 
                   color=bar_colors, alpha=0.6, width=0.8)
    
    ax2.set_title('Annual Changes in Unemployment Rate', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Annual Change (%)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Cumulative change
    ax3 = axes[2]
    ax3.plot(country_data['Year'], country_data['Cumulative_Change'], 
             'purple', linewidth=2, marker='o', markersize=4)
    ax3.fill_between(country_data['Year'], 0, country_data['Cumulative_Change'],
                     alpha=0.3, color='purple')
    
    ax3.set_title('Cumulative Change from Starting Year', fontsize=14, fontweight='bold')
    ax3.set_xlabel('Year', fontsize=12)
    ax3.set_ylabel('Cumulative Change (%)', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    plt.tight_layout()
    return fig

# ==================== MAIN APPLICATION ====================
def main():
    """Main application function"""
    
    # Application title
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0;">📊 World Bank Unemployment Rate Analysis Dashboard</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Comprehensive Data Analysis Tool with Jupyter Notebook Features</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading and processing unemployment rate data..."):
        df = load_and_transform_data()
    
    if df.empty:
        st.error("Unable to load data. Please check your internet connection.")
        return
    
    # Display success message
    st.success(f"✅ Data loaded successfully! Total {len(df):,} data points covering {df['Year'].min()}-{df['Year'].max()}")
    
    # ==================== SIDEBAR ====================
    with st.sidebar:
        st.markdown('<div class="section-header">📊 Data Overview</div>', unsafe_allow_html=True)
        
        # Calculate and display statistics
        stats = data_overview(df)
        
        # Display key metrics in cards
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Records", stats['Total Records'])
            st.metric("Number of Countries", stats['Number of Countries'])
        
        with col2:
            st.metric("Year Range", stats['Year Range'])
            st.metric("Valid Records", stats['Valid Records'])
        
        st.markdown("---")
        
        # Analysis settings
        st.markdown('<div class="section-header">⚙️ Analysis Settings</div>', unsafe_allow_html=True)
        
        # Country selection
        available_countries = sorted(df['Country_Code'].unique())
        selected_countries = st.multiselect(
            "Select Countries for Analysis",
            options=available_countries,
            default=['CHN', 'USA', 'JPN', 'DEU', 'GBR', 'FRA', 'ITA', 'AUS', 'FIN']
        )
        
        # Year range selection
        min_year = int(df['Year'].min())
        max_year = int(df['Year'].max())
        year_range = st.slider(
            "Select Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(max(min_year, 1990), max_year)
        )
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Trend Analysis", "Country Comparison", "Correlation Analysis", 
             "Distribution Analysis", "Time Series Analysis", "Advanced Statistics"]
        )
        
        # Visualization library selection
        viz_library = st.radio(
            "Select Visualization Library",
            ["Matplotlib/Seaborn", "Plotly (Interactive)"],
            horizontal=True
        )
        
        st.markdown("---")
        
        # Data operations
        st.markdown('<div class="section-header">🔧 Data Operations</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Reload Data", use_container_width=True):
            st.rerun()
        
        if st.button("📥 Download Processed Data", use_container_width=True):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Click to Download",
                data=csv,
                file_name="unemployment_data_processed.csv",
                mime="text/csv"
            )
    
    # ==================== MAIN CONTENT ====================
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Visual Analysis", "🔍 Data Explorer", "📊 Advanced Analysis"])
    
    with tab1:
        # Dashboard overview
        st.markdown('<div class="section-header">🏛️ Country Unemployment Overview</div>', unsafe_allow_html=True)
        
        if not selected_countries:
            st.warning("Please select at least one country from the sidebar")
        else:
            # Create country cards
            cols = st.columns(min(4, len(selected_countries)))
            
            for idx, country in enumerate(selected_countries):
                col_idx = idx % 4
                with cols[col_idx]:
                    country_stats, _ = analyze_country(df, country)
                    
                    if country_stats:
                        level_class = country_stats.get('Level Class', 'medium')
                        st.markdown(f"""
                        <div class="metric-card">
                            <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;">
                                {country_stats['Country Name']} ({country})
                            </div>
                            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;" class="{level_class}">
                                {country_stats['Average Unemployment Rate']}
                            </div>
                            <div style="font-size: 12px; color: #6c757d;">
                                <div>📅 {country_stats['Years Covered']}</div>
                                <div>📊 Level: <span class="{level_class}">{country_stats['Unemployment Level']}</span></div>
                                <div>📈 Current: {country_stats['Current Rate']}</div>
                                <div>📉 Volatility: {country_stats['Volatility (Std Dev)']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Quick statistics
        st.markdown('<div class="section-header">📊 Quick Statistics</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_rate = df['Unemployment_Rate'].dropna().mean()
            st.metric("Global Average", f"{avg_rate:.2f}%")
        
        with col2:
            latest_year = df['Year'].max()
            latest_data = df[df['Year'] == latest_year]['Unemployment_Rate'].dropna()
            st.metric(f"Latest Year ({latest_year}) Avg", f"{latest_data.mean():.2f}%")
        
        with col3:
            max_rate = df['Unemployment_Rate'].max()
            st.metric("Historical Maximum", f"{max_rate:.2f}%")
        
        with col4:
            min_rate = df['Unemployment_Rate'].min()
            st.metric("Historical Minimum", f"{min_rate:.2f}%")
    
    with tab2:
        # Visual analysis
        st.markdown('<div class="section-header">📈 Unemployment Rate Visual Analysis</div>', unsafe_allow_html=True)
        
        if not selected_countries:
            st.warning("Please select countries for analysis")
        else:
            if analysis_type == "Trend Analysis":
                if viz_library == "Matplotlib/Seaborn":
                    fig = plot_unemployment_trend_matplotlib(df, selected_countries, year_range[0], year_range[1])
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.info("No data available for the selected criteria")
                else:
                    # Plotly implementation
                    fig = go.Figure()
                    colors = ['#FF6B6B', '#FF8E53', '#FFC154', '#FFE66D', '#A8E6CF']
                    
                    for i, country in enumerate(selected_countries):
                        country_data = df[(df['Country_Code'] == country) & 
                                         (df['Year'] >= year_range[0]) & 
                                         (df['Year'] <= year_range[1])]
                        country_data = country_data.dropna(subset=['Unemployment_Rate'])
                        
                        if not country_data.empty:
                            fig.add_trace(go.Scatter(
                                x=country_data['Year'],
                                y=country_data['Unemployment_Rate'],
                                mode='lines+markers',
                                name=country,
                                line=dict(width=3, color=colors[i % len(colors)]),
                                marker=dict(size=8)
                            ))
                    
                    fig.update_layout(
                        title=f"Unemployment Rate Trends ({year_range[0]}-{year_range[1]})",
                        xaxis_title="Year",
                        yaxis_title="Unemployment Rate (%)",
                        height=500,
                        template="plotly_white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Country Comparison":
                year = st.selectbox(
                    "Select Year for Comparison",
                    options=sorted(df['Year'].unique(), reverse=True),
                    index=0
                )
                
                if viz_library == "Matplotlib/Seaborn":
                    fig = plot_country_comparison_matplotlib(df, year)
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.info(f"No data available for {year}")
                else:
                    # Plotly implementation
                    year_data = df[df['Year'] == year].dropna(subset=['Unemployment_Rate'])
                    year_data = year_data[year_data['Country_Code'].isin(selected_countries)]
                    
                    if not year_data.empty:
                        year_data = year_data.sort_values('Unemployment_Rate', ascending=False)
                        
                        fig = px.bar(
                            year_data,
                            x='Country_Name',
                            y='Unemployment_Rate',
                            title=f"{year} Unemployment Rate Comparison",
                            color='Unemployment_Rate',
                            color_continuous_scale=['#2ecc71', '#f39c12', '#e74c3c']
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Correlation Analysis":
                if len(selected_countries) >= 2:
                    if viz_library == "Matplotlib/Seaborn":
                        fig = plot_correlation_heatmap_matplotlib(df, selected_countries)
                        if fig:
                            st.pyplot(fig)
                    else:
                        # Plotly implementation
                        pivot_df = df.pivot_table(
                            index='Year',
                            columns='Country_Code',
                            values='Unemployment_Rate'
                        )
                        pivot_df = pivot_df[selected_countries].dropna()
                        
                        if len(pivot_df.columns) >= 2:
                            corr_matrix = pivot_df.corr()
                            
                            fig = px.imshow(
                                corr_matrix,
                                title="Unemployment Rate Correlation Heatmap",
                                color_continuous_scale='RdBu',
                                zmin=-1,
                                zmax=1,
                                text_auto='.2f'
                            )
                            fig.update_layout(height=400)
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select at least 2 countries for correlation analysis")
            
            elif analysis_type == "Distribution Analysis":
                if viz_library == "Matplotlib/Seaborn":
                    fig = plot_distribution_analysis_matplotlib(df)
                    if fig:
                        st.pyplot(fig)
                else:
                    # Plotly implementation
                    latest_year = df['Year'].max()
                    latest_data = df[df['Year'] == latest_year].dropna(subset=['Unemployment_Rate'])
                    
                    if not latest_data.empty:
                        fig = px.box(
                            latest_data,
                            y='Unemployment_Rate',
                            title=f"{latest_year} Unemployment Rate Distribution",
                            points='all'
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            elif analysis_type == "Time Series Analysis":
                if len(selected_countries) == 1:
                    country = selected_countries[0]
                    
                    if viz_library == "Matplotlib/Seaborn":
                        fig = plot_time_series_analysis_matplotlib(df, country)
                        if fig:
                            st.pyplot(fig)
                    else:
                        # Plotly implementation
                        country_data = df[df['Country_Code'] == country].copy()
                        country_data = country_data.dropna(subset=['Unemployment_Rate']).sort_values('Year')
                        
                        if not country_data.empty:
                            # Calculate moving averages
                            country_data['5_Year_MA'] = country_data['Unemployment_Rate'].rolling(window=5, min_periods=1).mean()
                            country_data['10_Year_MA'] = country_data['Unemployment_Rate'].rolling(window=10, min_periods=1).mean()
                            
                            fig = go.Figure()
                            
                            # Original data
                            fig.add_trace(go.Scatter(
                                x=country_data['Year'],
                                y=country_data['Unemployment_Rate'],
                                mode='lines',
                                name='Original Data',
                                line=dict(color='lightgray', width=1),
                                opacity=0.5
                            ))
                            
                            # 5-year moving average
                            fig.add_trace(go.Scatter(
                                x=country_data['Year'],
                                y=country_data['5_Year_MA'],
                                mode='lines',
                                name='5-Year Moving Average',
                                line=dict(color='orange', width=2)
                            ))
                            
                            # 10-year moving average
                            fig.add_trace(go.Scatter(
                                x=country_data['Year'],
                                y=country_data['10_Year_MA'],
                                mode='lines',
                                name='10-Year Moving Average',
                                line=dict(color='red', width=3)
                            ))
                            
                            fig.update_layout(
                                title=f"{country} - Time Series Analysis",
                                xaxis_title="Year",
                                yaxis_title="Unemployment Rate (%)",
                                height=400,
                                template="plotly_white"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select exactly one country for time series analysis")
            
            elif analysis_type == "Advanced Statistics":
                st.markdown("### 📊 Advanced Statistical Analysis")
                
                if len(selected_countries) >= 2:
                    results = perform_advanced_analysis(df, selected_countries)
                    
                    if results:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Statistical Tests")
                            for key, value in results.items():
                                if key not in ['Correlation Matrix']:
                                    st.metric(key, value)
                        
                        with col2:
                            if 'Correlation Matrix' in results:
                                st.markdown("#### Correlation Matrix")
                                st.dataframe(results['Correlation Matrix'].round(3), use_container_width=True)
                                
                                # Create heatmap
                                fig = px.imshow(
                                    results['Correlation Matrix'],
                                    title="Correlation Heatmap",
                                    color_continuous_scale='RdBu',
                                    zmin=-1,
                                    zmax=1,
                                    text_auto='.2f'
                                )
                                fig.update_layout(height=300)
                                st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Insufficient data for advanced analysis")
                else:
                    st.warning("Please select at least 2 countries for advanced statistical analysis")
    
    with tab3:
        # Data explorer
        st.markdown('<div class="section-header">🔍 Data Explorer</div>', unsafe_allow_html=True)
        
        # Data preview
        with st.expander("📋 Data Preview", expanded=True):
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Unemployment_Rate": st.column_config.NumberColumn(
                        format="%.2f%%",
                        help="Unemployment rate percentage"
                    ),
                    "Year": st.column_config.NumberColumn(
                        format="%d",
                        help="Year"
                    )
                }
            )
            
            st.caption(f"Data Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Data filtering
        with st.expander("🔎 Advanced Filtering", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_countries = st.multiselect(
                    "Filter by Country",
                    options=sorted(df['Country_Code'].unique()),
                    default=[]
                )
            
            with col2:
                filter_year_min, filter_year_max = st.slider(
                    "Filter Year Range",
                    min_value=int(df['Year'].min()),
                    max_value=int(df['Year'].max()),
                    value=(int(df['Year'].min()), int(df['Year'].max()))
                )
            
            with col3:
                if not df['Unemployment_Rate'].isnull().all():
                    rate_min = float(df['Unemployment_Rate'].min())
                    rate_max = float(df['Unemployment_Rate'].max())
                    filter_rate_min, filter_rate_max = st.slider(
                        "Filter Unemployment Rate Range",
                        min_value=rate_min,
                        max_value=rate_max,
                        value=(rate_min, rate_max)
                    )
                else:
                    filter_rate_min, filter_rate_max = 0, 20
            
            # Apply filters
            filtered_df = df.copy()
            
            if filter_countries:
                filtered_df = filtered_df[filtered_df['Country_Code'].isin(filter_countries)]
            
            filtered_df = filtered_df[
                (filtered_df['Year'] >= filter_year_min) & 
                (filtered_df['Year'] <= filter_year_max)
            ]
            
            if not df['Unemployment_Rate'].isnull().all():
                filtered_df = filtered_df[
                    (filtered_df['Unemployment_Rate'] >= filter_rate_min) & 
                    (filtered_df['Unemployment_Rate'] <= filter_rate_max)
                ]
            
            # Display filtered results
            st.metric("Filtered Data Count", f"{len(filtered_df):,} rows")
            
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Unemployment_Rate": st.column_config.NumberColumn(
                            format="%.2f%%"
                        )
                    }
                )
            else:
                st.info("No data matches the selected filters")
        
        # Summary statistics
        with st.expander("📊 Summary Statistics", expanded=False):
            if not filtered_df.empty:
                # Basic statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Mean", f"{filtered_df['Unemployment_Rate'].mean():.2f}%")
                
                with col2:
                    st.metric("Median", f"{filtered_df['Unemployment_Rate'].median():.2f}%")
                
                with col3:
                    st.metric("Std Dev", f"{filtered_df['Unemployment_Rate'].std():.2f}%")
                
                with col4:
                    st.metric("Range", f"{filtered_df['Unemployment_Rate'].max() - filtered_df['Unemployment_Rate'].min():.2f}%")
                
                # Detailed statistics
                st.markdown("#### Detailed Statistics")
                stats_df = filtered_df['Unemployment_Rate'].describe().round(3)
                st.dataframe(stats_df, use_container_width=True)
        
        # Data export
        with st.expander("💾 Data Export", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export original data
                csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 Download Original Data",
                    data=csv_data,
                    file_name="unemployment_data_original.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Export filtered data
                filtered_csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📊 Download Filtered Data",
                    data=filtered_csv,
                    file_name="unemployment_data_filtered.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col3:
                # Export summary statistics
                if not filtered_df.empty:
                    stats_csv = filtered_df['Unemployment_Rate'].describe().to_csv()
                    st.download_button(
                        label="📈 Download Statistics",
                        data=stats_csv,
                        file_name="unemployment_statistics.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    
    with tab4:
        # Advanced analysis
        st.markdown('<div class="section-header">📊 Advanced Analytical Tools</div>', unsafe_allow_html=True)
        
        # Comparative analysis
        st.markdown("### 🏛️ Comparative Country Analysis")
        
        if len(selected_countries) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Create comparison table
                comparison_data = []
                for country in selected_countries:
                    country_stats, _ = analyze_country(df, country)
                    if country_stats:
                        comparison_data.append({
                            'Country': f"{country_stats['Country Name']} ({country})",
                            'Avg Rate': country_stats['Average Unemployment Rate'],
                            'Current Rate': country_stats['Current Rate'],
                            'Level': country_stats['Unemployment Level'],
                            'Volatility': country_stats['Volatility (Std Dev)'],
                            'Years': country_stats['Years Covered']
                        })
                
                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(
                        comparison_df,
                        use_container_width=True,
                        hide_index=True
                    )
            
            with col2:
                # Ranking analysis
                st.markdown("#### Ranking by Average Rate")
                
                if comparison_data:
                    # Sort by average rate
                    ranking_df = pd.DataFrame(comparison_data)
                    ranking_df['Avg Rate Numeric'] = ranking_df['Avg Rate'].str.replace('%', '').astype(float)
                    ranking_df = ranking_df.sort_values('Avg Rate Numeric')
                    ranking_df['Rank'] = range(1, len(ranking_df) + 1)
                    
                    # Display ranking
                    for _, row in ranking_df.iterrows():
                        st.metric(f"Rank {row['Rank']}: {row['Country']}", row['Avg Rate'])
        
        # Time series decomposition
        st.markdown("### 📅 Time Series Decomposition")
        
        if len(selected_countries) == 1:
            country = selected_countries[0]
            country_data = df[df['Country_Code'] == country].copy()
            country_data = country_data.dropna(subset=['Unemployment_Rate']).sort_values('Year')
            
            if len(country_data) >= 10:
                # Simple decomposition
                country_data['Trend'] = country_data['Unemployment_Rate'].rolling(window=5, center=True).mean()
                country_data['Seasonal'] = country_data['Unemployment_Rate'] - country_data['Trend']
                country_data['Residual'] = country_data['Unemployment_Rate'] - (country_data['Trend'] + country_data['Seasonal'].mean())
                
                # Plot decomposition
                fig, axes = plt.subplots(4, 1, figsize=(12, 10))
                
                # Original
                axes[0].plot(country_data['Year'], country_data['Unemployment_Rate'], 'b-')
                axes[0].set_title(f'{country} - Original Time Series')
                axes[0].set_ylabel('Rate (%)')
                axes[0].grid(True, alpha=0.3)
                
                # Trend
                axes[1].plot(country_data['Year'], country_data['Trend'], 'r-')
                axes[1].set_title('Trend Component')
                axes[1].set_ylabel('Rate (%)')
                axes[1].grid(True, alpha=0.3)
                
                # Seasonal
                axes[2].plot(country_data['Year'], country_data['Seasonal'], 'g-')
                axes[2].set_title('Seasonal Component')
                axes[2].set_ylabel('Deviation')
                axes[2].grid(True, alpha=0.3)
                
                # Residual
                axes[3].plot(country_data['Year'], country_data['Residual'], 'k-')
                axes[3].set_title('Residual Component')
                axes[3].set_xlabel('Year')
                axes[3].set_ylabel('Deviation')
                axes[3].grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
        
        # Predictive analysis
        st.markdown("### 🔮 Simple Forecasting")
        
        if len(selected_countries) == 1:
            country = selected_countries[0]
            country_data = df[df['Country_Code'] == country].copy()
            country_data = country_data.dropna(subset=['Unemployment_Rate']).sort_values('Year')
            
            if len(country_data) >= 10:
                # Simple linear forecast
                from scipy.stats import linregress
                
                years = country_data['Year'].values
                rates = country_data['Unemployment_Rate'].values
                
                # Fit linear model
                slope, intercept, r_value, p_value, std_err = linregress(years, rates)
                
                # Forecast next 5 years
                future_years = np.arange(years[-1] + 1, years[-1] + 6)
                forecast_rates = intercept + slope * future_years
                
                # Create forecast plot
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # Historical data
                ax.plot(years, rates, 'b-', linewidth=2, label='Historical Data')
                ax.scatter(years, rates, color='blue', s=30, alpha=0.6)
                
                # Forecast
                ax.plot(future_years, forecast_rates, 'r--', linewidth=2, label='Forecast')
                ax.scatter(future_years, forecast_rates, color='red', s=30, alpha=0.6)
                
                # Confidence interval
                forecast_std_err = std_err * np.sqrt(1 + 1/len(years) + (future_years - np.mean(years))**2 / np.sum((years - np.mean(years))**2))
                ax.fill_between(future_years, 
                               forecast_rates - 1.96*forecast_std_err, 
                               forecast_rates + 1.96*forecast_std_err, 
                               color='red', alpha=0.2, label='95% Confidence Interval')
                
                ax.set_title(f'{country} - Unemployment Rate Forecast (Next 5 Years)')
                ax.set_xlabel('Year')
                ax.set_ylabel('Unemployment Rate (%)')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
                
                # Display forecast values
                st.markdown("#### Forecast Values")
                forecast_df = pd.DataFrame({
                    'Year': future_years,
                    'Forecasted Rate': [f"{rate:.2f}%" for rate in forecast_rates],
                    'Lower Bound (95%)': [f"{rate - 1.96*err:.2f}%" for rate, err in zip(forecast_rates, forecast_std_err)],
                    'Upper Bound (95%)': [f"{rate + 1.96*err:.2f}%" for rate, err in zip(forecast_rates, forecast_std_err)]
                })
                st.dataframe(forecast_df, use_container_width=True, hide_index=True)
        
        # Statistical tests
        st.markdown("### 📊 Statistical Tests")
        
        if len(selected_countries) >= 2:
            from scipy.stats import ttest_ind, mannwhitneyu, kruskal
            
            # Prepare data
            test_data = []
            for country in selected_countries:
                country_rates = df[df['Country_Code'] == country]['Unemployment_Rate'].dropna()
                if len(country_rates) > 0:
                    test_data.append(country_rates.values)
            
            if len(test_data) >= 2:
                # T-test for first two countries
                if len(test_data[0]) > 1 and len(test_data[1]) > 1:
                    t_stat, t_p = ttest_ind(test_data[0], test_data[1])
                    st.metric("T-test p-value", f"{t_p:.4f}")
                    st.metric("T-test Result", "Significant difference" if t_p < 0.05 else "No significant difference")
                
                # Mann-Whitney U test
                if len(test_data[0]) > 1 and len(test_data[1]) > 1:
                    u_stat, u_p = mannwhitneyu(test_data[0], test_data[1])
                    st.metric("Mann-Whitney U p-value", f"{u_p:.4f}")
                
                # Kruskal-Wallis test for multiple groups
                if len(test_data) > 2:
                    h_stat, h_p = kruskal(*test_data)
                    st.metric("Kruskal-Wallis p-value", f"{h_p:.4f}")
    
    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 12px;">
        <p>📊 <strong>Unemployment Rate Analysis Dashboard</strong> | Data Source: World Bank | Indicator: SL.UEM.TOTL.ZS</p>
        <p>💡 <strong>Unemployment Level Guide:</strong> 
        <span class="very-low">Very Low (<3%)</span> | 
        <span class="low">Low (3-5%)</span> | 
        <span class="medium">Medium (5-8%)</span> | 
        <span class="high">High (8-12%)</span> | 
        <span class="very-high">Very High (>12%)</span>
        </p>
        <p>📅 Data Coverage: 1990-2025 | Countries: Australia, China, France, Finland, Germany, Italy, Japan, UK, USA</p>
        <p>🔧 Built with Streamlit, Pandas, NumPy, Matplotlib, Plotly, and SciPy</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
