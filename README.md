📊 Economic Analysis Dashboard Hub

An interactive Streamlit application for analyzing global economic indicators including GDP, Unemployment, and Inflation data.
🎯 Project Overview

This interactive data analysis tool provides comprehensive visualization and analysis of three key economic indicators across multiple countries over the past five decades. The application allows users to explore, compare, and understand economic trends through intuitive visualizations and statistical analysis.
👥 Target Audience

Business & Finance Students: Understanding macroeconomic trends and data analysis
Economics Researchers: Quick data exploration and visualization
Data Analysts: Exporting processed data for further analysis
General Public: Learning about global economic indicators
📊 Features
🏛️ GDP Analysis

Time series visualization of GDP trends
Country comparison and ranking
Cumulative growth analysis
Interactive charts with Plotly
📉 Unemployment Analysis

Historical unemployment rate tracking
Multi-country comparison
Box plot distribution analysis
Correlation analysis between countries
💹 Inflation Analysis

Inflation rate trends visualization
Year-over-year comparison
Statistical summaries
Interactive data tables
📁 Project Structure

plaintext
├── MAIN.py              # Main entry point (Dashboard Hub)
├── pages/               # Multi-page Streamlit application
│   ├── 01_GDP.py        # GDP Analysis Dashboard
│   ├── 02_UNEMPLOYMENT.py  # Unemployment Analysis Dashboard
│   └── 03_INFLATION.py  # Inflation Analysis Dashboard
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
🛠️ Installation & Setup
Prerequisites

Python 3.8 or higher
Git (for cloning)
Web browser (Chrome, Firefox, Edge, or Safari)
Local Setup

Clone this repository:

bash
git clone https://github.com/beverly/acc102-track4-data-tool.git
cd acc102-track4-data-tool

Create a virtual environment (recommended):

bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

Install dependencies:

bash
pip install -r requirements.txt

Run the application:

bash
streamlit run MAIN.py

Access the app:
Open your web browser and go to http://localhost:8501
📊 Data Source

Source: World Bank Open Data
Access Date: April 2026
Coverage: 9 countries (Australia, China, Finland, France, Germany, Italy, Japan, United Kingdom, United States)
Time Period: 1976-2025
Indicators:
GDP (constant 2015 US$)
Unemployment, total (% of total labor force)
Inflation, consumer prices (annual %)
🚀 Live Demo

Access the live application here: https://acc102-track4-data-tool.streamlit.app
🎬 Demo Video

A 1-3 minute demo video explaining the application features and functionality.

Video link to be added
💻 Technologies Used

Technology	Purpose
Streamlit	Web application framework
Pandas	Data manipulation and analysis
NumPy	Numerical computing
Plotly	Interactive visualizations
Matplotlib	Static chart generation
Seaborn	Statistical data visualization
SciPy	Statistical analysis
📝 Reflection Report

A detailed reflection report (500-800 words) documenting the analytical process, insights gained, and personal learning outcomes is available in the submission documents.
👤 Author

Name: Xiaoyu.Ren
Student ID: 2473529
Module: ACC102 - Python Data Product
Institution: Xi'an Jiaotong-Liverpool University
📚 Resources

Streamlit Documentation
Pandas Documentation
Plotly Python Documentation
World Bank Open Data
⚠️ Limitations & Future Improvements
Current Limitations

Static dataset (data accessed in April 2026)
Limited to 9 countries due to data availability
No real-time data updates
Potential Improvements

Add more countries and regions
Implement real-time data fetching from APIs
Add predictive analytics and forecasting
Include more economic indicators
Add data export functionality in multiple formats
📄 License

This project was created for educational purposes as part of the ACC102 module at Xi'an Jiaotong-Liverpool University.

Last Updated: April 2026
