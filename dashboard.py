import streamlit as st
import pandas as pd
import time

# Set page configuration
st.set_page_config(
    page_title="IoT Energy Consumption Dashboard",
    page_icon="⚡",
    layout="wide",
)

# Load data
data = pd.read_csv("Appliance_Data.csv")

# Convert 'Date' and 'Time' columns to datetime format
data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])

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
    return "Peak" if hour in range(8, 18) else "Non-Peak"

data['Hour Category'] = data['Datetime'].dt.hour.apply(categorize_hours)

# Simulate real-time data streaming
while True:
    current_data = data.iloc[:len(data)-1]
    
    # Check if current_data is empty
    if current_data.empty:
        st.warning("No data available to display.")
        break

    latest_reading = current_data.iloc[-1]

    with placeholder.container():
        st.subheader(f"Latest Readings at {latest_reading['Time']}, {latest_reading['Date']}")

        # Latest readings summary
        st.write(latest_reading[['Table Fan', 'PC', 'TV', 'Table Fan Current', 'PC Current', 'TV Current', 'Voltage']])
        
        col1, col2, col3 = st.columns(3)

        # Power Consumption Line Chart
        with col1:
            st.markdown("### Power Usage Trends (kWh)")
            selected_columns = [col for col in device_selection if col in current_data.columns]
            if selected_columns:
                st.line_chart(current_data[selected_columns].tail(50))
            else:
                st.warning("No valid data for selected devices.")

        # Current Usage Line Chart
        with col2:
            st.markdown("### Current Usage Trends (Amps)")
            current_columns = [f"{device} Current" for device in device_selection if f"{device} Current" in current_data.columns]
            if current_columns:
                st.line_chart(current_data[current_columns].tail(50))
            else:
                st.warning("No current data for selected devices.")

        # Voltage Bar Chart
        with col3:
            st.markdown("### Voltage Levels (V)")
            if not current_data['Voltage'].isnull().all():
                st.bar_chart(current_data['Voltage'].tail(50))
            else:
                st.warning("No voltage data available.")

        # Peak vs Non-Peak Analysis
        peak_data = current_data[current_data['Hour Category'] == 'Peak']
        non_peak_data = current_data[current_data['Hour Category'] == 'Non-Peak']

        col4, col5 = st.columns(2)

        # Bar chart for power usage
        with col4:
            st.markdown("### Power Usage: Peak vs Non-Peak")
            if not peak_data.empty or not non_peak_data.empty:
                power_usage = {
                    "Peak": peak_data[device_selection].sum().sum(),
                    "Non-Peak": non_peak_data[device_selection].sum().sum(),
                }
                st.bar_chart(pd.DataFrame.from_dict(power_usage, orient='index', columns=['Power Usage (kWh)']))
            else:
                st.warning("No data for peak/non-peak power usage.")

        # Bar chart for current usage
        with col5:
            st.markdown("### Current Usage: Peak vs Non-Peak")
            if not peak_data.empty or not non_peak_data.empty:
                current_usage = {
                    "Peak": peak_data[[f"{device} Current" for device in device_selection if f"{device} Current" in peak_data.columns]].sum().sum(),
                    "Non-Peak": non_peak_data[[f"{device} Current" for device in device_selection if f"{device} Current" in non_peak_data.columns]].sum().sum(),
                }
                st.bar_chart(pd.DataFrame.from_dict(current_usage, orient='index', columns=['Current Usage (Amps)']))
            else:
                st.warning("No data for peak/non-peak current usage.")

        # Daily Cost Bar Chart
        daily_costs = current_data.groupby('Date')[['Fan Cost', 'PC Cost', 'TV Cost']].sum()
        if not daily_costs.empty:
            st.markdown("### Daily Cost Breakdown")
            st.bar_chart(daily_costs)
        else:
            st.warning("No cost data available.")

    time.sleep(display_interval)