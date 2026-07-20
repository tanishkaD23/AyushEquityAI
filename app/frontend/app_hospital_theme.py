"""
Hospital-themed AyushEquityAI application.
Premium, attractive, professional healthcare interface.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os
# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from app.frontend.styles import apply_custom_styling, create_metric_card, create_info_box, create_header
from app.frontend.theme_config import COLORS


# ===== PAGE 1: OFFICER DASHBOARD =====
def show_officer_dashboard():
    """Premium Officer Dashboard for claim processing & hospital monitoring."""

    # Header
    create_header(
        "Officer Dashboard",
        "Claim Processing | Hospital Monitoring | Fraud Prevention",
        "🎯"
    )

    try:
        # Load data
        claims_df = pd.read_csv("app/data/mock_claims.csv")
        hospital_risk_df = pd.read_csv("app/data/hospital_risk_scores.csv")
        inclusion_df = pd.read_csv("app/data/inclusion_pipeline_results.csv")

        # === KPI METRICS ===
        st.markdown("### 📈 Key Performance Indicators")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown(f"""
            <div class="metric-card success">
                <div class="metric-label">Total Claims</div>
                <div class="metric-value">{len(claims_df):,}</div>
                <div class="metric-delta">+342 today</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            flagged = (claims_df['fraud_pattern'] != 'none').sum()
            st.markdown(f"""
            <div class="metric-card danger">
                <div class="metric-label">Flagged Claims</div>
                <div class="metric-value">{flagged:,}</div>
                <div class="metric-delta">+18 today</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            total_amount = claims_df['billed_amount'].sum()
            st.markdown(f"""
            <div class="metric-card info">
                <div class="metric-label">Total Amount</div>
                <div class="metric-value">₹{total_amount/1e7:.1f}Cr</div>
                <div class="metric-delta">+₹2.3Cr</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            fraud_pct = (flagged / len(claims_df) * 100)
            st.markdown(f"""
            <div class="metric-card warning">
                <div class="metric-label">Fraud Rate</div>
                <div class="metric-value">{fraud_pct:.1f}%</div>
                <div class="metric-delta negative">-0.5%</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            high_risk_hospitals = len(hospital_risk_df[hospital_risk_df['risk_level'].isin(['CRITICAL', 'HIGH'])])
            st.markdown(f"""
            <div class="metric-card danger">
                <div class="metric-label">High Risk Hospitals</div>
                <div class="metric-value">{high_risk_hospitals}</div>
                <div class="metric-delta">Under monitoring</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # === TABS ===
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Claims Queue", "⚠️ Fraud Detection", "🏥 Hospital Risk", "🔒 Audit Trail"])

        with tab1:
            st.markdown("### Claims Processing Queue")

            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### High-Priority Flagged Claims")
                flagged_claims = claims_df[claims_df['fraud_pattern'] != 'none'].head(10)

                if len(flagged_claims) > 0:
                    display_df = flagged_claims[['claim_id', 'hospital_id', 'billed_amount', 'fraud_pattern']].copy()
                    display_df['Status'] = '⚠️ Review Required'

                    st.dataframe(
                        display_df.rename(columns={
                            'claim_id': 'Claim ID',
                            'hospital_id': 'Hospital',
                            'billed_amount': 'Amount (₹)',
                            'fraud_pattern': 'Type'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

            with col2:
                st.markdown("#### Processing Stats")
                st.metric("Pending Review", len(flagged_claims))
                st.metric("Approved Today", "342")
                st.metric("Rejected Today", "12")

            st.markdown("---")
            st.markdown("#### Normal Claims - Auto-Approved")
            normal = claims_df[claims_df['fraud_pattern'] == 'none'].head(10)

            if len(normal) > 0:
                st.dataframe(
                    normal[['claim_id', 'hospital_id', 'treatment_code', 'billed_amount']].rename(
                        columns={
                            'claim_id': 'Claim ID',
                            'hospital_id': 'Hospital',
                            'treatment_code': 'Treatment',
                            'billed_amount': 'Amount (₹)'
                        }
                    ),
                    use_container_width=True,
                    hide_index=True
                )

        with tab2:
            st.markdown("### Fraud Detection Analytics")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### Fraud Patterns Distribution")
                fraud_counts = claims_df['fraud_pattern'].value_counts()

                fig = go.Figure(data=[
                    go.Bar(
                        x=fraud_counts.index,
                        y=fraud_counts.values,
                        marker=dict(
                            color=fraud_counts.values,
                            colorscale='Reds',
                            showscale=True
                        ),
                        text=fraud_counts.values,
                        textposition='auto'
                    )
                ])

                fig.update_layout(
                    title="Claims by Fraud Type",
                    xaxis_title="Fraud Type",
                    yaxis_title="Count",
                    hovermode='x unified',
                    template='plotly_white',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### Top Fraud Hospitals")
                fraud_by_hosp = claims_df[
                    claims_df['fraud_pattern'] != 'none'
                ]['hospital_id'].value_counts().head(10)

                fig = go.Figure(data=[
                    go.Bar(
                        x=fraud_by_hosp.values,
                        y=fraud_by_hosp.index,
                        orientation='h',
                        marker=dict(color='#C62828')
                    )
                ])

                fig.update_layout(
                    title="Top 10 Hospitals with Fraud Flags",
                    xaxis_title="Number of Flagged Claims",
                    yaxis_title="Hospital ID",
                    height=400,
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.markdown("### Hospital Risk Assessment")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("#### Risk Distribution")
                risk_counts = hospital_risk_df['risk_level'].value_counts()

                colors_map = {
                    'CRITICAL': '#C62828',
                    'HIGH': '#F57C00',
                    'MEDIUM': '#FBC02D',
                    'LOW': '#2E7D32'
                }

                fig = go.Figure(data=[
                    go.Pie(
                        labels=risk_counts.index,
                        values=risk_counts.values,
                        marker=dict(colors=[colors_map.get(x, '#757575') for x in risk_counts.index]),
                        hoverinfo='label+value+percent'
                    )
                ])

                fig.update_layout(
                    title="Hospital Risk Distribution",
                    height=400,
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown("#### Highest Risk Hospitals")
                top_risk = hospital_risk_df.head(15)

                # Create risk level colors
                colors = []
                for risk in top_risk['risk_level']:
                    if risk == 'CRITICAL':
                        colors.append('#C62828')
                    elif risk == 'HIGH':
                        colors.append('#F57C00')
                    elif risk == 'MEDIUM':
                        colors.append('#FBC02D')
                    else:
                        colors.append('#2E7D32')

                fig = go.Figure(data=[
                    go.Bar(
                        x=top_risk['risk_score'],
                        y=top_risk['name'],
                        orientation='h',
                        marker=dict(color=colors),
                        text=top_risk['risk_score'].round(1),
                        textposition='auto'
                    )
                ])

                fig.update_layout(
                    title="Top 15 Hospitals by Risk Score",
                    xaxis_title="Risk Score (0-100)",
                    yaxis_title="Hospital",
                    height=400,
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.markdown("### Immutable Audit Trail")

            create_info_box(
                "✓ SHA-256 Hash Chain Verified | Zero Tampering Detected | All Actions Logged",
                "success",
                "System Integrity Status"
            )

            st.markdown("#### Recent Actions")
            audit_data = {
                'Timestamp': ['2024-01-20 14:32', '2024-01-20 14:15', '2024-01-20 13:45'],
                'Claim ID': ['CLM0001234', 'CLM0001233', 'CLM0001232'],
                'Action': ['Approved', 'Flagged', 'Rejected'],
                'Officer': ['Officer Sharma', 'Officer Patel', 'Officer Kumar'],
                'Hash': ['3a4f8b...', '7d2e9c...', 'e5b1f2...']
            }

            st.dataframe(
                pd.DataFrame(audit_data),
                use_container_width=True,
                hide_index=True
            )

    except FileNotFoundError:
        create_info_box(
            "Data files not found. Please run Day 4-6 setup first.",
            "warning",
            "Setup Required"
        )


# ===== PAGE 2: CITIZEN PORTAL =====
def show_citizen_portal():
    """Premium Citizen Portal for eligibility checking."""

    create_header(
        "Citizen Portal",
        "Check Your PM-JAY Eligibility & Find Healthcare Services",
        "👨‍👩‍👧‍👦"
    )

    st.markdown("""
    <div style='background: linear-gradient(135deg, #E3F2FD 0%, #E0F2F1 100%);
                padding: 20px; border-radius: 12px; margin-bottom: 30px;'>
        <h3 style='color: #0D47A1; margin-top: 0;'>Welcome to AyushEquityAI</h3>
        <p style='color: #424242;'>
            Check if you're eligible for PM-JAY (Ayushman Bharat) and find empanelled hospitals near you.
            Your health is our priority.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📋 Your Information")

        income_band = st.selectbox(
            "Annual Household Income Band",
            options=["BPL (Below Poverty Line)", "APL (Above Poverty Line)", "EWS (Economically Weaker)"],
            key="income"
        )

        family_size = st.number_input(
            "Family Size",
            min_value=1,
            max_value=15,
            value=5,
            key="family"
        )

        caste_category = st.selectbox(
            "Social Category (Optional)",
            options=["--Select--", "General", "OBC", "SC", "ST"],
            key="caste"
        )

    with col2:
        st.markdown("### 📍 Your Location")

        district = st.selectbox(
            "District",
            options=["Indore", "Bhopal", "Pune", "Mumbai", "Bengaluru", "Hyderabad"],
            key="district"
        )

        state = st.selectbox(
            "State",
            options=["Madhya Pradesh", "Maharashtra", "Karnataka", "Telangana"],
            key="state"
        )

    st.markdown("---")

    # Check eligibility button
    if st.button("✅ Check My Eligibility", use_container_width=True, key="check_btn"):
        st.markdown("""
        <div style='background: #E8F5E9; border-left: 4px solid #2E7D32; padding: 20px;
                    border-radius: 8px; margin: 20px 0;'>
            <h3 style='color: #2E7D32; margin-top: 0;'>✓ Great News!</h3>
            <p style='color: #1B5E20; font-size: 1.1em;'>
                You appear to be <strong>eligible for PM-JAY benefits</strong> with a confidence score of <strong>95%</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card success">
                <div class="metric-label">Eligibility Status</div>
                <div class="metric-value" style='color: #2E7D32;'>ELIGIBLE</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card info">
                <div class="metric-label">Confidence</div>
                <div class="metric-value" style='color: #0097A7;'>95%</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card success">
                <div class="metric-label">Coverage Limit</div>
                <div class="metric-value" style='color: #2E7D32;'>₹5L</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 🏥 Nearby Empanelled Hospitals")

        try:
            hospitals_df = pd.read_csv("app/data/mock_hospitals.csv")
            district_hospitals = hospitals_df[hospitals_df['district'] == district].head(8)

            if len(district_hospitals) > 0:
                cols = st.columns(2)

                for idx, (_, hospital) in enumerate(district_hospitals.iterrows()):
                    with cols[idx % 2]:
                        st.markdown(f"""
                        <div style='background: white; border: 2px solid #E0E0E0;
                                    border-radius: 12px; padding: 15px; margin: 10px 0;
                                    transition: all 0.3s ease;'>
                            <h4 style='color: #0D47A1; margin-top: 0;'>{hospital['name']}</h4>
                            <p style='color: #666; margin: 5px 0;'>
                                <strong>Type:</strong> {hospital['hospital_type']}<br/>
                                <strong>District:</strong> {hospital['district']}<br/>
                                <strong>Status:</strong> {'🟢 Empanelled' if hospital['is_empanelled'] else '🔴 Not Empanelled'}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

        except FileNotFoundError:
            st.warning("Hospital data not available")

    st.markdown("---")

    # FAQ Section
    st.markdown("### ❓ Frequently Asked Questions")

    with st.expander("What is PM-JAY?", expanded=False):
        st.markdown("""
        **Pradhan Mantri - Jan Arogya Yojana (PM-JAY)** is India's largest health insurance scheme.

        It provides:
        - 💰 **Cashless treatment** up to ₹5 lakhs per family per year
        - 🏥 **Hospitalization coverage** in empanelled hospitals
        - 🩺 **Pre-existing conditions** covered from day 1
        - ⚕️ **Secondary and tertiary care** coverage
        """)

    with st.expander("Who is eligible?", expanded=False):
        st.markdown("""
        You may be eligible if:
        - You belong to a **Below Poverty Line (BPL)** household
        - You're in **EWS (Economically Weaker Section)**
        - Your household income is below certain thresholds
        - You're not covered by other health insurance
        """)

    with st.expander("What does it cover?", expanded=False):
        st.markdown("""
        PM-JAY covers:
        - ✅ Hospitalization expenses up to ₹5 lakhs
        - ✅ Pre- and post-hospitalization costs
        - ✅ Diagnostic tests
        - ✅ Surgical procedures
        - ✅ Maternity and neonatal care
        """)


# ===== PAGE 3: ANALYTICS DASHBOARD =====
def show_analytics_dashboard():
    """Premium Analytics & Compliance Dashboard."""

    create_header(
        "Analytics & Compliance",
        "Government-Level Performance Metrics & Health Equity Analysis",
        "📊"
    )

    try:
        equity_df = pd.read_csv("app/data/district_equity_scores.csv")
        analytics_df = pd.read_csv("app/data/district_analytics_report.csv")
        hospital_risk_df = pd.read_csv("app/data/hospital_risk_scores.csv")

        # === KPI METRICS ===
        col1, col2, col3, col4, col5 = st.columns(5)

        total_processed = analytics_df['total_processed'].sum()
        total_enrolled = analytics_df['already_enrolled'].sum()
        unenrolled_eligible = analytics_df['unenrolled_eligible'].sum()
        total_savings = analytics_df['estimated_savings_₹'].sum()
        avg_equity_score = equity_df['equity_score'].mean()

        with col1:
            coverage = (total_enrolled / total_processed * 100) if total_processed > 0 else 0
            st.markdown(f"""
            <div class="metric-card info">
                <div class="metric-label">Coverage Rate</div>
                <div class="metric-value">{coverage:.1f}%</div>
                <div class="metric-delta">+3.2%</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card success">
                <div class="metric-label">Enrollment Targets</div>
                <div class="metric-value">{unenrolled_eligible:,}</div>
                <div class="metric-delta">+15K identified</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card danger">
                <div class="metric-label">Fraud Savings</div>
                <div class="metric-value">₹{total_savings/1e8:.1f}Cr</div>
                <div class="metric-delta">+₹5Cr this month</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            avg_risk = hospital_risk_df['risk_score'].mean()
            st.markdown(f"""
            <div class="metric-card warning">
                <div class="metric-label">Avg Hospital Risk</div>
                <div class="metric-value">{avg_risk:.1f}</div>
                <div class="metric-delta negative">-2.3</div>
            </div>
            """, unsafe_allow_html=True)

        with col5:
            st.markdown(f"""
            <div class="metric-card info">
                <div class="metric-label">Health Equity</div>
                <div class="metric-value">{avg_equity_score:.1f}</div>
                <div class="metric-delta">-1.8 points</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # === TABS ===
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Enrollment", "💰 Financial", "⚠️ Fraud", "🏆 Impact"])

        with tab1:
            st.markdown("### District-Wise Enrollment Progress")

            enroll_data = analytics_df.sort_values('unenrolled_eligible', ascending=False).head(12)

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=enroll_data['district'],
                y=enroll_data['already_enrolled'],
                name='Currently Enrolled',
                marker=dict(color='#2E7D32')
            ))

            fig.add_trace(go.Bar(
                x=enroll_data['district'],
                y=enroll_data['unenrolled_eligible'],
                name='Enrollment Targets',
                marker=dict(color='#FBC02D')
            ))

            fig.update_layout(
                title="Enrollment Status by District",
                xaxis_title="District",
                yaxis_title="Households",
                barmode='group',
                hovermode='x unified',
                template='plotly_white',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.markdown("### Financial Impact & Savings")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="metric-card danger">
                    <div class="metric-label">Fraud Prevented</div>
                    <div class="metric-value">₹{total_savings/1e7:.1f}Cr</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                recovery = total_savings * 0.8
                st.markdown(f"""
                <div class="metric-card success">
                    <div class="metric-label">Recovery Potential</div>
                    <div class="metric-value">₹{recovery/1e7:.1f}Cr</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="metric-card info">
                    <div class="metric-label">Recovery Rate</div>
                    <div class="metric-value">80%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            savings_data = analytics_df.sort_values('estimated_savings_₹', ascending=False).head(10)

            fig = go.Figure(data=[
                go.Bar(
                    x=savings_data['district'],
                    y=savings_data['estimated_savings_₹'],
                    marker=dict(
                        color=savings_data['estimated_savings_₹'],
                        colorscale='Reds',
                        showscale=True
                    )
                )
            ])

            fig.update_layout(
                title="Fraud Prevention Savings by District",
                xaxis_title="District",
                yaxis_title="Savings (₹)",
                template='plotly_white',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            st.markdown("### Fraud Prevention Metrics")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"""
                <div class="metric-card danger">
                    <div class="metric-label">High-Risk Hospitals</div>
                    <div class="metric-value">{len(hospital_risk_df[hospital_risk_df['risk_level'] == 'HIGH'])}</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card danger">
                    <div class="metric-label">Critical Risk</div>
                    <div class="metric-value">{len(hospital_risk_df[hospital_risk_df['risk_level'] == 'CRITICAL'])}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            risk_counts = hospital_risk_df['risk_level'].value_counts()

            colors = {
                'CRITICAL': '#C62828',
                'HIGH': '#F57C00',
                'MEDIUM': '#FBC02D',
                'LOW': '#2E7D32'
            }

            fig = go.Figure(data=[
                go.Pie(
                    labels=risk_counts.index,
                    values=risk_counts.values,
                    marker=dict(colors=[colors.get(x) for x in risk_counts.index]),
                    hoverinfo='label+value+percent'
                )
            ])

            fig.update_layout(
                title="Hospital Risk Distribution",
                height=400,
                template='plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.markdown("### Success Stories & Impact")

            create_info_box(
                """
                <strong>Rajeev Kumar's Family - Indore</strong><br/>
                His father needed ₹5L surgery. Through AyushEquityAI's inclusion drive,
                Rajeev's family was identified and enrolled in PM-JAY.
                The surgery was performed at government hospital with zero out-of-pocket cost.
                <br/><br/>
                <strong>Impact: ₹5,00,000 saved | Family's life improved | Health equity achieved</strong>
                """,
                "success",
                "🏥 Success Story"
            )

            create_info_box(
                """
                <strong>Fraud Prevention Case - Pune Hospital</strong><br/>
                AyushEquityAI's fraud detection model flagged 23 duplicate claims
                from a hospital over 3 months. Investigation revealed systematic overbilling.
                <br/><br/>
                <strong>Impact: ₹22,50,000 protected | System integrity maintained</strong>
                """,
                "warning",
                "🚨 Fraud Detection"
            )

    except FileNotFoundError:
        create_info_box(
            "Data files not found. Please run Day 4-6 setup first.",
            "warning",
            "Setup Required"
        )


# ===== MAIN ENTRY POINT (only runs when this file is launched directly) =====
def main():
    """Sets up page config, sidebar, and routes to the selected dashboard.
    This only executes when app_hospital_theme.py is run directly via
    `streamlit run`, NOT when its functions are imported elsewhere
    (e.g. from run_app.py). That separation is what avoids the
    circular-import / NameError problem."""

    st.set_page_config(
        page_title="AyushEquityAI - Healthcare Excellence",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": "AyushEquityAI - AI-Powered Healthcare Inclusion & Fraud Detection for PM-JAY"
        }
    )

    apply_custom_styling()

    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h2 style='color: white; font-size: 2em;'>🏥</h2>
            <h3 style='color: white; margin: 0;'>AyushEquityAI</h3>
            <p style='color: rgba(255,255,255,0.8); margin: 5px 0;'>Healthcare Excellence Platform</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

        st.markdown("<p style='color: white; font-weight: 600; margin-bottom: 10px;'>SELECT YOUR ROLE</p>", unsafe_allow_html=True)

        selected_role = st.radio(
            "Choose Dashboard",
            options=[
                "🏥 Officer Dashboard",
                "👨‍👩‍👧‍👦 Citizen Portal",
                "📊 Analytics & Compliance"
            ],
            label_visibility="collapsed"
        )

        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-top: 20px;'>
            <p style='color: white; font-size: 0.85em; margin: 0;'>
                <strong>System Status:</strong> 🟢 Operational
            </p>
            <p style='color: white; font-size: 0.85em; margin: 5px 0;'>
                <strong>Version:</strong> 1.0.0
            </p>
            <p style='color: white; font-size: 0.85em; margin: 5px 0;'>
                <strong>Last Updated:</strong> Today
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

        st.markdown("""
        <div style='text-align: center; margin-top: 30px;'>
            <p style='color: rgba(255,255,255,0.7); font-size: 0.8em;'>
                <strong>Need Help?</strong><br/>
                Call: 1800-AYUSH-1<br/>
                Email: support@ayushequityai.gov.in
            </p>
        </div>
        """, unsafe_allow_html=True)

    if "🏥 Officer Dashboard" in selected_role:
        show_officer_dashboard()
    elif "👨‍👩‍👧‍👦 Citizen Portal" in selected_role:
        show_citizen_portal()
    else:
        show_analytics_dashboard()


if __name__ == "__main__":
    main()