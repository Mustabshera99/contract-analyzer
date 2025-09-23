"""
Enhanced results display component with expandable sections and rich formatting.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st


def format_risk_level(risk_level: str) -> str:
    """Format risk level with appropriate emoji and color."""
    risk_mapping = {
        "High": "🔴 High Risk",
        "Medium": "🟡 Medium Risk",
        "Low": "🟢 Low Risk",
    }
    return risk_mapping.get(risk_level, f"⚪ {risk_level}")


def display_risk_score(score: Optional[float]):
    """Display overall risk score with visual indicator."""
    if score is None:
        st.metric("Overall Risk Score", "N/A")
        return

    # Determine color based on score
    if score >= 7:
        color = "red"
        emoji = "🔴"
    elif score >= 4:
        color = "orange"
        emoji = "🟡"
    else:
        color = "green"
        emoji = "🟢"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall Risk Score", f"{score:.1f}/10")
    with col2:
        st.markdown(
            f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {color}20; border-left: 4px solid {color};">
            {emoji} Risk Level: {"High" if score >= 7 else "Medium" if score >= 4 else "Low"}
        </div>
        """,
            unsafe_allow_html=True,
        )


def display_risky_clauses(risky_clauses: List[Dict]):
    """Display risky clauses with detailed information."""
    if not risky_clauses:
        st.info("✅ No risky clauses identified in this contract.")
        return

    st.subheader(f"⚠️ Risky Clauses ({len(risky_clauses)} found)")

    # Summary statistics
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    for clause in risky_clauses:
        risk_level = clause.get("risk_level", "Unknown")
        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 High Risk", risk_counts["High"])
    with col2:
        st.metric("🟡 Medium Risk", risk_counts["Medium"])
    with col3:
        st.metric("🟢 Low Risk", risk_counts["Low"])

    # Display each clause
    for i, clause in enumerate(risky_clauses, 1):
        risk_level = clause.get("risk_level", "Unknown")
        clause_text = clause.get("clause_text", "")
        risk_explanation = clause.get("risk_explanation", "")
        precedent_reference = clause.get("precedent_reference")
        clause_index = clause.get("clause_index", i)

        with st.expander(
            f"{format_risk_level(risk_level)} - Clause {clause_index}", expanded=False
        ):
            # Clause text
            st.markdown("**📄 Clause Text:**")
            st.markdown(
                f'<div style="background-color: #f0f0f0; color: #333333; padding: 10px; border-radius: 5px; font-style: italic; border: 1px solid #cccccc;">{clause_text}</div>',
                unsafe_allow_html=True,
            )

            # Risk explanation
            st.markdown("**⚠️ Risk Analysis:**")
            st.write(risk_explanation)

            # Precedent reference if available
            if precedent_reference:
                st.markdown("**📚 Legal Precedent:**")
                st.info(precedent_reference)

            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 Copy Clause {clause_index}", key=f"copy_clause_{i}"):
                    st.write("Clause text copied to clipboard!")
            with col2:
                if st.button(
                    f"🔍 More Details {clause_index}", key=f"details_clause_{i}"
                ):
                    st.json(clause)


def display_redline_suggestions(redlines: List[Dict]):
    """Display redline suggestions with before/after comparison."""
    if not redlines:
        st.info("ℹ️ No redline suggestions generated.")
        return

    st.subheader(f"✏️ Redline Suggestions ({len(redlines)} suggestions)")

    for i, redline in enumerate(redlines, 1):
        original_clause = redline.get("original_clause", "")
        suggested_redline = redline.get("suggested_redline", "")
        risk_explanation = redline.get("risk_explanation", "")
        change_rationale = redline.get("change_rationale", "")
        clause_index = redline.get("clause_index", i)
        risk_mitigated = redline.get("risk_mitigated")

        with st.expander(f"✏️ Redline Suggestion {clause_index}", expanded=False):
            # Before/After comparison
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📄 Original Clause:**")
                st.markdown(
                    f'<div style="background-color: #ffebee; color: #333333; padding: 10px; border-radius: 5px; border-left: 4px solid #f44336; border: 1px solid #ffcdd2;">{original_clause}</div>',
                    unsafe_allow_html=True,
                )

            with col2:
                st.markdown("**✅ Suggested Redline:**")
                st.markdown(
                    f'<div style="background-color: #e8f5e8; color: #333333; padding: 10px; border-radius: 5px; border-left: 4px solid #4caf50; border: 1px solid #c8e6c9;">{suggested_redline}</div>',
                    unsafe_allow_html=True,
                )

            # Risk explanation
            st.markdown("**⚠️ Risk Being Addressed:**")
            st.write(risk_explanation)

            # Change rationale
            if change_rationale:
                st.markdown("**💡 Rationale for Change:**")
                st.write(change_rationale)

            # Risk mitigation status
            if risk_mitigated is not None:
                if risk_mitigated:
                    st.success(
                        "✅ This change effectively mitigates the identified risk"
                    )
                else:
                    st.warning(
                        "⚠️ This change partially addresses the risk - additional review recommended"
                    )

            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📋 Copy Original {clause_index}", key=f"copy_orig_{i}"):
                    st.write("Original clause copied!")
            with col2:
                if st.button(
                    f"📋 Copy Redline {clause_index}", key=f"copy_redline_{i}"
                ):
                    st.write("Redlined clause copied!")
            with col3:
                if st.button(f"📊 Compare {clause_index}", key=f"compare_{i}"):
                    # Show detailed comparison
                    st.markdown("**Detailed Comparison:**")
                    st.text_area(
                        "Original", original_clause, height=100, key=f"orig_text_{i}"
                    )
                    st.text_area(
                        "Suggested", suggested_redline, height=100, key=f"sugg_text_{i}"
                    )


def display_email_draft(email_draft: str):
    """Display email draft for negotiation."""
    if not email_draft:
        st.info("ℹ️ No email draft generated.")
        return

    st.subheader("📧 Negotiation Email Draft")

    with st.expander("📧 Email Content", expanded=True):
        st.markdown("**Generated Email:**")
        st.markdown(
            f'<div style="background-color: #f8f9fa; color: #333333; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; font-family: monospace;">{email_draft}</div>',
            unsafe_allow_html=True,
        )

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy Email", key="copy_email"):
                st.success("Email copied to clipboard!")
        with col2:
            if st.button("✏️ Edit Email", key="edit_email"):
                edited_email = st.text_area(
                    "Edit email content:", email_draft, height=200
                )
                if st.button("💾 Save Changes"):
                    st.session_state.edited_email = edited_email
                    st.success("Email updated!")
        with col3:
            if st.button("📤 Export Email", key="export_email"):
                st.download_button(
                    label="📥 Download as .txt",
                    data=email_draft,
                    file_name="negotiation_email.txt",
                    mime="text/plain",
                )


def display_analysis_metadata(analysis_data: Dict):
    """Display analysis metadata and processing information."""
    processing_time = analysis_data.get("processing_time")
    analysis_timestamp = analysis_data.get("analysis_timestamp")
    warnings = analysis_data.get("warnings", [])
    errors = analysis_data.get("errors", [])

    with st.expander("📊 Analysis Details", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            if processing_time:
                st.metric("⏱️ Processing Time", f"{processing_time:.2f}s")
            if analysis_timestamp:
                st.metric("📅 Analysis Date", analysis_timestamp)

        with col2:
            st.metric("⚠️ Warnings", len(warnings))
            st.metric("❌ Errors", len(errors))

        # Show warnings and errors
        if warnings:
            st.markdown("**⚠️ Warnings:**")
            for warning in warnings:
                st.warning(warning)

        if errors:
            st.markdown("**❌ Errors:**")
            for error in errors:
                st.error(error)


def export_results(analysis_results: Dict):
    """Provide export options for analysis results."""
    st.subheader("📤 Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        # JSON export
        json_data = json.dumps(analysis_results, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name="contract_analysis.json",
            mime="application/json",
        )

    with col2:
        # CSV export for risky clauses
        if analysis_results.get("risky_clauses"):
            df = pd.DataFrame(analysis_results["risky_clauses"])
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="risky_clauses.csv",
                mime="text/csv",
            )

    with col3:
        # Summary report
        summary = generate_summary_report(analysis_results)
        st.download_button(
            label="📥 Download Report",
            data=summary,
            file_name="analysis_report.txt",
            mime="text/plain",
        )


def generate_summary_report(analysis_results: Dict) -> str:
    """Generate a text summary report."""
    report = []
    report.append("CONTRACT RISK ANALYSIS REPORT")
    report.append("=" * 40)
    report.append("")

    # Overall risk score
    risk_score = analysis_results.get("overall_risk_score")
    if risk_score:
        report.append(f"Overall Risk Score: {risk_score:.1f}/10")
        report.append("")

    # Risky clauses summary
    risky_clauses = analysis_results.get("risky_clauses", [])
    report.append(f"Risky Clauses Found: {len(risky_clauses)}")

    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    for clause in risky_clauses:
        risk_level = clause.get("risk_level", "Unknown")
        if risk_level in risk_counts:
            risk_counts[risk_level] += 1

    report.append(f"  - High Risk: {risk_counts['High']}")
    report.append(f"  - Medium Risk: {risk_counts['Medium']}")
    report.append(f"  - Low Risk: {risk_counts['Low']}")
    report.append("")

    # Redlines summary
    redlines = analysis_results.get("suggested_redlines", [])
    report.append(f"Redline Suggestions: {len(redlines)}")
    report.append("")

    # Processing info
    processing_time = analysis_results.get("processing_time")
    if processing_time:
        report.append(f"Processing Time: {processing_time:.2f} seconds")

    timestamp = analysis_results.get("analysis_timestamp")
    if timestamp:
        report.append(f"Analysis Date: {timestamp}")

    return "\n".join(report)


def results_display(analysis_results: Dict[str, Any]):
    """
    Main results display function with comprehensive analysis presentation.

    Args:
        analysis_results: Dictionary containing analysis results
    """
    if not analysis_results:
        st.warning("No analysis results to display.")
        return

    st.header("📊 Contract Analysis Results")

    # Overall risk score
    risk_score = analysis_results.get("overall_risk_score")
    if risk_score is not None:
        display_risk_score(risk_score)
        st.divider()

    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["⚠️ Risky Clauses", "✏️ Redlines", "📧 Communication", "📊 Details"]
    )

    with tab1:
        risky_clauses = analysis_results.get("risky_clauses", [])
        display_risky_clauses(risky_clauses)

    with tab2:
        redlines = analysis_results.get("suggested_redlines", [])
        display_redline_suggestions(redlines)

    with tab3:
        email_draft = analysis_results.get("email_draft", "")
        display_email_draft(email_draft)

    with tab4:
        display_analysis_metadata(analysis_results)

    # Export options
    st.divider()
    export_results(analysis_results)
