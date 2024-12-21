import streamlit as st
import pandas as pd
import time
import requests

# Set page configuration
st.set_page_config(
    page_title="IoT Energy Consumption Dashboard",
    page_icon="⚡",
    layout="wide",
)

# Title and Description
st.title("Real-Time IoT Energy Consumption Dashboard ⚡")
st.markdown("Monitor the energy usage trends for Table Fan, PC, and TV in real-time.")

# Load data
git_url = "https://github.com/n1sarga/Streamlit_App/blob/main/Appliance_Data.csv"
response = requests.get(git_url)
data = pd.read_csv(git_url)
data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'], dayfirst=True)

# Create placeholders for real-time updates
placeholder = st.empty()

# Sidebar filters
st.sidebar.header("Filters")
device_selection = st.sidebar.multiselect(
    "Select devices to display",
    options=["Table Fan", "PC", "TV"],
    default=["Table Fan", "PC", "TV"]
)
display_interval = st.sidebar.slider("Update Interval (seconds)", min_value=1, max_value=5, value=2)

# Define peak and non-peak hours
def categorize_hours(hour):
    return "Peak" if 8 <= hour < 18 else "Non-Peak"

data['Hour Category'] = data['Datetime'].dt.hour.apply(categorize_hours)

# Simulate real-time data streaming
for i in range(len(data)):
    current_data = data.iloc[:i+1]
    latest_reading = current_data.iloc[-1]

    with placeholder.container():
        st.subheader(f"Latest Readings at {latest_reading['Time']}, {latest_reading['Date']}")
        
        # Latest readings summary
        if 'Table Fan' in current_data.columns and 'PC' in current_data.columns and 'TV' in current_data.columns:
            st.write(latest_reading[['Table Fan', 'PC', 'TV']])
        else:
            st.warning("No valid data for selected devices.")

        col1, col2, col3 = st.columns(3)

        # Power Consumption Line Chart
        with col1:
            st.markdown("### Power Usage Trends (kWh)")
            st.line_chart(current_data[device_selection])

        # Current Usage Line Chart
        with col2:
            st.markdown("### Current Usage Trends (Amps)")
            st.line_chart(current_data[[f"{device} Current" for device in device_selection]])

        # Voltage Bar Chart
        with col3:
            st.markdown("### Voltage Levels (V)")
            st.bar_chart(current_data['Voltage'])

        # Peak vs Non-Peak Analysis
        peak_data = current_data[current_data['Hour Category'] == 'Peak']
        non_peak_data = current_data[current_data['Hour Category'] == 'Non-Peak']

        col4, col5 = st.columns(2)

        # Bar chart for power usage
        with col4:
            st.markdown("### Power Usage: Peak vs Non-Peak")
            power_usage = {
                "Peak": peak_data[device_selection].sum().sum(),
                "Non-Peak": non_peak_data[device_selection].sum().sum(),
            }
            st.bar_chart(pd.DataFrame.from_dict(power_usage, orient='index', columns=['Power Usage (kWh)']))

        # Bar chart for current usage
        with col5:
            st.markdown("### Current Usage: Peak vs Non-Peak")
            current_usage = {
                "Peak": peak_data[[f"{device} Current" for device in device_selection]].sum().sum(),
                "Non-Peak": non_peak_data[[f"{device} Current" for device in device_selection]].sum().sum(),
            }
            st.bar_chart(pd.DataFrame.from_dict(current_usage, orient='index', columns=['Current Usage (Amps)']))

        # Daily Cost Bar Chart
        daily_costs = current_data.groupby('Date')[['Fan Cost', 'PC Cost', 'TV Cost']].sum()
        st.markdown("### Daily Cost Breakdown")
        st.bar_chart(daily_costs)

    time.sleep(display_interval)  # Dynamic pause for live updates