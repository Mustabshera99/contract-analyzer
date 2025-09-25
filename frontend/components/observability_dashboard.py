"""
Observability Dashboard Component for LangSmith and AI Operations Monitoring.
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


class ObservabilityDashboard:
    """Observability dashboard for AI operations and LangSmith monitoring."""

    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_client = APIClient(self.base_url)

    def render_langsmith_health(self):
        """Render LangSmith health status."""
        st.subheader("🔍 AI Operations Health Status")

        if st.button("🔄 Refresh Health Status", key="refresh_langsmith_health"):
            with st.spinner("Checking AI operations health..."):
                try:
                    data = self.api_client._make_request(
                        "GET", "/api/v1/monitoring/observability/health"
                    )

                    if "error" in data:
                        st.error(f"Failed to get AI operations health: {data['error']}")
                    else:
                        self._display_ai_operations_health(data)

                except Exception as e:
                    st.error(f"Error checking AI operations health: {e}")

    def render_langsmith_metrics(self):
        """Render LangSmith metrics."""
        st.subheader("📊 LangSmith Metrics")

        col1, col2 = st.columns(2)
        with col1:
            hours = st.selectbox(
                "Time Period", [1, 6, 12, 24, 48, 72], index=3, key="langsmith_hours"
            )
        with col2:
            if st.button("📈 Load Metrics", key="load_langsmith_metrics"):
                with st.spinner("Loading LangSmith metrics..."):
                    try:
                        data = self.api_client._make_request(
                            "GET", f"/api/v1/monitoring/langsmith/metrics?hours={hours}"
                        )

                        if "error" in data:
                            st.error(
                                f"Failed to get LangSmith metrics: {data['error']}"
                            )
                        else:
                            self._display_langsmith_metrics(data)

                    except Exception as e:
                        st.error(f"Error loading LangSmith metrics: {e}")

    def render_ai_performance(self):
        """Render AI performance metrics."""
        st.subheader("⚡ AI Performance Metrics")

        col1, col2 = st.columns(2)
        with col1:
            hours = st.selectbox(
                "Time Period", [1, 6, 12, 24, 48, 72], index=3, key="performance_hours"
            )
        with col2:
            if st.button("🚀 Load Performance", key="load_performance"):
                with st.spinner("Loading performance metrics..."):
                    try:
                        data = self.api_client._make_request(
                            "GET",
                            f"/api/v1/monitoring/observability/performance?hours={hours}",
                        )

                        if "error" in data:
                            st.error(
                                f"Failed to get performance metrics: {data['error']}"
                            )
                        else:
                            self._display_comprehensive_performance(data)

                    except Exception as e:
                        st.error(f"Error loading performance metrics: {e}")

    def render_cost_analysis(self):
        """Render cost analysis."""
        st.subheader("💰 Cost Analysis")

        col1, col2 = st.columns(2)
        with col1:
            hours = st.selectbox(
                "Time Period", [1, 6, 12, 24, 48, 72], index=3, key="cost_hours"
            )
        with col2:
            if st.button("💸 Load Cost Analysis", key="load_cost_analysis"):
                with st.spinner("Loading cost analysis..."):
                    try:
                        data = self.api_client._make_request(
                            "GET",
                            f"/api/v1/monitoring/observability/costs?hours={hours}",
                        )

                        if "error" in data:
                            st.error(f"Failed to get cost analysis: {data['error']}")
                        else:
                            self._display_comprehensive_costs(data)

                    except Exception as e:
                        st.error(f"Error loading cost analysis: {e}")

    def render_error_analysis(self):
        """Render error analysis."""
        st.subheader("🚨 Error Analysis")

        col1, col2 = st.columns(2)
        with col1:
            hours = st.selectbox(
                "Time Period", [1, 6, 12, 24, 48, 72], index=3, key="error_hours"
            )
        with col2:
            if st.button("🔍 Load Error Analysis", key="load_error_analysis"):
                with st.spinner("Loading error analysis..."):
                    try:
                        data = self.api_client._make_request(
                            "GET",
                            f"/api/v1/monitoring/observability/errors?hours={hours}",
                        )

                        if "error" in data:
                            st.error(f"Failed to get error analysis: {data['error']}")
                        else:
                            self._display_comprehensive_errors(data)

                    except Exception as e:
                        st.error(f"Error loading error analysis: {e}")

    def _display_ai_operations_health(self, data: Dict[str, Any]):
        """Display AI operations health status."""
        overall_health = data.get("overall_health", "unknown")
        langsmith = data.get("langsmith", {})
        ai_operations = data.get("ai_operations", {})
        config = data.get("config", {})

        # Overall health status
        if overall_health == "healthy":
            st.success("✅ AI Operations are healthy and operational")
        elif overall_health == "degraded":
            st.warning("⚠️ AI Operations are partially operational")
        elif overall_health == "partial":
            st.warning("⚠️ Some AI operations are disabled")
        else:
            st.error("❌ AI Operations are not healthy")

        # LangSmith status
        st.subheader("🔍 LangSmith Status")
        langsmith_status = langsmith.get("status", "unknown")
        langsmith_enabled = langsmith.get("enabled", False)

        if langsmith_enabled:
            if langsmith_status == "healthy":
                st.success("✅ LangSmith is connected and healthy")
            elif langsmith_status == "degraded":
                st.warning("⚠️ LangSmith is partially operational")
            else:
                st.error("❌ LangSmith is not healthy")
        else:
            st.info("ℹ️ LangSmith is disabled")

        # AI Operations status
        st.subheader("🤖 AI Operations Status")
        ai_status = ai_operations.get("status", "unknown")
        ai_enabled = ai_operations.get("enabled", False)

        if ai_enabled:
            if ai_status == "healthy":
                st.success("✅ AI Operations are healthy")
            elif ai_status == "degraded":
                st.warning("⚠️ AI Operations are partially operational")
            else:
                st.error("❌ AI Operations are not healthy")
        else:
            st.info("ℹ️ AI Operations are disabled")

        # Configuration details
        st.subheader("⚙️ Configuration")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("LangSmith Enabled", "Yes" if langsmith_enabled else "No")
            st.metric("AI Operations Enabled", "Yes" if ai_enabled else "No")

        with col2:
            st.metric("Overall Health", overall_health.title())
            st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

    def _display_langsmith_metrics(self, data: Dict[str, Any]):
        """Display LangSmith metrics."""
        metrics = data.get("metrics", {})
        performance = metrics.get("performance", {})
        costs = metrics.get("costs", {})
        errors = metrics.get("errors", {})

        # Performance metrics
        st.subheader("⚡ Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Runs", performance.get("total_runs", 0))
        with col2:
            st.metric("Avg Duration", f"{performance.get('avg_duration', 0):.2f}s")
        with col3:
            st.metric("Success Rate", f"{performance.get('success_rate', 0):.1f}%")
        with col4:
            st.metric("Error Rate", f"{performance.get('error_rate', 0):.1f}%")

        # Cost metrics
        st.subheader("💰 Cost Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Cost", f"${costs.get('total_cost', 0):.4f}")
        with col2:
            st.metric("Avg Cost per Run", f"${costs.get('avg_cost_per_run', 0):.4f}")
        with col3:
            st.metric("Token Usage", f"{costs.get('total_tokens', 0):,}")
        with col4:
            st.metric("Cost per Token", f"${costs.get('cost_per_token', 0):.6f}")

        # Error metrics
        st.subheader("🚨 Error Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Errors", errors.get("total_errors", 0))
        with col2:
            st.metric("Error Rate", f"{errors.get('error_rate', 0):.1f}%")
        with col3:
            st.metric("Critical Errors", errors.get("critical_errors", 0))
        with col4:
            st.metric("Recovery Rate", f"{errors.get('recovery_rate', 0):.1f}%")

    def _display_comprehensive_performance(self, data: Dict[str, Any]):
        """Display comprehensive performance metrics."""
        performance = data.get("performance", {})
        trends = data.get("trends", {})
        models = data.get("models", {})

        # Key performance indicators
        st.subheader("📊 Key Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Operations", performance.get("total_operations", 0))
        with col2:
            st.metric(
                "Avg Response Time", f"{performance.get('avg_response_time', 0):.2f}s"
            )
        with col3:
            st.metric("Throughput", f"{performance.get('throughput', 0):.1f} ops/min")
        with col4:
            st.metric("Success Rate", f"{performance.get('success_rate', 0):.1f}%")

        # Performance trends
        if trends.get("response_times"):
            st.subheader("📈 Response Time Trends")
            df = pd.DataFrame(trends["response_times"])
            fig = px.line(
                df, x="timestamp", y="response_time", title="Response Time Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Model performance comparison
        if models:
            st.subheader("🤖 Model Performance Comparison")
            model_data = []
            for model_name, model_stats in models.items():
                model_data.append(
                    {
                        "Model": model_name,
                        "Avg Response Time": model_stats.get("avg_response_time", 0),
                        "Success Rate": model_stats.get("success_rate", 0),
                        "Total Operations": model_stats.get("total_operations", 0),
                    }
                )

            if model_data:
                df = pd.DataFrame(model_data)
                fig = px.bar(
                    df,
                    x="Model",
                    y="Avg Response Time",
                    title="Average Response Time by Model",
                )
                st.plotly_chart(fig, use_container_width=True)

    def _display_comprehensive_costs(self, data: Dict[str, Any]):
        """Display comprehensive cost analysis."""
        costs = data.get("costs", {})
        trends = data.get("trends", {})
        models = data.get("models", {})

        # Cost summary
        st.subheader("💰 Cost Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Cost", f"${costs.get('total_cost', 0):.4f}")
        with col2:
            st.metric("Daily Cost", f"${costs.get('daily_cost', 0):.4f}")
        with col3:
            st.metric(
                "Avg Cost per Operation",
                f"${costs.get('avg_cost_per_operation', 0):.6f}",
            )
        with col4:
            st.metric("Cost Efficiency", f"{costs.get('cost_efficiency', 0):.1f}%")

        # Cost trends
        if trends.get("costs"):
            st.subheader("📈 Cost Trends")
            df = pd.DataFrame(trends["costs"])
            fig = px.line(df, x="timestamp", y="cost", title="Cost Over Time")
            st.plotly_chart(fig, use_container_width=True)

        # Model cost comparison
        if models:
            st.subheader("🤖 Cost by Model")
            model_data = []
            for model_name, model_stats in models.items():
                model_data.append(
                    {
                        "Model": model_name,
                        "Total Cost": model_stats.get("total_cost", 0),
                        "Avg Cost per Operation": model_stats.get(
                            "avg_cost_per_operation", 0
                        ),
                        "Operations": model_stats.get("operations", 0),
                    }
                )

            if model_data:
                df = pd.DataFrame(model_data)
                fig = px.bar(df, x="Model", y="Total Cost", title="Total Cost by Model")
                st.plotly_chart(fig, use_container_width=True)

    def _display_comprehensive_errors(self, data: Dict[str, Any]):
        """Display comprehensive error analysis."""
        errors = data.get("errors", {})
        trends = data.get("trends", {})
        error_types = data.get("error_types", {})

        # Error summary
        st.subheader("🚨 Error Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Errors", errors.get("total_errors", 0))
        with col2:
            st.metric("Error Rate", f"{errors.get('error_rate', 0):.1f}%")
        with col3:
            st.metric("Critical Errors", errors.get("critical_errors", 0))
        with col4:
            st.metric("Recovery Rate", f"{errors.get('recovery_rate', 0):.1f}%")

        # Error trends
        if trends.get("errors"):
            st.subheader("📈 Error Trends")
            df = pd.DataFrame(trends["errors"])
            fig = px.line(df, x="timestamp", y="error_count", title="Errors Over Time")
            st.plotly_chart(fig, use_container_width=True)

        # Error types breakdown
        if error_types:
            st.subheader("🔍 Error Types Breakdown")
            error_data = []
            for error_type, count in error_types.items():
                error_data.append({"Error Type": error_type, "Count": count})

            if error_data:
                df = pd.DataFrame(error_data)
                fig = px.pie(
                    df,
                    values="Count",
                    names="Error Type",
                    title="Error Types Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)

        # Recent errors
        recent_errors = data.get("recent_errors", [])
        if recent_errors:
            st.subheader("🕐 Recent Errors")
            for error in recent_errors[:10]:  # Show last 10 errors
                with st.expander(f"Error at {error.get('timestamp', 'Unknown time')}"):
                    st.code(error.get("message", "No message available"))
                    st.text(f"Type: {error.get('type', 'Unknown')}")
                    st.text(f"Severity: {error.get('severity', 'Unknown')}")


def render_observability_dashboard():
    """Render the complete observability dashboard."""
    st.title("🔍 Observability Dashboard")
    st.markdown("Monitor AI operations, performance, costs, and errors in real-time.")

    dashboard = ObservabilityDashboard()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "🏥 Health Status",
            "📊 LangSmith Metrics",
            "⚡ Performance",
            "💰 Costs",
            "🚨 Errors",
        ]
    )

    with tab1:
        dashboard.render_langsmith_health()

    with tab2:
        dashboard.render_langsmith_metrics()

    with tab3:
        dashboard.render_ai_performance()

    with tab4:
        dashboard.render_cost_analysis()

    with tab5:
        dashboard.render_error_analysis()
