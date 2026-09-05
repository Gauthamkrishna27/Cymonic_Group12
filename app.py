"""
Restaurant Reservation Concierge - Main Streamlit Application.
Frontend Lead (Member 3) Implementation.

Provides an enterprise-grade AI Concierge with:
1. Executive Login Authentication Gateway (Admin access).
2. Autonomous dynamic yield optimization & reservation concierge.
3. Teammate zero-configuration auto-plugging (Member 1 data/store.py & Member 2 agent/reasoning.py).
"""

import streamlit as st
import time
from datetime import datetime

# Streamlit Page Config
st.set_page_config(
    page_title="Le Bistro Concierge | AI Yield Optimizer",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dynamic Adapter: Auto-detect teammates' modules if present
HAS_REAL_DATA = False
HAS_REAL_AGENT = False

try:
    from data.store import get_context as real_get_context
    from data.store import update_record as real_update_record
    from data.store import list_scenarios as real_list_scenarios
    from data.store import get_all_reservations as real_get_all_reservations
    HAS_REAL_DATA = True
except ImportError:
    pass

try:
    from agent.reasoning import run_concierge as real_run_concierge
    HAS_REAL_AGENT = True
except ImportError:
    pass

# Import mock backend fallbacks conforming to CONTRACT.md
import ui.mock_backend as mock_backend
from ui.components import (
    inject_styles,
    render_login_page,
    render_header,
    render_kpi_cards,
    render_decision_display,
    render_occupancy_chart,
    render_reservation_records_table,
    render_decision_history
)

# Apply UI CSS styles
inject_styles()

# ----------------- SESSION STATE INITIALIZATION -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "show_login_success" not in st.session_state:
    st.session_state.show_login_success = False

if "username" not in st.session_state:
    st.session_state.username = None

if "reservations" not in st.session_state:
    st.session_state.reservations = mock_backend.get_all_reservations()

if "history" not in st.session_state:
    st.session_state.history = []

if "last_decision" not in st.session_state:
    st.session_state.last_decision = None

if "last_context" not in st.session_state:
    st.session_state.last_context = None

if "status_notification" not in st.session_state:
    st.session_state.status_notification = None

if "auto_pilot" not in st.session_state:
    st.session_state.auto_pilot = False

# ----------------- AUTHENTICATION GATEWAY -----------------
# Ensure the login page is the first page to be opened
if not st.session_state.authenticated:
    render_login_page()
    st.stop()

# ----------------- NOTIFICATIONS UPON SUCCESSFUL LOGIN -----------------
if st.session_state.show_login_success:
    st.success("Login successful! Welcome to Le Bistro Concierge.")
    st.toast("Login successful!")
    st.session_state.show_login_success = False

# ----------------- SIDEBAR: ENVIRONMENT & INTEGRATION -----------------
with st.sidebar:
    st.title("System Control")
    st.markdown(f"**Manager Profile:** `{st.session_state.username}`")
    
    if st.button("Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.show_login_success = False
        st.session_state.last_decision = None
        st.rerun()

    st.markdown("---")
    
    # Mode indicator
    if HAS_REAL_DATA and HAS_REAL_AGENT:
        active_mode = "Live Integrated Stack (M1 + M2 + M3)"
        st.success("Full Backend Connected")
    elif HAS_REAL_AGENT:
        active_mode = "Live Agent + Mock Dataset"
        st.info("Live LLM Agent Active")
    elif HAS_REAL_DATA:
        active_mode = "Live Dataset + Mock Agent"
        st.info("Live Dataset Active")
    else:
        active_mode = "Contract Mock Mode (Standalone)"
        st.caption("Ready for Teammate Integration")

    st.markdown("---")
    st.subheader("Autonomous Agent Settings")
    auto_pilot_toggle = st.toggle(
        "Auto-Pilot Mode",
        value=st.session_state.auto_pilot,
        help="When enabled, the Concierge Agent automatically triggers analysis and executes recommendations on context change."
    )
    st.session_state.auto_pilot = auto_pilot_toggle
    
    st.markdown("---")
    st.subheader("Hackathon Team Status")
    st.markdown(f"""
    - **M1 (Data Layer):** {'Ready' if HAS_REAL_DATA else 'Mock Active'}
    - **M2 (Reasoning Agent):** {'Ready' if HAS_REAL_AGENT else 'Mock Active'}
    - **M3 (Frontend UI):** **Complete & Autonomous**
    - **M4 (Integration/QA):** **Auto-Plugging Ready**
    """)
    
    st.markdown("---")
    if st.button("Reset Session & Dataset", use_container_width=True):
        st.session_state.reservations = mock_backend.get_all_reservations()
        st.session_state.history = []
        st.session_state.last_decision = None
        st.session_state.last_context = None
        st.session_state.status_notification = "Session and dataset reset to initial state."
        st.rerun()

# ----------------- MAIN DASHBOARD VIEW -----------------
render_header(status_text=active_mode)

if st.session_state.status_notification:
    st.success(st.session_state.status_notification)
    st.session_state.status_notification = None

# 1. SCENARIO SELECTION & SIMULATOR
st.subheader("Scenario Selector & Dynamic Simulator")

# Load scenarios
scenarios = real_list_scenarios() if HAS_REAL_DATA else mock_backend.list_scenarios()
scenario_labels = [s["label"] for s in scenarios]
scenario_labels.append("Custom Scenario Simulator (Judge Sandbox)")

col_sel, col_mode = st.columns([3, 1])

with col_sel:
    selected_option = st.selectbox(
        "Select an operational scenario to evaluate:",
        options=scenario_labels,
        index=1  # Default to Scenario 2 for strong demo impact
    )

is_custom = selected_option.startswith("Custom Scenario Simulator")

if not is_custom:
    selected_scenario = next(s for s in scenarios if s["label"] == selected_option)
    scenario_id = selected_scenario["id"]
    
    # Retrieve context
    if HAS_REAL_DATA:
        active_context = real_get_context(scenario_id)
    else:
        active_context = mock_backend.get_context(scenario_id)
    
    st.caption(f"**Scenario Context:** {selected_scenario.get('description', '')}")
else:
    st.markdown("##### Sandbox Parameters (Tweak and evaluate how the agent dynamically responds):")
    sim_c1, sim_c2, sim_c3 = st.columns(3)
    with sim_c1:
        custom_occupancy = st.slider("Current Occupancy %", min_value=10, max_value=100, value=35, step=5)
        custom_cancellations = st.number_input("Recent Cancellations Count", min_value=0, max_value=10, value=4)
    with sim_c2:
        custom_slot = st.selectbox("Dining Time Slot", ["12:00 PM", "01:00 PM", "02:30 PM", "05:30 PM", "07:00 PM", "08:00 PM", "09:30 PM"], index=3)
        custom_is_peak = st.checkbox("Peak Dining Window", value=False)
    with sim_c3:
        custom_tier = st.selectbox("Target Customer Loyalty Tier", ["Gold", "Silver", "Regular"], index=0)
        custom_party = st.number_input("Party Size", min_value=1, max_value=8, value=4)

    active_context = {
        "scenario_id": "custom_sandbox",
        "time_slot": custom_slot,
        "is_peak": custom_is_peak,
        "occupancy_pct": float(custom_occupancy),
        "cancellations_count": int(custom_cancellations),
        "customer_id": "CUST-SANDBOX",
        "customer_name": "Valued Sandbox Guest",
        "customer_tier": custom_tier,
        "reservation_id": "RES-SANDBOX",
        "table_id": "T-09",
        "party_size": custom_party,
        "last_visit_days_ago": 14,
        "lifetime_spend": "$1,200"
    }

# Render KPI overview for the selected context
render_kpi_cards(active_context, st.session_state.last_decision)

# 2. TRIGGER AGENT EXECUTION
run_agent = False

if st.session_state.auto_pilot:
    # Auto-pilot triggers if context changed
    if st.session_state.last_context != active_context:
        run_agent = True
else:
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    c_btn, c_note = st.columns([1.5, 3.5])
    with c_btn:
        if st.button("Run Concierge Agent", type="primary", use_container_width=True):
            run_agent = True
    with c_note:
        st.caption("Agent parses occupancy, cancellation spike, customer tier, and time-of-day to formulate a yield-preserving strategy.")

if run_agent:
    with st.spinner("Concierge Agent reasoning over table yield and brand economics..."):
        # Brief natural delay for demonstration feel
        time.sleep(0.4)
        
        # Call agent function (Member 2 or Mock)
        if HAS_REAL_AGENT:
            decision_result = real_run_concierge(active_context)
        else:
            decision_result = mock_backend.run_concierge(active_context)

        st.session_state.last_decision = decision_result
        st.session_state.last_context = active_context

        # Automatically update dataset
        res_id = active_context.get("reservation_id", "RES-AUTO")
        new_status = "offer_sent" if decision_result.get("decision") != "notify" else "notified"
        
        if HAS_REAL_DATA:
            real_update_record(res_id, new_status, decision_result.get("offer"))
            st.session_state.reservations = real_get_all_reservations()
        else:
            updated_record = mock_backend.update_record(res_id, new_status, decision_result.get("offer"))
            # Update in-session list
            st.session_state.reservations = mock_backend.get_all_reservations()

        # Log to session history
        st.session_state.history.insert(0, {
            "Timestamp": datetime.now().strftime("%H:%M:%S"),
            "Scenario": active_context.get("scenario_id", "Manual"),
            "Slot": active_context.get("time_slot"),
            "Customer": active_context.get("customer_name"),
            "Tier": active_context.get("customer_tier"),
            "Decision": decision_result.get("decision").upper(),
            "Status": new_status.upper()
        })

# 3. DISPLAY AGENT DECISION & EXPLAINABILITY
if st.session_state.last_decision:
    st.markdown("---")
    render_decision_display(st.session_state.last_decision, active_context)
    
    # Manager action approval
    res_id = active_context.get("reservation_id", "RES-AUTO")
    c_m1, c_m2 = st.columns([3, 1])
    with c_m1:
        st.caption(f"Record `{res_id}` synchronized to reservations dataset with status `{new_status if run_agent else 'logged'}`.")
    with c_m2:
        if st.button("Re-evaluate Strategy"):
            st.session_state.last_decision = None
            st.rerun()

# 4. ANALYTICS & VISUALIZATION
st.markdown("---")
tab_charts, tab_dataset, tab_history = st.tabs(["Occupancy & Cancellations", "Dataset Records", "Audit History"])

with tab_charts:
    trends_data = mock_backend.get_occupancy_trends()
    render_occupancy_chart(trends_data, active_context.get("time_slot", "20:00"))

with tab_dataset:
    render_reservation_records_table(st.session_state.reservations, active_context.get("reservation_id"))

with tab_history:
    render_decision_history(st.session_state.history)
