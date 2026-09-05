"""
Custom styles and HTML templates for Restaurant Reservation Concierge Streamlit UI.
Provides polished badges, customer notification preview card, reasoning container,
and interactive control cards.
"""

CUSTOM_CSS = """
<style>
/* Font and container polish */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* App Header styling */
.header-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid #334155;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.header-title {
    color: #f8fafc;
    font-size: 1.75rem;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.header-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.25rem;
    margin-bottom: 0;
}

.header-status-badge {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

/* Decision Badges */
.badge-notify {
    background-color: #dbeafe;
    color: #1e40af;
    border: 1px solid #93c5fd;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.badge-low-incentive {
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #fcd34d;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

.badge-high-incentive {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
    padding: 0.4rem 1rem;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.1rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

/* Agent Reasoning Callout */
.reasoning-box {
    background: #f8fafc;
    border-left: 5px solid #6366f1;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    padding: 1.25rem;
    border-radius: 0 10px 10px 0;
    margin-top: 0.75rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.reasoning-box-dark {
    background: #1e293b;
    border-left: 5px solid #818cf8;
    border-top: 1px solid #334155;
    border-right: 1px solid #334155;
    border-bottom: 1px solid #334155;
    padding: 1.25rem;
    border-radius: 0 10px 10px 0;
    margin-top: 0.75rem;
    color: #e2e8f0;
}

/* Customer Mobile Notification Preview Card */
.mobile-preview-frame {
    background: #ffffff;
    border: 2px solid #e2e8f0;
    border-radius: 20px;
    padding: 1rem;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    position: relative;
    max-width: 480px;
    margin: 0 auto;
}

.mobile-preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #f1f5f9;
    padding-bottom: 0.5rem;
    margin-bottom: 0.75rem;
}

.sender-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.sender-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #4f46e5;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    font-weight: bold;
}

.sender-name {
    font-weight: 600;
    font-size: 0.9rem;
    color: #0f172a;
}

.message-bubble {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px 12px 12px 2px;
    padding: 0.85rem 1rem;
    color: #1e293b;
    font-size: 0.92rem;
    line-height: 1.45;
    position: relative;
}

.message-timestamp {
    text-align: right;
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.4rem;
}

.channel-tag {
    font-size: 0.75rem;
    background: #e2e8f0;
    color: #475569;
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    font-weight: 500;
}

/* KPI Summary Cards */
.kpi-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.kpi-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0f172a;
}

.kpi-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    color: #64748b;
    letter-spacing: 0.05em;
    margin-top: 0.2rem;
}

/* Login Page Styling */
.login-hero-container {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid #312e81;
    border-radius: 16px;
    padding: 2.2rem 2rem 1.8rem;
    text-align: center;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
    margin-bottom: 1.5rem;
}

.login-logo-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 14px;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: #ffffff;
    font-size: 1.8rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
}

.login-title {
    color: #ffffff;
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
}

.login-subtitle {
    color: #a5b4fc;
    font-size: 0.92rem;
    margin-top: 0.4rem;
    margin-bottom: 1rem;
}

.login-badge-pill {
    display: inline-block;
    background: rgba(99, 102, 241, 0.18);
    color: #c7d2fe;
    border: 1px solid rgba(129, 140, 248, 0.3);
    padding: 0.25rem 0.8rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.credential-helper-box {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #475569;
    margin-top: 1rem;
    text-align: center;
}
</style>
"""

import textwrap

def render_decision_badge_html(decision: str) -> str:
    """Renders HTML for the decision badge."""
    decision_map = {
        "notify": (
            "badge-notify",
            "NOTIFY ONLY - SOFT NUDGE",
            "No discount needed | Brand margin preserved"
        ),
        "low_incentive": (
            "badge-low-incentive",
            "LOW INCENTIVE - COMPLIMENTARY PERK",
            "Value-add culinary perk | Protects menu prices"
        ),
        "high_incentive": (
            "badge-high-incentive",
            "HIGH INCENTIVE - DYNAMIC DISCOUNT",
            "20% Dining Concession | Fills critical off-peak void"
        )
    }
    css_class, label, sublabel = decision_map.get(
        decision, 
        ("badge-notify", f"DECISION: {decision.upper()}", "Evaluated by AI Agent")
    )
    return textwrap.dedent(f"""
    <div style="margin: 0.5rem 0 1rem 0;">
        <div class="{css_class}">
            <span>{label}</span>
        </div>
        <div style="color: #64748b; font-size: 0.85rem; margin-top: 0.35rem; font-weight: 500;">
            {sublabel}
        </div>
    </div>
    """).strip()

def render_preview_card_html(customer_name: str, tier: str, time_slot: str, offer_text: str, decision: str) -> str:
    """Renders customer-facing rendered message preview satisfying hackathon guidelines."""
    tier_colors = {
        "Gold": "#d97706",
        "Silver": "#64748b",
        "Regular": "#2563eb"
    }
    tier_color = tier_colors.get(tier, "#64748b")
    
    return f"""<div class="mobile-preview-frame">
<div class="mobile-preview-header">
<div class="sender-info">
<div class="sender-avatar">LB</div>
<div>
<div class="sender-name">Le Bistro Concierge</div>
<div style="font-size: 0.75rem; color: #64748b;">Automated In-App Dispatch</div>
</div>
</div>
<div style="display: flex; gap: 0.4rem; align-items: center;">
<span class="channel-tag" style="border-left: 3px solid {tier_color};">{tier.upper()} GUEST</span>
<span class="channel-tag">SMS / Push</span>
</div>
</div>
<div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem; display: flex; justify-content: space-between;">
<span>To: <strong>{customer_name}</strong></span>
<span>Window: <strong>{time_slot}</strong></span>
</div>
<div class="message-bubble">
<div>{offer_text}</div>
<div class="message-timestamp"><span>Delivered</span></div>
</div>
<div style="display: flex; justify-content: space-around; margin-top: 0.75rem; padding-top: 0.5rem; border-top: 1px dashed #e2e8f0; font-size: 0.8rem;">
<span style="color: #2563eb; font-weight: 600; cursor: pointer;">[ Reserve Table ]</span>
<span style="color: #64748b; font-weight: 500; cursor: pointer;">[ Change Time ]</span>
<span style="color: #94a3b8; cursor: pointer;">[ Opt Out ]</span>
</div>
</div>"""

def render_login_header_html() -> str:
    """Renders the executive login brand header."""
    return textwrap.dedent("""
    <div class="login-hero-container">
        <div class="login-logo-badge">
            LB
        </div>
        <h1 class="login-title">Le Bistro Concierge</h1>
        <p class="login-subtitle">Autonomous Restaurant Yield Optimizer & AI Reservation Concierge</p>
        <div class="login-badge-pill">
            Executive Portal &middot; Restricted Access
        </div>
    </div>
    """).strip()


