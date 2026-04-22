import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="GDP Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS STYLES ====================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #4e73df;
        margin-bottom: 15px;
    }
    
    .upload-area {
        border: 2px dashed #4e73df;
        border-radius: 10px;
        padding: 40px;
        text-align: center;
        background-color: #f8f9fa;
        margin-bottom: 20px;
    }
    
    /* Sidebar styling */
    .sidebar-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    
    .sidebar-section {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
        border-left: 4px solid #4e73df;
    }
    
    .country-card {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid #4e73df;
        transition: all 0.3s ease;
    }
    
    .country-card:hover {
        background-color: #e9ecef;
        transform: translateX(5px);
    }
    
    .selected-country {
        background-color: #e3f2fd;
        border-left: 3px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# ==================== COLOR CONFIGURATION ====================
COLOR_PALETTE = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9A8B'
]

# ==================== UTILITY FUNCTIONS ====================
def create_sample_data() -> pd.DataFrame:
    """Create sample data"""
    st.info("📊 Using sample data for analysis")
    
    # Create realistic sample data
    years = list(range(1976, 2026))
    countries = {
        'CHN': 'China',
        'USA': 'United States',
        'JPN': 'Japan',
        'DEU': 'Germany',
        'GBR': 'United Kingdom',
        'FRA': 'France',
        'ITA': 'Italy',
        'AUS': 'Australia',
        'FIN': 'Finland',
        'IND': 'India',
        'BRA': 'Brazil',
        'RUS': 'Russia',
        'CAN': 'Canada',
        'KOR': 'South Korea',
        'MEX': 'Mexico'
    }
    
    # Generate data
    data = []
    for country_code, country_name in countries.items():
        # Generate reasonable GDP growth trends for each country
        base_gdp = {
            'CHN': 3.0e11, 'USA': 6.0e12, 'JPN': 1.8e12, 
            'DEU': 1.6e12, 'GBR': 1.2e12, 'FRA': 1.1e12,
            'ITA': 1.0e12, 'AUS': 4.0e11, 'FIN': 1.0e11,
            'IND': 2.0e11, 'BRA': 5.0e11, 'RUS': 1.5e12,
            'CAN': 8.0e11, 'KOR': 6.0e11, 'MEX': 4.0e11
        }.get(country_code, 1e11)
        
        growth_rate = {
            'CHN': 0.08, 'USA': 0.03, 'JPN': 0.02,
            'DEU': 0.025, 'GBR': 0.025, 'FRA': 0.02,
            'ITA': 0.015, 'AUS': 0.03, 'FIN': 0.02,
            'IND': 0.06, 'BRA': 0.025, 'RUS': 0.02,
            'CAN': 0.028, 'KOR': 0.04, 'MEX': 0.025
        }.get(country_code, 0.02)
        
        for year in years:
            # Calculate GDP value (with some random fluctuation)
            years_since_1976 = year - 1976
            gdp = base_gdp * (1 + growth_rate) ** years_since_1976
            gdp *= np.random.uniform(0.95, 1.05)  # Add 5% random fluctuation
            
            data.append({
                'Indicator Name': 'GDP (constant 2015 US$)',
                'Indicator Code': 'NY.GDP.MKTP.KD',
                'Country Name': country_name,
                'Country Code': country_code,
                'Year': year,
                'GDP Value': gdp
            })
    
    return pd.DataFrame(data)

@st.cache_data
def load_gdp_data(uploaded_file=None) -> pd.DataFrame:
    """Load GDP data"""
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
            
            # Verify required columns
            required_columns = ['Indicator Name', 'Indicator Code', 'Country Name', 'Country Code', 'Year', 'GDP Value']
            missing_cols = [col for col in required_columns if col not in df.columns]
            
            if missing_cols:
                st.warning(f"File is missing the following columns: {missing_cols}, using sample data")
                return create_sample_data()
            
            return df
            
        except Exception as e:
            st.error(f"File reading failed: {str(e)}")
            return create_sample_data()
    else:
        # If no file uploaded, use sample data
        return create_sample_data()

def calculate_growth_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate GDP growth rate"""
    df = df.copy()
    df = df.sort_values(['Country Code', 'Year'])
    
    # Calculate annual growth rate
    df['GDP Growth Rate'] = df.groupby('Country Code')['GDP Value'].pct_change() * 100
    
    # Calculate logarithmic growth rate
    df['Log Growth Rate'] = np.log(df['GDP Value'] / df.groupby('Country Code')['GDP Value'].shift(1)) * 100
    
    # Calculate 5-year moving average growth rate
    df['5-Year Moving Average Growth'] = df.groupby('Country Code')['GDP Growth Rate'].rolling(window=5, min_periods=1).mean().values
    
    return df

# ==================== VISUALIZATION FUNCTIONS ====================
def create_gdp_trend_chart(df: pd.DataFrame, selected_countries: list, year_range: tuple) -> go.Figure:
    """Create GDP trend chart"""
    fig = go.Figure()
    
    filtered_df = df[
        (df['Country Code'].isin(selected_countries)) & 
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1])
    ]
    
    if filtered_df.empty:
        return fig
    
    for i, country in enumerate(selected_countries):
        country_data = filtered_df[filtered_df['Country Code'] == country]
        
        if not country_data.empty:
            fig.add_trace(go.Scatter(
                x=country_data['Year'],
                y=country_data['GDP Value'],
                mode='lines+markers',
                name=country,
                line=dict(width=3, color=COLOR_PALETTE[i % len(COLOR_PALETTE)]),
                marker=dict(size=8),
                hovertemplate=(
                    f"<b>{country}</b><br>"
                    "Year: %{x}<br>"
                    "GDP: %{y:,.2f}<br>"
                    "<extra></extra>"
                )
            ))
    
    fig.update_layout(
        title=f"GDP Trend Comparison by Country ({year_range[0]}-{year_range[1]})",
        xaxis_title="Year",
        yaxis_title="GDP (constant 2015 US$)",
        hovermode="x unified",
        height=500,
        template="plotly_white",
        yaxis=dict(
            tickformat=",.0f"
        )
    )
    
    return fig

def create_growth_rate_chart(df: pd.DataFrame, selected_countries: list, year_range: tuple) -> go.Figure:
    """Create growth rate chart"""
    fig = go.Figure()
    
    filtered_df = df[
        (df['Country Code'].isin(selected_countries)) & 
        (df['Year'] >= year_range[0]) & 
        (df['Year'] <= year_range[1])
    ]
    
    if filtered_df.empty:
        return fig
    
    for i, country in enumerate(selected_countries):
        country_data = filtered_df[filtered_df['Country Code'] == country]
        
        if not country_data.empty:
            fig.add_trace(go.Scatter(
                x=country_data['Year'],
                y=country_data['GDP Growth Rate'],
                mode='lines+markers',
                name=country,
                line=dict(width=2, color=COLOR_PALETTE[i % len(COLOR_PALETTE)]),
                marker=dict(size=6),
                hovertemplate=(
                    f"<b>{country}</b><br>"
                    "Year: %{x}<br>"
                    "Growth Rate: %{y:.2f}%<br>"
                    "<extra></extra>"
                )
            ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title=f"GDP Growth Rate Comparison by Country ({year_range[0]}-{year_range[1]})",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        hovermode="x unified",
        height=500,
        template="plotly_white"
    )
    
    return fig

def create_comparison_bar_chart(df: pd.DataFrame, year: int) -> go.Figure:
    """Create annual comparison bar chart"""
    year_data = df[df['Year'] == year].copy()
    
    if year_data.empty:
        return go.Figure()
    
    # Sort by GDP value
    year_data = year_data.sort_values('GDP Value', ascending=False)
    
    fig = go.Figure(data=[
        go.Bar(
            x=year_data['Country Name'],
            y=year_data['GDP Value'],
            marker_color=COLOR_PALETTE,
            text=year_data['GDP Value'].apply(lambda x: f"{x:,.0f}"),
            textposition='outside',
            hovertemplate=(
                "<b>%{x}</b><br>"
                "GDP: %{y:,.0f}<br>"
                "<extra></extra>"
            )
        )
    ])
    
    fig.update_layout(
        title=f"GDP Comparison by Country ({year})",
        xaxis_title="Country",
        yaxis_title="GDP (constant 2015 US$)",
        height=400,
        template="plotly_white",
        yaxis=dict(
            tickformat=",.0f"
        )
    )
    
    return fig

# ==================== SIDEBAR FUNCTIONS ====================
def create_sidebar(df: pd.DataFrame):
    """Create sidebar with all controls"""
    
    # Sidebar header
    st.sidebar.markdown("""
    <div class="sidebar-header">
        <h2 style="margin: 0;">⚙️ Dashboard Controls</h2>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Configure your analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data source section
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("📁 Data Source")
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV File",
        type=['csv'],
        help="Upload your GDP data CSV file"
    )
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Country selection section
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🌍 Country Selection")
    
    # Get available countries
    available_countries = sorted(df['Country Code'].unique())
    country_names = df[['Country Code', 'Country Name']].drop_duplicates()
    country_name_dict = dict(zip(country_names['Country Code'], country_names['Country Name']))
    
    # Display available countries with checkboxes in a nice layout
    st.sidebar.markdown("**Available Countries:**")
    
    # Create two columns for checkboxes
    col1, col2 = st.sidebar.columns(2)
    
    selected_countries = []
    for idx, country_code in enumerate(available_countries):
        col = col1 if idx % 2 == 0 else col2
        with col:
            country_display = f"{country_code}"
            if st.checkbox(country_display, key=f"country_{country_code}", 
                          help=country_name_dict.get(country_code, "")):
                selected_countries.append(country_code)
    
    # If no countries selected, use default
    if not selected_countries:
        default_countries = ['CHN', 'USA', 'JPN']
        selected_countries = [c for c in default_countries if c in available_countries]
        if selected_countries:
            st.sidebar.info(f"ℹ️ Using default countries: {', '.join(selected_countries)}")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis parameters section
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("📊 Analysis Parameters")
    
    # Year range selection
    min_year = int(df['Year'].min())
    max_year = int(df['Year'].max())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        help="Select the year range for analysis"
    )
    
    # Chart type selection
    chart_type = st.sidebar.radio(
        "Chart Type",
        ["GDP Trend Chart", "Growth Rate Chart", "Annual Comparison Chart"],
        help="Select the type of chart to display"
    )
    
    # Additional options based on chart type
    if chart_type == "Annual Comparison Chart":
        year = st.sidebar.selectbox(
            "Comparison Year",
            options=sorted(df['Year'].unique(), reverse=True),
            index=0,
            help="Select year for comparison"
        )
    else:
        year = None
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected countries
    if selected_countries:
        st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.sidebar.subheader("✅ Selected Countries")
        
        for country in selected_countries:
            country_name = country_name_dict.get(country, country)
            st.sidebar.markdown(f"""
            <div class="country-card selected-country">
                <strong>{country}</strong> - {country_name}
            </div>
            """, unsafe_allow_html=True)
        
        st.sidebar.markdown(f"**Total:** {len(selected_countries)} countries selected")
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions section
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Reset Selection", use_container_width=True):
        st.rerun()
    
    if st.sidebar.button("📊 Show All Countries", use_container_width=True):
        selected_countries = available_countries
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Information section
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("ℹ️ Information")
    
    st.sidebar.markdown(f"""
    **Data Summary:**
    - Countries: {len(available_countries)}
    - Years: {min_year} - {max_year}
    - Data Points: {len(df):,}
    """)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_file, selected_countries, year_range, chart_type, year

# ==================== MAIN APPLICATION ====================
def main():
    """Main application function"""
    
    # Application title
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0;">🌍 World Bank GDP Data Analysis Dashboard</h1>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">Interactive analysis of GDP data across countries</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initial data loading (sample data for sidebar)
    df = load_gdp_data(None)
    
    # Create sidebar and get parameters
    uploaded_file, selected_countries, year_range, chart_type, year = create_sidebar(df)
    
    # Reload data if file uploaded
    if uploaded_file is not None:
        with st.spinner("Loading uploaded data..."):
            df = load_gdp_data(uploaded_file)
    
    # Display data information
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Number of Countries", df['Country Code'].nunique())
    with col2:
        st.metric("Year Range", f"{df['Year'].min()} - {df['Year'].max()}")
    with col3:
        st.metric("Total Data Points", f"{len(df):,}")
    with col4:
        avg_gdp = df['GDP Value'].mean()
        st.metric("Average GDP", f"{avg_gdp:,.0f}")
    
    # Data preview
    with st.expander("📋 Data Preview", expanded=True):
        st.dataframe(df.head(10))
        st.caption(f"Data shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Calculate growth rates
    df_processed = calculate_growth_rate(df)
    
    # Display analysis section
    if selected_countries:
        st.subheader("📈 GDP Data Analysis")
        
        # Display selected countries info
        st.markdown(f"**Analyzing {len(selected_countries)} countries:** {', '.join(selected_countries)}")
        
        # Display charts based on selection
        if chart_type == "GDP Trend Chart":
            fig = create_gdp_trend_chart(df_processed, selected_countries, year_range)
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Growth Rate Chart":
            fig = create_growth_rate_chart(df_processed, selected_countries, year_range)
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_type == "Annual Comparison Chart":
            fig = create_comparison_bar_chart(df_processed, year)
            st.plotly_chart(fig, use_container_width=True)
        
        # Display statistical summary
        st.subheader("📊 Statistical Summary")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Country Details", "📊 Comparison Table", "📋 Raw Data"])
        
        with tab1:
            # Country-by-country details
            for country in selected_countries:
                country_data = df_processed[df_processed['Country Code'] == country]
                if not country_data.empty:
                    with st.expander(f"{country} - {country_data['Country Name'].iloc[0]}", expanded=False):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Average GDP", f"{country_data['GDP Value'].mean():,.0f}")
                        with col2:
                            growth_rate = country_data['GDP Growth Rate'].mean()
                            st.metric("Avg Growth Rate", f"{growth_rate:.2f}%")
                        with col3:
                            st.metric("Maximum GDP", f"{country_data['GDP Value'].max():,.0f}")
                        with col4:
                            st.metric("Minimum GDP", f"{country_data['GDP Value'].min():,.0f}")
                        
                        # Detailed statistics
                        st.markdown("**Detailed Statistics:**")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Data Points", len(country_data))
                        with col2:
                            st.metric("Start Year", int(country_data['Year'].min()))
                        with col3:
                            st.metric("End Year", int(country_data['Year'].max()))
                        with col4:
                            growth_multiple = country_data['GDP Value'].iloc[-1] / country_data['GDP Value'].iloc[0]
                            st.metric("Growth Multiple", f"{growth_multiple:.2f}x")
        
        with tab2:
            # Comparison table
            comparison_data = []
            for country in selected_countries:
                country_data = df_processed[df_processed['Country Code'] == country]
                if not country_data.empty:
                    comparison_data.append({
                        'Country Code': country,
                        'Country Name': country_data['Country Name'].iloc[0],
                        'Avg GDP': country_data['GDP Value'].mean(),
                        'Avg Growth Rate': country_data['GDP Growth Rate'].mean(),
                        'Max GDP': country_data['GDP Value'].max(),
                        'Min GDP': country_data['GDP Value'].min(),
                        'Start Year': int(country_data['Year'].min()),
                        'End Year': int(country_data['Year'].max()),
                        'Data Points': len(country_data)
                    })
            
            if comparison_data:
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(
                    comparison_df.style.format({
                        'Avg GDP': '{:,.0f}',
                        'Avg Growth Rate': '{:.2f}%',
                        'Max GDP': '{:,.0f}',
                        'Min GDP': '{:,.0f}'
                    }),
                    use_container_width=True
                )
        
        with tab3:
            # Raw data for selected countries
            filtered_data = df_processed[df_processed['Country Code'].isin(selected_countries)]
            st.dataframe(filtered_data, use_container_width=True)
    
    else:
        st.warning("⚠️ Please select at least one country from the sidebar to begin analysis.")
        st.info("💡 Tip: Check the boxes in the '🌍 Country Selection' section of the sidebar to select countries.")
    
    # Data download section
    st.subheader("💾 Data Download")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download original data
        csv_original = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Original Data (CSV)",
            data=csv_original,
            file_name="gdp_data_original.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Download processed data
        csv_processed = df_processed.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📊 Processed Data (CSV)",
            data=csv_processed,
            file_name="gdp_data_processed.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        # Download filtered data (if countries selected)
        if selected_countries:
            filtered_data = df_processed[df_processed['Country Code'].isin(selected_countries)]
            csv_filtered = filtered_data.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="🎯 Filtered Data (CSV)",
                data=csv_filtered,
                file_name="gdp_data_filtered.csv",
                mime="text/csv",
                use_container_width=True
        )
        else:
            st.info("Select countries to enable filtered download")
    
    # Usage instructions
    with st.expander("📖 Usage Instructions", expanded=False):
        st.markdown("""
        ### How to Use This Dashboard
        
        1. **Upload Data** (optional)
           - Click "Browse files" in the sidebar to upload your CSV data
           - If no file is uploaded, sample data will be used
        
        2. **Select Countries**
           - Go to "🌍 Country Selection" in the sidebar
           - Check the boxes for countries you want to analyze
           - You can select 1 or more countries
        
        3. **Configure Analysis**
           - Adjust the year range slider
           - Choose a chart type (GDP Trend, Growth Rate, or Annual Comparison)
           - For Annual Comparison, select a specific year
        
        4. **View Results**
           - Charts will update automatically
           - Check the statistical summary tabs for detailed information
           - Download data using the buttons at the bottom
        
        ### Data Format Requirements
        CSV file should contain the following columns:
        
        | Column Name | Description | Example |
        |-------------|-------------|---------|
        | Indicator Name | Economic indicator name | GDP (constant 2015 US$) |
        | Indicator Code | Indicator code | NY.GDP.MKTP.KD |
        | Country Name | Country name | China |
        | Country Code | Country code | CHN |
        | Year | Year | 2020 |
        | GDP Value | GDP value | 1470000000000 |
        
        ### Features
        - **Interactive Charts**: Hover over charts for detailed information
        - **Multiple Views**: Tabs for detailed statistics, comparison tables, and raw data
        - **Data Export**: Download original, processed, or filtered data
        - **Responsive Design**: Works on desktop and mobile devices
        
        ### Sample Data
        The sample data includes 15 countries with realistic GDP trends from 1976 to 2025.
        """)

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
