# main.py - Economic Analysis Dashboard Hub
"""
ECONOMIC ANALYSIS DASHBOARD HUB
Unified entry page integrating GDP, Inflation, and Unemployment analysis applications
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
from pathlib import Path

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Economic Analysis Dashboard Hub",
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
        padding: 30px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 40px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="white" opacity="0.1"/></svg>');
    }
    
    /* Application card style */
    .app-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 1px solid #eef2f7;
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .app-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
    }
    
    .app-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
    }
    
    .gdp-card::before { background: linear-gradient(to bottom, #4CAF50, #8BC34A); }
    .inflation-card::before { background: linear-gradient(to bottom, #FF5722, #FF9800); }
    .unemployment-card::before { background: linear-gradient(to bottom, #2196F3, #03A9F4); }
    
    /* Icon container */
    .icon-container {
        width: 70px;
        height: 70px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        font-size: 30px;
        color: white;
    }
    
    .gdp-icon { background: linear-gradient(135deg, #4CAF50, #8BC34A); }
    .inflation-icon { background: linear-gradient(135deg, #FF5722, #FF9800); }
    .unemployment-icon { background: linear-gradient(135deg, #2196F3, #03A9F4); }
    
    /* Metric card */
    .metric-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #333;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Footer style */
    .footer {
        text-align: center;
        padding: 30px;
        margin-top: 50px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
        color: #666;
    }
    
    /* Progress bar style */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tab style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 15px 15px 0 0;
        padding: 15px 25px;
        background-color: #f8f9fa;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Data table style */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid #eef2f7;
    }
    
    /* Animation effects */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Navigation guide style */
    .nav-guide {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        border-left: 5px solid #667eea;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .app-card {
            padding: 20px;
        }
        
        .icon-container {
            width: 60px;
            height: 60px;
            font-size: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================
def get_base64_of_bin_file(bin_file):
    """Convert file to base64 for embedding"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background_image():
    """Set background image"""
    bg_image = """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    </style>
    """
    st.markdown(bg_image, unsafe_allow_html=True)

def create_welcome_section():
    """Create welcome section with animated text"""
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="margin: 0; font-size: 3.5rem; font-weight: 800;">📊 Economic Analysis Dashboard Hub</h1>
        <p style="margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.9;">
            Integrated Platform for GDP, Inflation & Unemployment Analysis
        </p>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.8;">
            Comprehensive Economic Data Analysis and Visualization
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_navigation_guide():
    """Create navigation guide section"""
    st.markdown("""
    <div class="nav-guide fade-in">
        <h3 style="color: #667eea; margin-top: 0;">🚀 How to Access Analysis Modules</h3>
        <p><strong>To view detailed analysis for each economic indicator, please use the sidebar on the left:</strong></p>
        <ul style="color: #666; line-height: 1.8;">
            <li><strong>💰 GDP Analysis</strong> - Click "GDP Analysis" in the sidebar to access detailed GDP growth analysis</li>
            <li><strong>📈 Inflation Analysis</strong> - Click "Inflation Analysis" in the sidebar to access detailed inflation analysis</li>
            <li><strong>👥 Unemployment Analysis</strong> - Click "Unemployment Analysis" in the sidebar to access detailed unemployment analysis</li>
        </ul>
        <p style="margin-top: 15px; font-style: italic; color: #FF5722;">
            ⚠️ <strong>Important:</strong> This is the main overview page. For detailed analysis of specific economic indicators, 
            please use the navigation links in the sidebar on the left side of the screen.
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_app_card(title, description, icon, card_class):
    """Create application card without launch button"""
    st.markdown(f"""
    <div class="app-card {card_class} fade-in">
        <div class="icon-container {icon}">
            {icon}
        </div>
        <h2 style="margin-bottom: 15px; color: #333;">{title}</h2>
        <p style="color: #666; line-height: 1.6; margin-bottom: 20px;">{description}</p>
        <p style="color: #888; font-size: 14px; font-style: italic;">
            <strong>Access:</strong> Use the sidebar on the left to navigate to this analysis module
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_quick_stats():
    """Create quick statistics section"""
    st.markdown('<div class="section-header fade-in">📈 Economic Indicators Overview</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Global Avg GDP Growth</div>
            <div class="metric-value" style="color: #4CAF50;">3.2%</div>
            <div style="font-size: 12px; color: #888;">2024 Forecast</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Average Inflation Rate</div>
            <div class="metric-value" style="color: #FF5722;">4.8%</div>
            <div style="font-size: 12px; color: #888;">Global Average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Average Unemployment Rate</div>
            <div class="metric-value" style="color: #2196F3;">5.6%</div>
            <div style="font-size: 12px; color: #888;">Developed Countries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Countries Covered</div>
            <div class="metric-value" style="color: #9C27B0;">189</div>
            <div style="font-size: 12px; color: #888;">World Bank Data</div>
        </div>
        """, unsafe_allow_html=True)

def create_sample_chart():
    """Create sample chart for demonstration"""
    # Sample data for chart
    years = list(range(2010, 2024))
    gdp_growth = [3.1, 3.2, 2.8, 3.0, 3.3, 3.1, 2.9, 3.2, 3.0, 2.8, -3.1, 5.9, 3.1, 3.2]
    inflation = [2.1, 2.3, 2.0, 1.9, 2.2, 2.1, 2.0, 2.3, 2.1, 1.8, 1.2, 4.7, 6.5, 5.8]
    unemployment = [8.3, 8.0, 7.7, 7.4, 7.2, 6.9, 6.7, 6.2, 5.8, 5.3, 6.7, 6.2, 5.8, 5.5]
    
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=years,
        y=gdp_growth,
        mode='lines+markers',
        name='GDP Growth Rate (%)',
        line=dict(color='#4CAF50', width=3),
        marker=dict(size=8, color='#4CAF50')
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=inflation,
        mode='lines+markers',
        name='Inflation Rate (%)',
        line=dict(color='#FF5722', width=3),
        marker=dict(size=8, color='#FF5722')
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=unemployment,
        mode='lines+markers',
        name='Unemployment Rate (%)',
        line=dict(color='#2196F3', width=3),
        marker=dict(size=8, color='#2196F3')
    ))
    
    # Update layout
    fig.update_layout(
        title='📊 Economic Indicators Trend (2010-2023)',
        xaxis_title='Year',
        yaxis_title='Percentage (%)',
        hovermode='x unified',
        height=500,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig

def create_footer():
    """Create footer section"""
    st.markdown("""
    <div class="footer fade-in">
        <h3 style="margin-bottom: 20px;">💡 About This Platform</h3>
        <div style="max-width: 800px; margin: 0 auto; line-height: 1.8;">
            <p style="margin-bottom: 15px;">
                This platform integrates three core economic analysis modules, providing comprehensive macroeconomic data analysis capabilities.
                All data comes from authoritative sources like the World Bank, and analysis tools are built on advanced Python ecosystem libraries.
            </p>
            <div style="display: flex; justify-content: center; gap: 30px; margin: 20px 0;">
                <div>
                    <div style="font-size: 24px;">📈</div>
                    <div style="font-size: 12px; margin-top: 5px;">Data Visualization</div>
                </div>
                <div>
                    <div style="font-size: 24px;">🔍</div>
                    <div style="font-size: 12px; margin-top: 5px;">Deep Analysis</div>
                </div>
                <div>
                    <div style="font-size: 24px;">💾</div>
                    <div style="font-size: 12px; margin-top: 5px;">Data Export</div>
                </div>
                <div>
                    <div style="font-size: 24px;">🌐</div>
                    <div style="font-size: 12px; margin-top: 5px;">Multi-country Comparison</div>
                </div>
            </div>
            <hr style="border: none; height: 1px; background: linear-gradient(to right, transparent, #667eea, transparent); margin: 20px 0;">
            <p style="font-size: 12px; color: #888;">
                © 2024 Economic Analysis System • Version 3.0 • Last Updated: """ + datetime.now().strftime("%Y-%m-%d") + """
                <br>
                Powered by: Streamlit • Plotly • Pandas • NumPy
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN APPLICATION ====================
def main():
    """Main application function"""
    
    # Set background
    set_background_image()
    
    # ==================== MAIN PAGE CONTENT ====================
    
    # Welcome section
    create_welcome_section()
    
    # Navigation guide - IMPORTANT: This tells users to use sidebar
    create_navigation_guide()
    
    # Quick stats
    create_quick_stats()
    
    st.markdown("---")
    
    # Application overview section
    st.markdown('<div class="section-header fade-in">📊 Analysis Modules Overview</div>', unsafe_allow_html=True)
    
    # Create three columns for app cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_app_card(
            title="GDP Analysis Dashboard",
            description="Analyze GDP growth rates, economic scale, development trends across countries. Provides multi-dimensional comparison and trend forecasting.",
            icon="💰",
            card_class="gdp-card"
        )
    
    with col2:
        create_app_card(
            title="Inflation Analysis Dashboard",
            description="Analyze inflation rates, price index changes, monitor inflation trends. Provides inflation alerts and predictive analysis.",
            icon="📈",
            card_class="inflation-card"
        )
    
    with col3:
        create_app_card(
            title="Unemployment Analysis Dashboard",
            description="Analyze unemployment data, labor market conditions. Provides employment trend analysis and policy recommendations.",
            icon="👥",
            card_class="unemployment-card"
        )
    
    st.markdown("---")
    
    # Sample chart section
    st.markdown('<div class="section-header fade-in">📈 Economic Indicators Preview</div>', unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Trend Chart", "🌍 Global Distribution", "📋 Data Overview"])
    
    with tab1:
        fig = create_sample_chart()
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="background: #f8f9fa; padding: 20px; border-radius: 15px; margin-top: 20px;">
            <h4>💡 Interpretation Guide</h4>
            <ul style="color: #666;">
                <li><strong>GDP Growth Rate</strong>: Reflects economic growth speed, 2-3% is considered healthy growth</li>
                <li><strong>Inflation Rate</strong>: Reflects price level changes, around 2% is the ideal target</li>
                <li><strong>Unemployment Rate</strong>: Reflects labor market conditions, 4-6% is normal range</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        # Create a sample world map
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <div style="font-size: 80px; margin-bottom: 20px;">🌍</div>
            <h3>Global Economic Data Distribution Map</h3>
            <p style="color: #666;">Navigate to specific analysis sections in the sidebar to view detailed geographical distribution data</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample country data
        countries = ['USA', 'China', 'Japan', 'Germany', 'UK', 'France', 'India', 'Brazil', 'Russia', 'Australia']
        gdp_values = [25462, 17963, 4912, 4223, 3186, 2937, 3471, 1609, 1836, 1693]
        
        data = pd.DataFrame({
            'Country': countries,
            'GDP (Billion USD)': gdp_values
        })
        
        # Create bar chart
        fig_bar = px.bar(
            data,
            x='Country',
            y='GDP (Billion USD)',
            title='Major Countries GDP Comparison',
            color='GDP (Billion USD)',
            color_continuous_scale='Viridis'
        )
        
        fig_bar.update_layout(
            height=400,
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab3:
        # Create sample data table
        st.markdown("### 📋 Sample Data Overview")
        
        sample_data = pd.DataFrame({
            'Year': list(range(2020, 2024)),
            'Global Avg GDP Growth (%)': [2.9, 6.0, 3.1, 3.2],
            'Global Avg Inflation Rate (%)': [3.2, 4.7, 8.7, 6.5],
            'Global Avg Unemployment Rate (%)': [6.5, 6.2, 5.8, 5.5],
            'Countries Covered': [189, 189, 189, 189]
        })
        
        st.dataframe(
            sample_data,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%); padding: 20px; border-radius: 15px; margin-top: 20px;">
            <h4>📊 Data Sources</h4>
            <ul style="color: #666;">
                <li><strong>World Bank Database</strong>: GDP, unemployment and other macroeconomic data</li>
                <li><strong>International Monetary Fund (IMF)</strong>: Economic growth forecasts</li>
                <li><strong>National Statistical Agencies</strong>: Official economic statistics</li>
                <li><strong>Organization for Economic Cooperation and Development (OECD)</strong>: Developed countries economic data</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    create_footer()
    
    # ==================== SIDEBAR CONTENT ====================
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-bottom: 20px;">
            <div style="font-size: 40px; margin-bottom: 10px;">📊</div>
            <h3 style="margin: 0;">Economic Analysis Hub</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">v3.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧭 Navigation")
        
        # Navigation instructions
        st.info("""
        **Use the links below to access detailed analysis:**
        
        1. **💰 GDP Analysis** - Detailed GDP growth analysis
        2. **📈 Inflation Analysis** - Detailed inflation analysis  
        3. **👥 Unemployment Analysis** - Detailed unemployment analysis
        """)
        
        st.markdown("---")
        
        st.markdown("### 🔧 Quick Settings")
        
        # Theme selection
        theme = st.selectbox(
            "Select Theme",
            ["Default Theme", "Dark Mode", "Professional Mode", "Minimal Mode"]
        )
        
        # Language selection
        language = st.selectbox(
            "Select Language",
            ["English", "Chinese", "Bilingual Mode"]
        )
        
        # Data source selection
        data_source = st.multiselect(
            "Data Sources",
            ["World Bank", "International Monetary Fund", "National Statistics", "OECD"],
            default=["World Bank", "International Monetary Fund"]
        )
        
        st.markdown("---")
        
        st.markdown("### 📈 Live Indicators")
        
        # Progress bars for indicators
        st.markdown("**GDP Growth Forecast**")
        st.progress(0.65)
        st.caption("2024 Forecast: +3.2%")
        
        st.markdown("**Inflation Rate**")
        st.progress(0.48)
        st.caption("Current: 4.8%")
        
        st.markdown("**Unemployment Rate**")
        st.progress(0.56)
        st.caption("Developed Countries Avg: 5.6%")
        
        st.markdown("---")
        
        st.markdown("### 🟢 System Status")
        
        status_items = [
            ("GDP Analysis Module", "🟢 Available"),
            ("Inflation Analysis Module", "🟢 Available"),
            ("Unemployment Analysis Module", "🟢 Available"),
            ("Data Update", "🟡 Within 24h"),
            ("System Load", "🟢 Normal")
        ]
        
        for item, status in status_items:
            st.markdown(f"**{item}**: {status}")
        
        st.markdown("---")
        
        # Last updated
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"**Last Updated**: {current_time}")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()