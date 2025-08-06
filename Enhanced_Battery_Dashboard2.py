import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd
import datetime
from io import StringIO

st.set_page_config(page_title="🔋 Battery Simulation Dashboard", layout="wide")

st.title("🔋 Battery Simulation Dashboard")

# --- CELL INPUT SECTION ---
with st.sidebar:
    st.header("🔧 Cell Configuration")
    number_of_cell = st.number_input("Number of Cells", min_value=1, max_value=10, value=2)
    list_of_cell = [st.selectbox(f"Cell {i+1} Type", ["lfp", "nmc"], key=f"cell_{i}") for i in range(number_of_cell)]

cells_data = {}
for idx, cell_type in enumerate(list_of_cell, start=1):
    voltage = 3.2 if cell_type == "lfp" else 3.6
    min_voltage = 2.8 if cell_type == "lfp" else 3.2
    max_voltage = 3.6 if cell_type == "lfp" else 4.0
    current = 0.0
    temp = round(random.uniform(25, 40), 1)
    capacity = round(voltage * current, 2)

    cells_data[f"Cell {idx} ({cell_type.upper()})"] = {
        "Voltage (V)": voltage,
        "Current (A)": current,
        "Temperature (°C)": temp,
        "Capacity (Ah)": capacity,
        "Min Voltage (V)": min_voltage,
        "Max Voltage (V)": max_voltage
    }

# --- Improved Cells Overview ---
with st.expander("📋 View Cells Overview", expanded=True):
    for name, data in cells_data.items():
        st.markdown(f"""
            <div style="
                background-color: #e3f2fd;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
            ">
            <h3 style="color:#0d47a1;">🔹 {name}</h3>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric(label="Voltage (V)", value=f"{data['Voltage (V)']:.2f}", delta=None)
        col2.metric(label="Temperature (°C)", value=f"{data['Temperature (°C)']:.1f}", delta=None)
        col3.metric(label="Capacity (Ah)", value=f"{data['Capacity (Ah)']:.3f}", delta=None)

        st.markdown("</div>", unsafe_allow_html=True)

# --- TASK CONFIGURATION ---
with st.sidebar:
    st.header("🛠️ Task Configuration")
    task_number = st.number_input("Number of Tasks", min_value=1, max_value=5, value=1)
    task_dict = {}

    for i in range(task_number):
        st.markdown(f"### Task {i+1}")
        task_type = st.selectbox(f"Type", ["CC_CV", "IDLE", "CC_CD"], key=f"task_{i}_type")
        task_key = f"task_{i+1}"
        task_data = {"task_type": task_type}

        if task_type == "CC_CV":
            task_data["cc_cp"] = st.text_input("CC Value (e.g. 5A)", key=f"cc_cp_{i}")
            task_data["cv_voltage"] = st.number_input("CV Voltage (V)", key=f"cv_voltage_{i}")
            task_data["current"] = st.number_input("Current (A)", key=f"current_{i}")
            task_data["capacity"] = st.number_input("Capacity", key=f"capacity_{i}")
            task_data["time_seconds"] = st.number_input("Duration (s)", min_value=1, key=f"time_{i}")
        elif task_type == "IDLE":
            task_data["time_seconds"] = st.number_input("Idle Time (s)", min_value=1, key=f"idle_{i}")
        elif task_type == "CC_CD":
            task_data["cc_cp"] = st.text_input("CC Value (e.g. 5A)", key=f"cc_cp_cd_{i}")
            task_data["voltage"] = st.number_input("Voltage (V)", key=f"voltage_cd_{i}")
            task_data["capacity"] = st.number_input("Capacity", key=f"capacity_cd_{i}")
            task_data["time_seconds"] = st.number_input("Duration (s)", min_value=1, key=f"time_cd_{i}")

        task_dict[task_key] = task_data

# --- Improved Task Configuration View ---
with st.expander("⚙️ View Task Configuration", expanded=False):
    for task_key, task in task_dict.items():
        # Colored box based on task type
        color_map = {
            "CC_CV": "#ffecb3",  # light yellow
            "IDLE": "#c8e6c9",   # light green
            "CC_CD": "#ffcdd2"   # light red
        }
        bg_color = color_map.get(task.get("task_type"), "#f0f0f0")

        st.markdown(f"""
            <div style="
                background-color: {bg_color};
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 12px;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            ">
            <h4 style="color:#37474f;">{task_key} - <span style='text-transform: uppercase;'>{task.get('task_type')}</span></h4>
        """, unsafe_allow_html=True)

        # Display task key-values
        for k, v in task.items():
            st.markdown(f"**{k.replace('_',' ').capitalize()}**: `{v}`")

        st.markdown("</div>", unsafe_allow_html=True)

# --- SIMULATION SECTION ---
st.markdown("## 🎬 Battery Simulation")
voltages = []
temps = []
start_time = datetime.datetime.now()
graph_placeholder = st.empty()
status_placeholder = st.empty()

if st.button("▶️ Start Simulation"):
    for i in range(40):
        voltage = round(random.uniform(3.1, 3.6), 3)
        temp = round(random.uniform(25, 40), 2)
        current = round(5.0 - (i * 0.1), 2) if i < 20 else round(-5.0 + (i * 0.1), 2)
        voltages.append(voltage)
        temps.append(temp)

        # Live status panel
        with status_placeholder.container():
            st.markdown("### 📈 Live Measurements")
            col1, col2, col3 = st.columns(3)
            col1.metric("Voltage (V)", voltage)
            col2.metric("Current (A)", current)
            col3.metric("Temperature (°C)", temp)

        # Live plotting
        with graph_placeholder.container():
            fig, ax1 = plt.subplots(figsize=(10, 4))
            time_labels = [(start_time + datetime.timedelta(seconds=j)).strftime("%H:%M:%S") for j in range(len(voltages))]
            ax1.plot(time_labels, [round(5.0 - (j * 0.1), 2) if j < 20 else round(-5.0 + (j * 0.1), 2) for j in range(len(voltages))], color='red', label='Current (A)')
            ax1.set_ylabel("Current (A)", color='red')
            ax1.tick_params(axis='y', labelcolor='red')
            ax1.set_ylim(-5.5, 5.5)
            ax1.set_xlabel("Time")

            ax2 = ax1.twinx()
            ax2.plot(time_labels, voltages, color='blue', label='Voltage (V)')
            ax2.set_ylabel("Voltage (V)", color='blue')
            ax2.tick_params(axis='y', labelcolor='blue')
            ax2.set_ylim(min(voltages) - 0.5, max(voltages) + 0.5)

            fig.autofmt_xdate(rotation=45)
            plt.title("Live Voltage and Current")
            st.pyplot(fig)

# --- CSV EXPORT ---
def generate_simulation_csv(voltages, temps, start_time, jump_events):
    sample_ids = list(range(1, len(voltages) + 1))
    test_data = {
        "Sample ID": sample_ids,
        "Sampling Time": ["00:30.0"] * len(sample_ids),
        "Termination": ["Step Jumped"] * len(sample_ids),
        "Actual Time": [(start_time + datetime.timedelta(seconds=i)).strftime("%H:%M:%S") for i in range(len(sample_ids))],
        "Voltage (V)": voltages,
        "Current (A)": [round(5.0 - (i * 0.1), 2) if i < 20 else round(-5.0 + (i * 0.1), 2) for i in range(len(sample_ids))],
        "Capacity (Ah)": [round(v * 0.0002, 6) for v in voltages],
        "Energy (Wh)": [round(v * 0.0006, 6) for v in voltages],
        "Step Type": ["Constant Voltage"] * len(sample_ids),
        "Cycle Count": [1] * len(sample_ids),
        "Step Number": list(range(1, len(sample_ids) + 1)),
        "DC Resistance": [0] * len(sample_ids),
        "Temperature (°C)": temps,
    }

    test_df = pd.DataFrame(test_data)
    stats_df = pd.DataFrame([[1, 0.056245, 0.0, 0.056245, 0.042359, "00:40.0", "00:00.0", "00:30.0", "00:30.0", 75.31, 100, 3.207, 3.207, max(temps), 15.6]], columns=[
        "Cycle Num", "CC Charge", "CV Charge", "Total Charge", "Total Discharge", "CC Charge Time", "CV Charge Time",
        "CC Discharge Time", "Total Discharge Time", "Efficiency (%)", "Capacity Fade (%)", "Avg Discharge Volt",
        "Median Voltage", "Max Temp", "DC Resistance (mΩ)"
    ])

    op_log_df = pd.DataFrame(jump_events)
    proc_df = pd.DataFrame([[
        "CC-CV Charge", "Constant Voltage", 5, 3.65, 3.65,
        6, "00:40.0", 0.03, 0, 0, 0
    ]], columns=[
        "Step Type", "Constant Type", "Voltage Limit", "Current Limit",
        "Capacity Limit", "Time Limit", "Temp Limit", "Delta V Limit",
        "Target Cap", "Step Num", "Jump Count"
    ])

    output = StringIO()
    output.write("### Test Data ###\n")
    test_df.to_csv(output, index=False)
    output.write("\n### Cycle Statistics ###\n")
    stats_df.to_csv(output, index=False)
    output.write("\n### Operation Log ###\n")
    op_log_df.to_csv(output, index=False)
    output.write("\n### Process Information ###\n")
    proc_df.to_csv(output, index=False)

    return output.getvalue()

# --- Download CSV ---
jump_events = [
    {"Timestamp": "19:31.7", "Sample ID": 3, "Event Type": "Step jumped due to time limit"},
    {"Timestamp": "19:48.5", "Sample ID": 5, "Event Type": "Step jumped due to time limit"},
    {"Timestamp": "20:20.6", "Sample ID": 7, "Event Type": "Step jumped due to time limit"},
    {"Timestamp": "20:47.6", "Sample ID": 9, "Event Type": "Step jumped due to time limit"},
    {"Timestamp": "20:52.9", "Sample ID": 11, "Event Type": "Step jumped due to current limit"},
    {"Timestamp": "21:58.7", "Sample ID": 14, "Event Type": "Channel test completed"}
]

if voltages:
    detailed_csv = generate_simulation_csv(voltages, temps, start_time, jump_events)
    st.markdown("### 📤 Export Results")
    st.download_button(
        label="📥 Download Detailed Simulation CSV",
        data=detailed_csv,
        file_name="battery_simulation.csv",
        mime="text/csv"
    )
