"""
UI Components for Restaurant Reservation Concierge Streamlit App.
Modular presentation components for Member 3 Frontend Lead.
"""

import streamlit as st
import pandas as pd
import textwrap
from ui.styles import (
    CUSTOM_CSS,
    render_decision_badge_html,
    render_preview_card_html,
    render_login_header_html
)

def inject_styles():
    """Injects custom CSS into the Streamlit session."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_login_page():
    """
    Renders the primary authentication gateway.
    Credentials:
      Username: admin
      Password: admin123
    """
    _, col_center, _ = st.columns([1, 1.4, 1])
    
    with col_center:
        st.markdown(render_login_header_html(), unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### Manager Sign In")
            st.caption("Enter authorized credentials to unlock the AI Concierge Yield Optimizer.")
            
            username = st.text_input("Username", placeholder="Enter username (admin)", key="login_username_input")
            password = st.text_input("Password", type="password", placeholder="Enter password (admin123)", key="login_password_input")
            
            submitted = st.form_submit_button("Sign In to Concierge", type="primary", use_container_width=True)
            
            if submitted:
                if username == "admin" and password == "admin123":
                    st.session_state.authenticated = True
                    st.session_state.username = "admin"
                    st.session_state.show_login_success = True
                    st.rerun()
                else:
                    st.error("Authentication failed: Invalid username or password.")

        st.markdown(textwrap.dedent("""
        <div class="credential-helper-box">
            <span>Authorized Demo Credentials:</span><br/>
            Username: <strong><code>admin</code></strong> &nbsp;&bull;&nbsp; Password: <strong><code>admin123</code></strong>
        </div>
        """).strip(), unsafe_allow_html=True)


def render_header(status_text: str = "Concierge Agent Active (Mock Mode)"):
    """Renders the top application navigation bar and branding."""
    st.markdown(textwrap.dedent(f"""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <h1 class="header-title">
                    Le Bistro AI Concierge
                </h1>
                <p class="header-subtitle">
                    Autonomous Restaurant Yield Optimizer & Dynamic Reservation Concierge
                </p>
            </div>
            <div>
                <span class="header-status-badge">
                    {status_text}
                </span>
            </div>
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)

def render_kpi_cards(context: dict, decision_data: dict = None):
    """Renders top 4 summary metric tiles."""
    c1, c2, c3, c4 = st.columns(4)
    
    occupancy = context.get("occupancy_pct", 50.0)
    cancellations = context.get("cancellations_count", 0)
    is_peak = context.get("is_peak", False)
    tier = context.get("customer_tier", "Regular")
    
    with c1:
        st.metric(
            label="Slot Occupancy",
            value=f"{occupancy:.0f}%",
            delta=f"{'Peak' if is_peak else 'Off-Peak'}",
            delta_color="normal" if occupancy > 70 else "inverse"
        )
    with c2:
        st.metric(
            label="Recent Cancellations",
            value=f"{cancellations} tables",
            delta="Gap Pressure" if cancellations >= 3 else "Normal",
            delta_color="inverse" if cancellations >= 3 else "normal"
        )
    with c3:
        st.metric(
            label="Target Diner Tier",
            value=tier,
            delta=f"Party of {context.get('party_size', 2)}"
        )
    with c4:
        decision_val = decision_data.get("decision", "pending") if decision_data else "Awaiting Run"
        decision_display = {
            "notify": "Notify Only",
            "low_incentive": "Low Incentive",
            "high_incentive": "High Incentive",
            "pending": "Ready"
        }.get(decision_val, decision_val.upper())
        
        st.metric(
            label="Concierge Strategy",
            value=decision_display,
            delta="Yield Protected" if decision_data else "Select Scenario"
        )

def render_decision_display(decision_data: dict, context: dict):
    """Renders the Decision badge, Plain English reasoning, and Outreach Preview."""
    decision = decision_data.get("decision", "notify")
    reasoning = decision_data.get("reasoning", "No reasoning recorded.")
    offer = decision_data.get("offer", "No offer generated.")
    
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.subheader("Agent Strategy & Rationale")
        st.markdown(render_decision_badge_html(decision), unsafe_allow_html=True)
        
        st.markdown(textwrap.dedent(f"""
        <div class="reasoning-box">
            <div style="font-weight: 600; color: #4338ca; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.4rem;">
                Explainable Agent Reasoning:
            </div>
            <div style="color: #334155; font-size: 0.93rem; line-height: 1.55;">
                {reasoning}
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        with st.expander("Inspection: Structured Context Ingested by Agent", expanded=False):
            st.json(context)

    with col_right:
        st.subheader("Rendered Outreach Payload")
        st.caption("Rendered in-app preview (conforms to No External Channel guideline)")
        st.markdown(
            render_preview_card_html(
                customer_name=context.get("customer_name", "Valued Diner"),
                tier=context.get("customer_tier", "Regular"),
                time_slot=context.get("time_slot", "19:00"),
                offer_text=offer,
                decision=decision
            ),
            unsafe_allow_html=True
        )

def render_manager_action_bar(reservation_id: str, current_status: str, on_accept_callback, on_override_callback):
    """Allows the restaurant manager to approve or override the agent's action."""
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3 = st.columns([2, 1, 1])
    with m_col1:
        st.info(f"Target Record: **{reservation_id}** (Current Status: `{current_status}`)")
    with m_col2:
        if st.button("Confirm & Update Dataset", use_container_width=True, type="primary"):
            on_accept_callback()
    with m_col3:
        if st.button("Manager Override", use_container_width=True):
            on_override_callback()

def render_occupancy_chart(trends: list[dict], current_slot: str = "20:00"):
    """Renders visual bar chart of dining slots and highlights current slot."""
    df = pd.DataFrame(trends)
    if df.empty:
        return
    
    st.subheader("Slot Occupancy & Cancellation Volatility")
    
    # Display using Streamlit bar chart
    chart_data = df.set_index("slot")[["occupancy", "cancellations"]]
    st.bar_chart(chart_data, color=["#3b82f6", "#ef4444"])
    st.caption("Blue: Occupancy % | Red: Sudden Cancellation Gaps")

def render_reservation_records_table(reservations: list[dict], active_id: str = None):
    """Renders the live reservation table demonstrating dataset updates."""
    st.subheader("Live Reservation Records (Dataset View)")
    
    df = pd.DataFrame(reservations)
    if not df.empty:
        cols_to_display = ["reservation_id", "customer_name", "tier", "time_slot", "table_id", "party_size", "status", "updated_at"]
        clean_df = df[cols_to_display].copy()
        clean_df.columns = ["Reservation ID", "Customer", "Tier", "Time Slot", "Table", "Party", "Status", "Updated At"]
        
        st.dataframe(
            clean_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No reservation records in dataset.")

def render_decision_history(history: list[dict]):
    """Renders session history of agent decisions."""
    if not history:
        return
    st.subheader("Session Decision Audit Log")
    df_hist = pd.DataFrame(history)
    st.dataframe(df_hist, use_container_width=True, hide_index=True)
