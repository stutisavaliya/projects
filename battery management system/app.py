import streamlit as st
import random
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Battery Cell Management Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .cell-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'cell_types' not in st.session_state:
    st.session_state.cell_types = []

# Main title
st.markdown('<h1 class="main-header">🔋 Battery Cell Management Dashboard</h1>', unsafe_allow_html=True)

# Sidebar for cell configuration
with st.sidebar:
    st.header("⚙️ Cell Configuration")

    num_cells = st.selectbox(
        "Number of cells:",
        options=range(1, 17),
        help="Select the number of battery cells to manage"
    )

    st.subheader("Cell Types")

    cell_types = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell #{i+1} type:",
            options=["LFP", "NMC"],
            key=f"cell_type_{i}",
            help=f"Select the chemistry type for cell #{i+1}"
        )
        cell_types.append(cell_type.lower())

    if st.button("🔄 Generate Cell Data", use_container_width=True):
        st.session_state.cell_types = cell_types
        cells_data = {}

        for idx, cell_type in enumerate(cell_types, start=1):
            cell_key = f"cell_{idx}_{cell_type}"

            voltage = 3.2 if cell_type == "lfp" else 3.6
            min_voltage = 2.8 if cell_type == "lfp" else 3.2
            max_voltage = 3.6 if cell_type == "lfp" else 4.0
            current = 0.0
            temp = round(random.uniform(25, 40), 1)
            capacity = round(voltage * current, 2)

            cells_data[cell_key] = {
                "voltage": voltage,
                "current": current,
                "temp": temp,
                "capacity": capacity,
                "min_voltage": min_voltage,
                "max_voltage": max_voltage,
                "type": cell_type.upper()
            }

        st.session_state.cells_data = cells_data
        st.success(f"Generated data for {num_cells} cells!")

# Main content area
if st.session_state.cells_data:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Cell Overview", "⚡ Current Settings", "📈 Analytics", "📋 Data Table"])

    # === Tab 1: Overview ===
    with tab1:
        st.subheader("Cell Status Overview")
        cols = st.columns(min(4, len(st.session_state.cells_data)))
        for idx, (cell_key, cell_data) in enumerate(st.session_state.cells_data.items()):
            with cols[idx % len(cols)]:
                voltage_ratio = (cell_data["voltage"] - cell_data["min_voltage"]) / (cell_data["max_voltage"] - cell_data["min_voltage"])
                if voltage_ratio > 0.8:
                    status_color, status = "🟢", "Good"
                elif voltage_ratio > 0.5:
                    status_color, status = "🟡", "OK"
                else:
                    status_color, status = "🔴", "Low"

                st.markdown(f"""
                <div class="cell-card">
                    <h4>{status_color} {cell_key.replace('_', ' ').title()}</h4>
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Voltage:</strong> {cell_data['voltage']}V</p>
                    <p><strong>Current:</strong> {cell_data['current']}A</p>
                    <p><strong>Temperature:</strong> {cell_data['temp']}°C</p>
                    <p><strong>Capacity:</strong> {cell_data['capacity']}Ah</p>
                </div>
                """, unsafe_allow_html=True)

    # === Tab 2: Current Settings ===
    with tab2:
        st.subheader("⚡ Current Settings")
        st.write("Adjust the current (in Amperes) for each cell:")
        col1, col2 = st.columns(2)
        updated_data = st.session_state.cells_data.copy()

        for idx, (cell_key, cell_data) in enumerate(st.session_state.cells_data.items()):
            with col1 if idx % 2 == 0 else col2:
                new_current = st.number_input(
                    f"Current for {cell_key.replace('_', ' ').title()}:",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(cell_data['current']),
                    step=0.1,
                    format="%.1f",
                    key=f"current_{cell_key}"
                )
                new_capacity = round(cell_data['voltage'] * new_current, 2)
                updated_data[cell_key]['current'] = new_current
                updated_data[cell_key]['capacity'] = new_capacity

        if st.button("🔄 Update All Currents", use_container_width=True):
            st.session_state.cells_data = updated_data
            st.success("All currents updated successfully!")

    # === Tab 3: Analytics ===
    with tab3:
        st.subheader("📈 Cell Analytics")
        df = pd.DataFrame([
            {
                'Cell': cell_key.replace('_', ' ').title(),
                'Voltage': data['voltage'],
                'Current': data['current'],
                'Temperature': data['temp'],
                'Capacity': data['capacity'],
                'Type': data['type']
            }
            for cell_key, data in st.session_state.cells_data.items()
        ])

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.bar(df, x='Cell', y='Voltage', color='Type', title='Voltage by Cell'), use_container_width=True)
            st.plotly_chart(px.scatter(df, x='Cell', y='Temperature', size='Capacity', color='Type', title='Temperature Distribution'), use_container_width=True)
        with col2:
            st.plotly_chart(px.bar(df, x='Cell', y='Current', color='Type', title='Current by Cell'), use_container_width=True)
            st.plotly_chart(px.pie(df, values='Capacity', names='Cell', title='Capacity Distribution'), use_container_width=True)

    # === Tab 4: Data Table ===
    with tab4:
        st.subheader("📋 Detailed Data Table")
        df_detailed = pd.DataFrame([
            {
                'Cell ID': key,
                'Type': data['type'],
                'Voltage (V)': data['voltage'],
                'Min Voltage (V)': data['min_voltage'],
                'Max Voltage (V)': data['max_voltage'],
                'Current (A)': data['current'],
                'Temperature (°C)': data['temp'],
                'Capacity (Ah)': data['capacity']
            }
            for key, data in st.session_state.cells_data.items()
        ])
        st.dataframe(df_detailed, use_container_width=True)
        st.download_button("📥 Download Data as CSV", df_detailed.to_csv(index=False), "battery_cell_data.csv", "text/csv")

else:
    st.info("👈 Please configure your cells in the sidebar and click 'Generate Cell Data' to get started!")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔋 LFP Cells")
        st.write("- **Voltage Range:** 2.8V - 3.6V")
        st.write("- **Nominal Voltage:** 3.2V")
        st.write("- **Chemistry:** Lithium Iron Phosphate")
        st.write("- **Characteristics:** Safe, long-lasting")
    with col2:
        st.subheader("⚡ NMC Cells")
        st.write("- **Voltage Range:** 3.2V - 4.0V")
        st.write("- **Nominal Voltage:** 3.6V")
        st.write("- **Chemistry:** Nickel Manganese Cobalt")
        st.write("- **Characteristics:** High energy density")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666; padding: 1rem;'>🔋 Battery Cell Management Dashboard | Built with Streamlit</div>", unsafe_allow_html=True)
