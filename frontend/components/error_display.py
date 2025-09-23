"""
Enhanced error display component with user-friendly messaging and troubleshooting.
"""

import traceback
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st


def categorize_error(error_message: str) -> tuple[str, str, str]:
    """
    Categorize error and provide user-friendly message and solution.

    Returns:
        tuple: (category, user_friendly_message, suggested_solution)
    """
    error_lower = error_message.lower()

    # File-related errors
    if any(keyword in error_lower for keyword in ["file", "upload", "size", "format"]):
        return (
            "File Error",
            "There was an issue with your uploaded file.",
            "Please check that your file is a valid PDF or DOCX under 50MB and try again.",
        )

    # Network/API errors
    elif any(
        keyword in error_lower
        for keyword in ["connection", "timeout", "network", "api", "server"]
    ):
        return (
            "Connection Error",
            "Unable to connect to the analysis service.",
            "Please check your internet connection and try again. If the problem persists, the service may be temporarily unavailable.",
        )

    # Processing errors
    elif any(
        keyword in error_lower
        for keyword in ["processing", "analysis", "workflow", "extraction"]
    ):
        return (
            "Processing Error",
            "An error occurred while analyzing your contract.",
            "This may be due to the contract format or content. Try uploading a different file or contact support if the issue persists.",
        )

    # Authentication errors
    elif any(
        keyword in error_lower
        for keyword in ["auth", "permission", "unauthorized", "forbidden"]
    ):
        return (
            "Authentication Error",
            "Authentication failed or insufficient permissions.",
            "Please check your credentials or contact your administrator.",
        )

    # Validation errors
    elif any(
        keyword in error_lower
        for keyword in ["validation", "invalid", "required", "missing"]
    ):
        return (
            "Validation Error",
            "The provided data is invalid or incomplete.",
            "Please check your input and ensure all required fields are filled correctly.",
        )

    # Default for unknown errors
    else:
        return (
            "Unknown Error",
            "An unexpected error occurred.",
            "Please try again. If the problem persists, contact support with the error details.",
        )


def get_troubleshooting_steps(error_category: str) -> List[str]:
    """Get troubleshooting steps based on error category."""
    troubleshooting_map = {
        "File Error": [
            "Ensure your file is in PDF or DOCX format",
            "Check that the file size is under 50MB",
            "Verify the file is not corrupted or password-protected",
            "Try uploading a different contract file",
        ],
        "Connection Error": [
            "Check your internet connection",
            "Try refreshing the page",
            "Wait a few minutes and try again",
            "Contact support if the issue persists",
        ],
        "Processing Error": [
            "Ensure your contract contains readable text (not scanned images)",
            "Try uploading a simpler contract file",
            "Check that the contract is in English",
            "Contact support with the contract details",
        ],
        "Authentication Error": [
            "Verify your login credentials",
            "Check if your session has expired",
            "Contact your administrator for permissions",
            "Try logging out and back in",
        ],
        "Validation Error": [
            "Review all required fields",
            "Check data format requirements",
            "Ensure all inputs are valid",
            "Try with different input values",
        ],
        "Unknown Error": [
            "Try refreshing the page",
            "Clear your browser cache",
            "Try again in a few minutes",
            "Contact support with error details",
        ],
    }

    return troubleshooting_map.get(error_category, troubleshooting_map["Unknown Error"])


def error_display(
    error_message: str, show_details: bool = False, error_id: Optional[str] = None
):
    """
    Display user-friendly error message with troubleshooting options.

    Args:
        error_message: The error message to display
        show_details: Whether to show technical details
        error_id: Optional error ID for tracking
    """
    # Categorize the error
    category, friendly_message, solution = categorize_error(error_message)

    # Main error display
    st.error(f"❌ {friendly_message}")

    # Error details in expandable section
    with st.expander("🔍 Error Details & Troubleshooting", expanded=False):
        # Error category and ID
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Category:** {category}")
        with col2:
            if error_id:
                st.write(f"**Error ID:** {error_id}")
            else:
                st.write(f"**Time:** {datetime.now().strftime('%H:%M:%S')}")

        # Suggested solution
        st.markdown("**💡 Suggested Solution:**")
        st.info(solution)

        # Troubleshooting steps
        st.markdown("**🛠️ Troubleshooting Steps:**")
        steps = get_troubleshooting_steps(category)
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step}")

        # Technical details (if requested)
        if show_details:
            st.markdown("**🔧 Technical Details:**")
            st.code(error_message, language="text")


def error_display_with_retry(
    error_message: str,
    retry_callback=None,
    show_details: bool = False,
    error_id: Optional[str] = None,
):
    """
    Display error with retry option.

    Args:
        error_message: The error message to display
        retry_callback: Function to call when retry is clicked
        show_details: Whether to show technical details
        error_id: Optional error ID for tracking
    """
    # Display the error
    error_display(error_message, show_details, error_id)

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("🔄 Retry", type="primary"):
            if retry_callback:
                retry_callback()
            else:
                st.rerun()

    with col2:
        if st.button("📞 Get Help"):
            show_help_dialog(error_message, error_id)

    with col3:
        if st.button("📋 Copy Error Details"):
            error_details = (
                f"Error: {error_message}\nTime: {datetime.now().isoformat()}"
            )
            if error_id:
                error_details += f"\nError ID: {error_id}"
            st.success("Error details copied to clipboard!")


def show_help_dialog(error_message: str, error_id: Optional[str] = None):
    """Show help dialog with contact information."""
    st.markdown("### 📞 Get Help")

    st.markdown(
        """
    If you continue to experience issues, please contact our support team:
    
    **📧 Email:** support@contractanalyzer.com  
    **💬 Chat:** Available 9 AM - 5 PM EST  
    **📚 Documentation:** [Help Center](https://docs.contractanalyzer.com)
    
    When contacting support, please include:
    """
    )

    # Pre-filled support information
    support_info = f"""
    Error Message: {error_message}
    Time: {datetime.now().isoformat()}
    Error ID: {error_id or "N/A"}
    Browser: {st.session_state.get("user_agent", "Unknown")}
    """

    st.text_area("Support Information (copy this):", support_info, height=150)


def validation_error_display(validation_errors: List[Dict[str, str]]):
    """
    Display validation errors in a structured format.

    Args:
        validation_errors: List of validation error dictionaries
    """
    if not validation_errors:
        return

    st.error("❌ Please fix the following issues:")

    for i, error in enumerate(validation_errors, 1):
        field = error.get("field", "Unknown")
        message = error.get("message", "Invalid value")

        st.markdown(f"**{i}. {field}:** {message}")


def warning_display(warning_message: str, dismissible: bool = True):
    """
    Display warning message.

    Args:
        warning_message: Warning message to display
        dismissible: Whether the warning can be dismissed
    """
    warning_key = f"warning_dismissed_{hash(warning_message)}"

    if dismissible and st.session_state.get(warning_key, False):
        return

    col1, col2 = st.columns([4, 1])

    with col1:
        st.warning(f"⚠️ {warning_message}")

    with col2:
        if dismissible and st.button("✕", key=f"dismiss_{warning_key}"):
            st.session_state[warning_key] = True
            st.rerun()


def success_display(success_message: str, show_confetti: bool = False):
    """
    Display success message.

    Args:
        success_message: Success message to display
        show_confetti: Whether to show confetti animation
    """
    st.success(f"✅ {success_message}")

    if show_confetti:
        st.balloons()


def info_display(info_message: str, icon: str = "ℹ️"):
    """
    Display informational message.

    Args:
        info_message: Information message to display
        icon: Icon to display with the message
    """
    st.info(f"{icon} {info_message}")


def debug_error_display(error: Exception, show_traceback: bool = False):
    """
    Display error for debugging purposes.

    Args:
        error: Exception object
        show_traceback: Whether to show full traceback
    """
    st.error(f"❌ Debug Error: {error!s}")

    if show_traceback:
        with st.expander("🐛 Full Traceback", expanded=False):
            st.code(traceback.format_exc(), language="python")
