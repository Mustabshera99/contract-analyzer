"""
Enhanced progress indicator component with real-time updates and loading states.
"""

import streamlit as st
import time
from typing import Optional, List, Dict
from datetime import datetime, timedelta


def format_time_remaining(seconds: Optional[int]) -> str:
    """Format remaining time in human-readable format."""
    if seconds is None:
        return "Calculating..."

    if seconds < 60:
        return f"{seconds}s remaining"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s remaining"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m remaining"


def progress_indicator(
    message: str, percentage: float, estimated_remaining: Optional[int] = None
):
    """
    Display progress indicator with message and percentage.

    Args:
        message: Progress message to display
        percentage: Progress percentage (0-100)
        estimated_remaining: Estimated remaining time in seconds
    """
    # Ensure percentage is within bounds
    percentage = max(0, min(100, percentage))

    # Create progress bar
    progress_bar = st.progress(percentage / 100)

    # Create status message
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"🔄 {message}")

    with col2:
        if estimated_remaining is not None:
            st.write(f"⏱️ {format_time_remaining(estimated_remaining)}")
        else:
            st.write(f"📊 {percentage:.1f}%")


def multi_step_progress(steps: List[Dict], current_step: int, overall_progress: float):
    """
    Display multi-step progress indicator.

    Args:
        steps: List of step dictionaries with 'name' and 'description'
        current_step: Current step index (0-based)
        overall_progress: Overall progress percentage (0-100)
    """
    st.subheader("📋 Analysis Progress")

    # Overall progress bar
    st.progress(overall_progress / 100)
    st.write(f"Overall Progress: {overall_progress:.1f}%")

    # Step-by-step progress
    for i, step in enumerate(steps):
        if i < current_step:
            # Completed step
            st.success(f"✅ {step['name']}: {step['description']}")
        elif i == current_step:
            # Current step
            st.info(f"🔄 {step['name']}: {step['description']}")
        else:
            # Pending step
            st.write(f"⏳ {step['name']}: {step['description']}")


def loading_spinner(message: str = "Processing..."):
    """Display a loading spinner with message."""
    with st.spinner(message):
        # This will show the spinner until the context exits
        pass


def animated_progress(message: str, duration_seconds: int = 30):
    """
    Display animated progress for unknown duration tasks.

    Args:
        message: Message to display
        duration_seconds: Expected duration for animation
    """
    progress_placeholder = st.empty()
    message_placeholder = st.empty()

    start_time = time.time()

    while time.time() - start_time < duration_seconds:
        elapsed = time.time() - start_time
        progress = min(elapsed / duration_seconds, 1.0)

        with progress_placeholder.container():
            st.progress(progress)

        with message_placeholder.container():
            dots = "." * (int(elapsed) % 4)
            st.write(f"🔄 {message}{dots}")

        time.sleep(0.5)

    # Clear placeholders
    progress_placeholder.empty()
    message_placeholder.empty()


def workflow_progress(
    workflow_nodes: List[str], current_node: str, node_progress: Dict[str, float]
):
    """
    Display workflow-specific progress.

    Args:
        workflow_nodes: List of workflow node names
        current_node: Currently executing node
        node_progress: Dictionary mapping node names to progress percentages
    """
    st.subheader("🔄 Workflow Progress")

    # Calculate overall progress
    total_progress = sum(node_progress.get(node, 0) for node in workflow_nodes) / len(
        workflow_nodes
    )

    # Overall progress
    st.progress(total_progress / 100)
    st.write(f"Overall: {total_progress:.1f}%")

    # Individual node progress
    with st.expander("📊 Detailed Progress", expanded=True):
        for node in workflow_nodes:
            progress = node_progress.get(node, 0)

            if node == current_node:
                st.info(f"🔄 {node}: {progress:.1f}%")
                st.progress(progress / 100)
            elif progress >= 100:
                st.success(f"✅ {node}: Complete")
            else:
                st.write(f"⏳ {node}: Pending")


def error_progress(error_message: str, retry_available: bool = True):
    """
    Display error state in progress indicator.

    Args:
        error_message: Error message to display
        retry_available: Whether retry option should be shown
    """
    st.error(f"❌ Error: {error_message}")

    if retry_available:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Retry", type="primary"):
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.analysis_in_progress = False
                st.rerun()


def success_progress(message: str = "Analysis completed successfully!"):
    """Display success state."""
    st.success(f"✅ {message}")
    st.balloons()


def progress_with_logs(message: str, percentage: float, logs: List[str]):
    """
    Display progress with expandable logs.

    Args:
        message: Progress message
        percentage: Progress percentage
        logs: List of log messages
    """
    # Main progress
    progress_indicator(message, percentage)

    # Expandable logs
    if logs:
        with st.expander("📋 Processing Logs", expanded=False):
            for log in logs[-10:]:  # Show last 10 logs
                st.text(log)


# Predefined workflow steps for contract analysis
CONTRACT_ANALYSIS_STEPS = [
    {"name": "Document Processing", "description": "Extracting text from contract"},
    {"name": "Risk Analysis", "description": "Identifying risky clauses"},
    {"name": "Redline Generation", "description": "Creating suggested alternatives"},
    {"name": "Communication Draft", "description": "Generating negotiation email"},
    {"name": "Final Review", "description": "Compiling results"},
]
