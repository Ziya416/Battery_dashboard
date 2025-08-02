import streamlit as st
import plotly.graph_objects as go
import time

st.set_page_config(page_title="🔋 Battery Dashboard", layout="wide")
st.title("🔋 Battery Dashboard (Calculated Capacity)")

# Initialize session state
if "simulation_started" not in st.session_state:
    st.session_state.simulation_started = False
if "analysis_requested" not in st.session_state:
    st.session_state.analysis_requested = False
if "all_cells_data" not in st.session_state:
    st.session_state.all_cells_data = []

# Sidebar controls
st.sidebar.header("🎛️ Control Panel")
cell_count = st.sidebar.slider("How many battery cells?", 1, 10, 2)
state = st.sidebar.radio("Battery State", ["Idle", "Charging", "Discharging"])
duration = st.sidebar.slider("Simulation Duration (s)", 5, 30, 10)

state_colors = {"Charging": "#43e97b", "Discharging": "#f67280", "Idle": "#cccccc"}
cols = st.columns(cell_count)

user_inputs = []

# Collect inputs first
for i in range(cell_count):
    with cols[i]:
        st.subheader(f"🔋 Cell {i + 1} Inputs")
        cell_type = st.selectbox(f"Battery Type - Cell {i+1}", ["LFP", "NMC"], key=f"type_{i}")
        user_current = st.number_input(f"Current (A) - Cell {i+1}", min_value=0.0, value=0.5, step=0.1, key=f"cur_{i}")
        user_temp = st.number_input(f"Temperature (°C) - Cell {i+1}", min_value=0.0, value=30.0, step=0.5, key=f"temp_{i}")
        user_inputs.append({"type": cell_type, "current": user_current, "temp": user_temp})

# Button controls
if st.button("▶️ Start Simulation"):
    st.session_state.simulation_started = True
    st.session_state.analysis_requested = False
    st.session_state.all_cells_data = []  # Reset

if st.button("📊 Show Analysis"):
    st.session_state.analysis_requested = True

# Run simulation only if triggered
if st.session_state.simulation_started:
    sim_cols = st.columns(cell_count)
    for i in range(cell_count):
        cell_type = user_inputs[i]["type"]
        user_current = user_inputs[i]["current"]
        user_temp = user_inputs[i]["temp"]

        if cell_type == "LFP":
            min_v = 2.8
            max_v = 3.6
            nominal_v = 3.2
        else:
            min_v = 3.2
            max_v = 4.0
            nominal_v = 3.6

        voltages, times, currents, temps, capacities = [], [], [], [], []

        with sim_cols[i]:
            st.markdown("---")
            st.markdown(f"### ⏱ Simulation Output for Cell {i+1}")
            battery_display = st.empty()
            stats = st.empty()
            progress_bar = st.empty()

            for t in range(duration + 1):
                if state == "Charging":
                    voltage = round(min_v + (t / duration) * (max_v - min_v), 2)
                elif state == "Discharging":
                    voltage = round(max_v - (t / duration) * (max_v - min_v), 2)
                else:
                    voltage = nominal_v

                capacity = round(voltage * user_current, 2)

                voltages.append(voltage)
                currents.append(user_current)
                temps.append(user_temp)
                capacities.append(capacity)
                times.append(t)

                fill = (voltage - min_v) / (max_v - min_v)
                battery_display.markdown(f"""
                <div style='
                    width: 60px;
                    height: 120px;
                    border: 4px solid #333;
                    border-radius: 6px;
                    position: relative;
                    background: #fff;
                    margin: 10px auto;'>
                    <div style='
                        width: 100%;
                        height: {int(fill * 100)}%;
                        background-color: {state_colors[state]};
                        position: absolute;
                        bottom: 0;
                        transition: height 0.2s ease-in-out;'>
                    </div>
                    <div style='
                        width: 20px;
                        height: 10px;
                        background: #333;
                        position: absolute;
                        top: -14px;
                        left: 20px;
                        border-radius: 2px;'>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                stats.markdown(f"""
                **🔌 Voltage:** {voltage} V  
                **⚡ Current:** {user_current} A  
                **🌡 Temp:** {user_temp} °C  
                **📊 Capacity (V×A):** {capacity} Wh  
                **⏱ Time:** {t}s
                """)
                progress_bar.progress(fill, text=f"{round(fill * 100)}% Charged" if state == "Charging" else f"{round(fill * 100)}% Remaining")
                time.sleep(0.1)

            st.session_state.all_cells_data.append({
                "label": f"Cell {i+1}",
                "time": times,
                "voltage": voltages,
                "current": currents,
                "temp": temps,
                "capacity": capacities
            })

    st.session_state.simulation_started = False  # Reset to prevent rerun

# Show analysis if requested
if st.session_state.analysis_requested and st.session_state.all_cells_data:
    st.markdown("---")
    st.header("📊 Analysis Charts")

    tab1, tab2, tab3 = st.tabs(["🔌 Voltage & Current", "🌡 Temperature", "⚡ Capacity"])

    with tab1:
        fig1 = go.Figure()
        for cell in st.session_state.all_cells_data:
            fig1.add_trace(go.Scatter(x=cell["time"], y=cell["voltage"], mode='lines+markers', name=f"{cell['label']} Voltage"))
            fig1.add_trace(go.Scatter(x=cell["time"], y=cell["current"], mode='lines+markers', name=f"{cell['label']} Current"))
        fig1.update_layout(title="Voltage and Current Over Time", xaxis_title="Time (s)", yaxis_title="Values")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = go.Figure()
        for cell in st.session_state.all_cells_data:
            fig2.add_trace(go.Scatter(x=cell["time"], y=cell["temp"], mode='lines+markers', name=cell["label"]))
        fig2.update_layout(title="Temperature Over Time", xaxis_title="Time (s)", yaxis_title="Temp (°C)")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        fig3 = go.Figure()
        for cell in st.session_state.all_cells_data:
            fig3.add_trace(go.Scatter(x=cell["time"], y=cell["capacity"], mode='lines+markers', name=cell["label"]))
        fig3.update_layout(title="Capacity Over Time", xaxis_title="Time (s)", yaxis_title="Capacity (Wh)")
        st.plotly_chart(fig3, use_container_width=True)
