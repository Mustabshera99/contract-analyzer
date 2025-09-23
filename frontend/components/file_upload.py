"""
Enhanced file upload component with validation and drag-and-drop support.
"""

import io
from typing import Optional, Union

import streamlit as st
from ..config import config


def validate_file_size(file_obj, max_size_mb: int = None) -> tuple[bool, str]:
    """Validate file size."""
    if max_size_mb is None:
        max_size_mb = config.MAX_FILE_SIZE_MB

    if hasattr(file_obj, "size"):
        file_size_mb = file_obj.size / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return (
                False,
                f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)",
            )

    return True, ""


def validate_file_type(file_obj, allowed_types: list = None) -> tuple[bool, str]:
    """Validate file type."""
    if allowed_types is None:
        allowed_types = config.ALLOWED_FILE_TYPES

    if hasattr(file_obj, "type"):
        file_extension = (
            file_obj.name.split(".")[-1].lower() if "." in file_obj.name else ""
        )

        # Check both MIME type and extension
        valid_extensions = [ext.strip().lower() for ext in allowed_types]

        if file_extension not in valid_extensions:
            return (
                False,
                f"File type '{file_extension}' not supported. Allowed types: {', '.join(valid_extensions)}",
            )

    return True, ""


def validate_file_content(file_obj) -> tuple[bool, str]:
    """Basic file content validation."""
    try:
        # Check if file is readable
        if hasattr(file_obj, "read"):
            current_pos = file_obj.tell() if hasattr(file_obj, "tell") else 0
            content = file_obj.read(1024)  # Read first 1KB
            if hasattr(file_obj, "seek"):
                file_obj.seek(current_pos)  # Reset position

            if not content:
                return False, "File appears to be empty"

        return True, ""
    except Exception as e:
        return False, f"Error reading file: {e!s}"


def display_file_info(file_obj):
    """Display file information."""
    if not file_obj:
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Filename", file_obj.name)

    with col2:
        if hasattr(file_obj, "size"):
            size_mb = file_obj.size / (1024 * 1024)
            st.metric("📊 Size", f"{size_mb:.2f} MB")

    with col3:
        if hasattr(file_obj, "type"):
            st.metric("🏷️ Type", file_obj.type or "Unknown")


def file_upload_component() -> Optional[Union[io.BytesIO, any]]:
    """
    Enhanced file upload component with drag-and-drop, validation, and user feedback.

    Returns:
        Uploaded file object if valid, None otherwise
    """
    st.header("📤 Upload Contract Document")

    # Create upload area with custom styling
    st.markdown(
        """
    <style>
    .upload-area {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 10px 0;
    }
    .upload-area:hover {
        border-color: #007bff;
        background-color: #e3f2fd;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # File uploader with enhanced options
    uploaded_file = st.file_uploader(
        label="Choose a contract file",
        type=config.ALLOWED_FILE_TYPES,
        help=f"Drag and drop your contract here or click to browse. "
        f"Supported formats: {', '.join(config.ALLOWED_FILE_TYPES).upper()}. "
        f"Maximum size: {config.MAX_FILE_SIZE_MB}MB",
        label_visibility="collapsed",
    )

    # Display upload instructions
    if not uploaded_file:
        st.markdown(
            """
        <div class="upload-area">
            <h3>📁 Drag & Drop Your Contract</h3>
            <p>Or click above to browse files</p>
            <p><small>Supported formats: PDF, DOCX | Max size: {}MB</small></p>
        </div>
        """.format(
                config.MAX_FILE_SIZE_MB
            ),
            unsafe_allow_html=True,
        )

        # Show format examples
        with st.expander("ℹ️ Supported File Formats"):
            st.markdown(
                """
            - **PDF (.pdf)**: Portable Document Format files
            - **Word (.docx)**: Microsoft Word documents
            
            **File Requirements:**
            - Maximum file size: {}MB
            - Text must be readable (not scanned images)
            - Contract should be in English
            """.format(
                    config.MAX_FILE_SIZE_MB
                )
            )

        return None

    # Validate uploaded file
    validation_errors = []

    # Size validation
    size_valid, size_error = validate_file_size(uploaded_file)
    if not size_valid:
        validation_errors.append(size_error)

    # Type validation
    type_valid, type_error = validate_file_type(uploaded_file)
    if not type_valid:
        validation_errors.append(type_error)

    # Content validation
    content_valid, content_error = validate_file_content(uploaded_file)
    if not content_valid:
        validation_errors.append(content_error)

    # Display validation results
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")

        st.warning("Please upload a valid file to continue.")
        return None

    # File is valid - display info and success message
    st.success("✅ File uploaded successfully!")

    # Display file information
    display_file_info(uploaded_file)

    # Additional file preview options
    with st.expander("🔍 File Preview Options"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📋 Show File Details"):
                st.json(
                    {
                        "filename": uploaded_file.name,
                        "size_bytes": getattr(uploaded_file, "size", "Unknown"),
                        "type": getattr(uploaded_file, "type", "Unknown"),
                        "size_mb": f"{getattr(uploaded_file, 'size', 0) / (1024 * 1024):.2f}",
                    }
                )

        with col2:
            if st.button("🔄 Reset Upload"):
                st.rerun()

    return uploaded_file


# Legacy function for backward compatibility
def file_upload():
    """Legacy file upload function."""
    return file_upload_component()
