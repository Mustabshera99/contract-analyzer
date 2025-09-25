"""
Analytics dashboard component for advanced contract analysis features.
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from frontend.utils.api_client import APIClient


class AnalyticsDashboard:
    """Analytics dashboard for contract analysis insights."""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_client = APIClient(self.base_url)

    def render_risk_trends(self):
        """Render risk trend analysis."""
        st.subheader("📈 Risk Trend Analysis")

        col1, col2 = st.columns(2)
        with col1:
            time_period = st.selectbox(
                "Time Period",
                ["7d", "30d", "90d", "180d"],
                index=1,
                key="risk_trend_period",
            )
        with col2:
            contract_types = st.multiselect(
                "Contract Types",
                ["Service Agreement", "Employment Contract", "NDA", "Vendor Agreement"],
                key="risk_trend_types",
            )

        if st.button("📊 Analyze Risk Trends", key="analyze_risk_trends"):
            with st.spinner("Analyzing risk trends..."):
                try:
                    data = self.api_client._make_request(
                        "GET",
                        "/api/v1/analytics/risk-trends",
                        params={
                            "time_period": time_period,
                            "contract_types": contract_types,
                        },
                    )

                    if "error" in data:
                        st.error(f"Failed to fetch risk trends: {data['error']}")
                    else:
                        self._display_risk_trends(data)

                except Exception as e:
                    st.error(f"Error analyzing risk trends: {e}")

    def render_contract_comparison(self):
        """Render contract comparison interface."""
        st.subheader("🔍 Contract Comparison")

        col1, col2 = st.columns(2)
        with col1:
            contract_1_id = st.text_input("Contract 1 ID", key="compare_contract_1")
        with col2:
            contract_2_id = st.text_input("Contract 2 ID", key="compare_contract_2")

        comparison_type = st.selectbox(
            "Comparison Type",
            ["comprehensive", "risk_only", "clause_only"],
            key="comparison_type",
        )

        if st.button("🔄 Compare Contracts", key="compare_contracts"):
            if not contract_1_id or not contract_2_id:
                st.warning("Please enter both contract IDs")
                return

            with st.spinner("Comparing contracts..."):
                try:
                    data = self.api_client._make_request(
                        "GET",
                        "/api/v1/analytics/contract-comparison",
                        params={
                            "contract_1_id": contract_1_id,
                            "contract_2_id": contract_2_id,
                            "comparison_type": comparison_type,
                        },
                    )

                    if "error" in data:
                        st.error(f"Failed to compare contracts: {data['error']}")
                    else:
                        self._display_contract_comparison(data)

                except Exception as e:
                    st.error(f"Error comparing contracts: {e}")

    def render_compliance_check(self):
        """Render compliance checking interface."""
        st.subheader("✅ Compliance Check")

        contract_id = st.text_input("Contract ID", key="compliance_contract_id")

        col1, col2 = st.columns(2)
        with col1:
            regulatory_framework = st.selectbox(
                "Regulatory Framework",
                ["general", "gdpr", "sox", "hipaa", "pci_dss"],
                key="regulatory_framework",
            )
        with col2:
            if st.button("🔍 Check Compliance", key="check_compliance"):
                if not contract_id:
                    st.warning("Please enter a contract ID")
                    return

                with st.spinner("Checking compliance..."):
                    try:
                        data = self.api_client._make_request(
                            "GET",
                            "/api/v1/analytics/compliance-check",
                            params={
                                "contract_id": contract_id,
                                "regulatory_framework": regulatory_framework,
                            },
                        )

                        if "error" in data:
                            st.error(f"Failed to check compliance: {data['error']}")
                        else:
                            self._display_compliance_results(data)

                    except Exception as e:
                        st.error(f"Error checking compliance: {e}")

    def render_cost_analysis(self):
        """Render cost analysis interface."""
        st.subheader("💰 Cost Analysis")

        col1, col2 = st.columns(2)
        with col1:
            time_period = st.selectbox(
                "Time Period", ["7d", "30d", "90d"], index=1, key="cost_period"
            )
        with col2:
            breakdown_by = st.selectbox(
                "Breakdown By", ["model", "user", "analysis_type"], key="cost_breakdown"
            )

        if st.button("📊 Analyze Costs", key="analyze_costs"):
            with st.spinner("Analyzing costs..."):
                try:
                    data = self.api_client._make_request(
                        "GET",
                        "/api/v1/analytics/cost-analysis",
                        params={
                            "time_period": time_period,
                            "breakdown_by": breakdown_by,
                        },
                    )

                    if "error" in data:
                        st.error(f"Failed to analyze costs: {data['error']}")
                    else:
                        self._display_cost_analysis(data)

                except Exception as e:
                    st.error(f"Error analyzing costs: {e}")

    def render_performance_metrics(self):
        """Render performance metrics."""
        st.subheader("⚡ Performance Metrics")

        time_period = st.selectbox(
            "Time Period", ["1d", "7d", "30d"], index=1, key="perf_period"
        )

        if st.button("📊 Get Performance Metrics", key="get_performance"):
            with st.spinner("Fetching performance metrics..."):
                try:
                    data = self.api_client._make_request(
                        "GET",
                        "/api/v1/analytics/performance-metrics",
                        params={"time_period": time_period},
                    )

                    if "error" in data:
                        st.error(
                            f"Failed to fetch performance metrics: {data['error']}"
                        )
                    else:
                        self._display_performance_metrics(data)

                except Exception as e:
                    st.error(f"Error fetching performance metrics: {e}")

    def render_dashboard_overview(self):
        """Render complete dashboard overview."""
        st.subheader("📊 Analytics Dashboard")

        if st.button("🔄 Refresh Dashboard", key="refresh_dashboard"):
            with st.spinner("Loading dashboard data..."):
                try:
                    data = self.api_client._make_request(
                        "GET",
                        "/api/v1/analytics/dashboard",
                        params={"time_period": "30d"},
                    )

                    if "error" in data:
                        st.error(f"Failed to load dashboard: {data['error']}")
                    else:
                        self._display_dashboard_overview(data)

                except Exception as e:
                    st.error(f"Error loading dashboard: {e}")

    def _display_risk_trends(self, data: Dict[str, Any]):
        """Display risk trend analysis results."""
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Average Risk Score", f"{data['average_risk_score']:.1f}")
        with col2:
            st.metric("Total Analyses", data["risk_count"])
        with col3:
            st.metric("High Risk %", f"{data['high_risk_percentage']:.1f}%")
        with col4:
            trend_emoji = {
                "increasing": "📈",
                "decreasing": "📉",
                "stable": "➡️",
                "volatile": "📊",
            }
            st.metric(
                "Trend",
                f"{trend_emoji.get(data['trend'], '❓')} {data['trend'].title()}",
            )

        # Display confidence
        confidence_color = (
            "green"
            if data["confidence"] > 0.8
            else "orange" if data["confidence"] > 0.6 else "red"
        )
        st.markdown(f"**Confidence:** :{confidence_color}[{data['confidence']:.2f}]")

    def _display_contract_comparison(self, data: Dict[str, Any]):
        """Display contract comparison results."""
        st.subheader("Comparison Results")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Similarity Score", f"{data['similarity_score']:.2f}")
        with col2:
            st.metric("Risk Differences", len(data["risk_differences"]))

        # Display risk differences
        if data["risk_differences"]:
            st.subheader("Risk Differences")
            for i, diff in enumerate(data["risk_differences"]):
                with st.expander(
                    f"Difference {i + 1}: {diff.get('clause_type', 'Unknown')}"
                ):
                    st.write(
                        f"**Contract 1 Risk:** {diff.get('contract_1_risk', 'N/A')}"
                    )
                    st.write(
                        f"**Contract 2 Risk:** {diff.get('contract_2_risk', 'N/A')}"
                    )
                    st.write(f"**Difference:** {diff.get('difference', 'N/A')}")

        # Display recommendations
        if data["recommendations"]:
            st.subheader("Recommendations")
            for rec in data["recommendations"]:
                st.info(f"💡 {rec}")

    def _display_compliance_results(self, data: Dict[str, Any]):
        """Display compliance check results."""
        st.subheader("Compliance Results")

        # Compliance score with color coding
        score = data["compliance_score"]
        if score >= 90:
            color = "green"
            emoji = "✅"
        elif score >= 70:
            color = "orange"
            emoji = "⚠️"
        else:
            color = "red"
            emoji = "❌"

        st.markdown(f"**Compliance Score:** :{color}[{emoji} {score:.1f}%]")
        st.markdown(f"**Framework:** {data['regulatory_framework'].upper()}")

        # Display violations
        if data["violations"]:
            st.subheader("Violations Found")
            for i, violation in enumerate(data["violations"]):
                with st.expander(
                    f"Violation {i + 1}: {violation.get('rule_id', 'Unknown')}"
                ):
                    st.write(f"**Description:** {violation.get('description', 'N/A')}")
                    st.write(f"**Severity:** {violation.get('severity', 'N/A')}")

        # Display recommendations
        if data["recommendations"]:
            st.subheader("Recommendations")
            for rec in data["recommendations"]:
                st.info(f"💡 {rec}")

    def _display_cost_analysis(self, data: Dict[str, Any]):
        """Display cost analysis results."""
        st.subheader("Cost Analysis Results")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Cost", f"${data['total_cost']:.2f}")
        with col2:
            st.metric("Period", data["period"])

        # Display breakdown
        if data["breakdown"]:
            st.subheader("Cost Breakdown")
            breakdown_df = pd.DataFrame(
                list(data["breakdown"].items()), columns=["Category", "Cost"]
            )

            # Create pie chart
            fig = px.pie(
                breakdown_df, values="Cost", names="Category", title="Cost Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display table
            st.dataframe(breakdown_df)

        # Display trends
        if "trends" in data:
            trends = data["trends"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Daily Average", f"${trends.get('daily_average', 0):.2f}")
            with col2:
                st.metric("Trend", trends.get("trend", "N/A"))
            with col3:
                peak_day = trends.get("peak_day")
                if peak_day:
                    st.metric("Peak Day", peak_day.split("T")[0])

    def _display_performance_metrics(self, data: Dict[str, Any]):
        """Display performance metrics."""
        st.subheader("Performance Metrics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Avg Processing Time", f"{data.get('average_processing_time', 0):.1f}s"
            )
        with col2:
            st.metric("Success Rate", f"{data.get('success_rate', 0):.1f}%")
        with col3:
            st.metric("Avg Confidence", f"{data.get('average_confidence', 0):.2f}")
        with col4:
            st.metric("Throughput/Hour", f"{data.get('throughput_per_hour', 0):.1f}")

        # Additional metrics
        st.metric("Total Analyses", data.get("total_analyses", 0))

    def _display_dashboard_overview(self, data: Dict[str, Any]):
        """Display complete dashboard overview."""
        st.subheader("Dashboard Overview")

        # Risk trends section
        if "risk_trends" in data:
            risk_data = data["risk_trends"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Risk Score", f"{risk_data['average_risk_score']:.1f}")
            with col2:
                st.metric("Total Analyses", risk_data["risk_count"])
            with col3:
                st.metric("High Risk %", f"{risk_data['high_risk_percentage']:.1f}%")

        # Performance section
        if "performance_metrics" in data:
            perf_data = data["performance_metrics"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Success Rate", f"{perf_data.get('success_rate', 0):.1f}%")
            with col2:
                st.metric(
                    "Avg Processing Time",
                    f"{perf_data.get('average_processing_time', 0):.1f}s",
                )
            with col3:
                st.metric(
                    "Throughput/Hour", f"{perf_data.get('throughput_per_hour', 0):.1f}"
                )

        # Cost section
        if "cost_analysis" in data:
            cost_data = data["cost_analysis"]
            st.metric("Total Cost", f"${cost_data.get('total_cost', 0):.2f}")


def render_analytics_dashboard():
    """Render the complete analytics dashboard."""
    dashboard = AnalyticsDashboard()

    # Create tabs for different analytics features
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📊 Overview",
            "📈 Risk Trends",
            "🔍 Contract Comparison",
            "✅ Compliance",
            "💰 Costs",
            "⚡ Performance",
        ]
    )

    with tab1:
        dashboard.render_dashboard_overview()

    with tab2:
        dashboard.render_risk_trends()

    with tab3:
        dashboard.render_contract_comparison()

    with tab4:
        dashboard.render_compliance_check()

    with tab5:
        dashboard.render_cost_analysis()

    with tab6:
        dashboard.render_performance_metrics()
