"""Quadron Streamlit dashboard for visual equipment condition inspection."""

import base64
import json
import mimetypes
from datetime import datetime

import streamlit as st
from azure.core.exceptions import ClientAuthenticationError

from config import APP_DESCRIPTION, APP_TITLE
from src.checklist import DEFAULT_CHECKLIST_PATH, load_checklists
from src.history import load_history, save_inspection
from src.image_validator import (
    ALLOWED_IMAGE_TYPES,
    MAX_IMAGE_SIZE_BYTES,
    validate_image_file,
)
from src.inspector import inspect_equipment


st.set_page_config(
    page_title="Quadron | Equipment Inspector",
    page_icon=":material/engineering:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    """Add small, scoped visual enhancements for the branded dashboard."""
    st.markdown(
        """
        <style>
        h1, h2, h3, h4 {
            font-family: "Aptos Display", "Aptos", "Segoe UI", Arial, sans-serif;
            letter-spacing: -0.02em;
        }
        .quadron-hero {
            padding: 2rem 2.15rem 2.1rem;
            border: 1px solid rgba(156, 163, 175, 0.2);
            border-radius: 16px;
            background: linear-gradient(135deg, #24262a, #141517);
            box-shadow: 0 16px 38px rgba(0, 0, 0, 0.28);
            margin-bottom: 1.75rem;
        }
        .quadron-eyebrow {
            color: #aeb4be;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }
        .quadron-title {
            color: #f3f4f6;
            font-size: clamp(1.75rem, 3vw, 2.7rem);
            font-weight: 750;
            letter-spacing: -0.035em;
            line-height: 1.1;
            margin: 0.55rem 0 0.9rem;
        }
        .quadron-subtitle {
            color: #c5c8ce;
            font-size: 1rem;
            line-height: 1.65;
            max-width: 760px;
            margin-bottom: 0;
        }
        .quadron-kicker {
            color: #969ba4;
            font-size: 0.82rem;
            margin-top: 1.1rem;
        }
        .quadron-verdict {
            border-radius: 12px;
            padding: 1.35rem 1.45rem;
            border: 1px solid rgba(156, 163, 175, 0.2);
            background: #1b1d20;
        }
        .quadron-verdict-label {
            color: #9ca3af;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .quadron-verdict-value {
            font-size: 1.55rem;
            font-weight: 760;
            margin-top: 0.22rem;
        }
        .verdict-good { color: #6ee7b7; }
        .verdict-repair { color: #fbbf24; }
        .verdict-unsafe { color: #fb7185; }
        .verdict-cannot { color: #c4c7cc; }
        .quadron-note {
            border-left: 3px solid #9ca3af;
            color: #d1d5db;
            padding: 0.35rem 0 0.35rem 1rem;
            line-height: 1.65;
        }
        .quadron-sidebar-brand {
            padding: 0.65rem 0 1.5rem;
        }
        .quadron-sidebar-brand strong {
            color: #f3f4f6;
            font-size: 1.35rem;
            letter-spacing: 0.08em;
        }
        .quadron-sidebar-brand span {
            color: #aeb4be;
            display: block;
            font-size: 0.76rem;
            line-height: 1.45;
            margin-top: 0.45rem;
        }
        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(156, 163, 175, 0.12);
        }
        div[data-testid="stVerticalBlock"] > div:has(> div.quadron-verdict) {
            margin-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def verdict_class(verdict: str) -> tuple[str, str]:
    """Return a CSS class and readable label for a verdict."""
    normalized = verdict.lower().replace(" ", "_")
    if normalized == "good":
        return "verdict-good", "GOOD"
    if normalized == "needs_repair":
        return "verdict-repair", "NEEDS REPAIR"
    if normalized == "unsafe":
        return "verdict-unsafe", "UNSAFE"
    return "verdict-cannot", "CANNOT ASSESS"


def render_verdict_card(verdict: str) -> None:
    """Render a prominent, color-coded verdict without changing its value."""
    css_class, label = verdict_class(verdict)
    st.markdown(
        f"""
        <div class="quadron-verdict">
            <div class="quadron-verdict-label">Inspection verdict</div>
            <div class="quadron-verdict-value {css_class}">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_checklist_results(checklist_results: list[dict]) -> None:
    """Render every checklist result and its evidence."""
    if not checklist_results:
        st.info("No checklist results available.", icon=":material/info:")
        return

    for index, item in enumerate(checklist_results, 1):
        status = item.get("status", "Unknown")
        status_icon = (
            ":material/check_circle:"
            if status == "Pass"
            else ":material/error:"
            if status == "Fail"
            else ":material/help:"
        )
        with st.container(border=True):
            st.markdown(
                f"**{index}. {item.get('item', 'Checklist item')}**  \n"
                f"{status_icon} **{status}**"
            )
            st.caption(item.get("evidence", "No evidence provided."))


def render_checklist_editor() -> None:
    """Render the existing editable checklist workflow in the sidebar."""
    try:
        checklists = load_checklists()
    except Exception as error:
        st.sidebar.error(f"Could not load checklists: {error}")
        return

    st.sidebar.subheader("Checklist management", divider="blue")
    st.sidebar.caption("Changes apply to future inspections.")
    edit_category = st.sidebar.selectbox(
        "Checklist category",
        list(checklists.keys()),
        key="edit_category",
    )

    with st.sidebar.form("checklist_editor"):
        edited_items = [
            st.text_input(
                f"Inspection item {index + 1}",
                value=item,
                key=f"checklist_{edit_category}_{index}",
            )
            for index, item in enumerate(
                checklists[edit_category]["inspection_items"]
            )
        ]
        save_checklist = st.form_submit_button(
            "Save checklist changes",
            type="primary",
            width="stretch",
            icon=":material/save:",
        )

    if save_checklist:
        if len(edited_items) != 5 or any(not item.strip() for item in edited_items):
            st.sidebar.error("All five checklist items must contain text.")
            return

        checklists[edit_category]["inspection_items"] = edited_items
        with DEFAULT_CHECKLIST_PATH.open("w", encoding="utf-8") as file:
            json.dump(checklists, file, indent=2)
        st.sidebar.success("Checklist saved successfully.", icon=":material/check:")
        st.rerun()


def render_sidebar() -> None:
    """Render brand, navigation cues, and the existing checklist editor."""
    with st.sidebar:
        st.markdown(
            """
            <div class="quadron-sidebar-brand">
                <strong>QUADRON</strong>
                <span>AI engineering equipment inspector</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Team 08 · Problem P06")
        st.markdown("**Workspace**  \n:material/scan: Inspect equipment")
        st.markdown("**Records**  \n:material/history: Inspection history")
        st.markdown("**Configuration**  \n:material/checklist: Checklist management")
        st.markdown("**About**  \n:material/info: Product and scope")
        st.divider()
        render_checklist_editor()
        st.divider()
        st.caption("Powered by Python · Streamlit · Azure AI Foundry")


def render_header() -> None:
    """Render the main product header and honest service status."""
    st.markdown(
        f"""
        <section class="quadron-hero">
            <div class="quadron-eyebrow">QUADRON · AI inspection workspace</div>
            <div class="quadron-title">{APP_TITLE}</div>
            <p class="quadron-subtitle">
                {APP_DESCRIPTION} Upload a clear photograph and receive a structured
                assessment grounded in visible evidence.
            </p>
            <div class="quadron-kicker">
                Visual screening only · No claims about internal functionality or calibration
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Service status: available for inspection when the configured Azure AI Foundry "
        "agent is reachable. No live connection check is performed until an inspection runs."
    )


def render_upload_section() -> tuple[object | None, bytes | None, str | None, bool]:
    """Render upload controls and return the selected image details."""
    st.header("Inspection workspace", icon=":material/biotech:")
    st.caption("Upload a PNG or JPEG image to begin. Inspection starts only when you click the button.")

    uploaded_file = st.file_uploader(
        "Equipment photograph",
        type=["png", "jpg", "jpeg"],
        help="Accepted formats: PNG and JPEG. Maximum size: 2 MB.",
        key="equipment_upload",
    )

    if uploaded_file is None:
        with st.container(border=True):
            st.markdown("### Ready for a new inspection")
            st.caption("Drag and drop an equipment photograph above, or browse your device.")
            st.markdown(
                ":material/upload_file: **PNG or JPEG** &nbsp;&nbsp; "
                ":material/data_usage: **2 MB maximum** &nbsp;&nbsp; "
                ":material/visibility: **Visible evidence only**"
            )
        return None, None, None, False

    image_data = uploaded_file.getvalue()
    content_type = (
        uploaded_file.type
        if uploaded_file.type in ALLOWED_IMAGE_TYPES
        else mimetypes.guess_type(uploaded_file.name)[0]
    )
    valid, validation_message = validate_image_file(image_data, content_type or "")
    can_inspect = valid

    image_column, details_column = st.columns([1.2, 1], gap="large")
    with image_column:
        st.image(
            image_data,
            caption=uploaded_file.name,
            width="stretch",
            alt="Uploaded equipment photograph",
        )
    with details_column:
        with st.container(border=True):
            st.subheader("Image details")
            st.metric("File size", f"{len(image_data) / 1024:.1f} KB")
            st.caption(f"Filename: {uploaded_file.name}")
            st.caption(f"Format: {content_type or 'Unknown'}")
            if valid:
                st.success(validation_message, icon=":material/check_circle:")
            else:
                st.error(validation_message, icon=":material/error:")

    return uploaded_file, image_data, content_type, can_inspect


def render_result(latest: dict) -> None:
    """Render the complete existing inspection response as a report."""
    st.header("Inspection report", icon=":material/assessment:")
    verdict = latest.get("verdict", "cannot_assess")
    confidence = latest.get("confidence", 0)

    verdict_column, summary_column = st.columns([1, 2], gap="large")
    with verdict_column:
        render_verdict_card(verdict)
        st.progress(float(confidence), text=f"Confidence · {confidence:.0%}")
    with summary_column:
        summary_a, summary_b, summary_c = st.columns(3)
        summary_a.metric("Equipment", latest.get("equipment_name", "Unknown"))
        summary_b.metric("Category", latest.get("category", "Unknown"))
        summary_c.metric("Confidence", f"{confidence:.0%}")

    with st.container(border=True):
        st.subheader("Assessment explanation")
        st.markdown(
            f'<div class="quadron-note">{latest.get("reason", "No explanation available.")}</div>',
            unsafe_allow_html=True,
        )

    issues = latest.get("visible_issues", [])
    with st.container(border=True):
        st.subheader("Visible issues", anchor=False)
        if issues:
            for issue in issues:
                st.warning(issue, icon=":material/warning:")
        elif verdict == "cannot_assess":
            st.info("The image could not be assessed reliably.", icon=":material/help:")
        else:
            st.success("No visible defects reported.", icon=":material/check_circle:")

    with st.container(border=True):
        st.subheader("Five-point checklist")
        render_checklist_results(latest.get("checklist_results", []))


def render_history(history: list[dict]) -> None:
    """Render history records with thumbnails without changing storage."""
    st.header("Inspection history", icon=":material/history:")
    if not history:
        with st.container(border=True):
            st.info(
                "No previous inspections available. Completed inspections will appear here.",
                icon=":material/inventory_2:",
            )
        return

    st.caption(f"{len(history)} inspection record(s) · newest first")
    for record in reversed(history):
        timestamp = record.get("timestamp", "Unknown date")
        equipment = record.get("equipment_name", "Unknown")
        verdict = record.get("verdict", "Unknown")
        with st.expander(
            f"{equipment} · {verdict} · {timestamp}",
            icon=":material/description:",
        ):
            image_column, details_column = st.columns([1, 2], gap="large")
            with image_column:
                encoded_image = record.get("image_base64")
                if encoded_image:
                    try:
                        st.image(
                            base64.b64decode(encoded_image),
                            caption=record.get("filename", "Inspection image"),
                            width="stretch",
                            alt="Historical inspection thumbnail",
                        )
                    except (ValueError, TypeError):
                        st.warning("Could not display saved thumbnail.")
            with details_column:
                st.metric("Verdict", verdict)
                st.write("**Category:**", record.get("category", "Unknown"))
                st.write("**Equipment:**", equipment)
                st.write("**Confidence:**", f"{record.get('confidence', 0):.0%}")
                for issue in record.get("visible_issues", []):
                    st.warning(issue, icon=":material/warning:")


def render_about() -> None:
    """Render product scope and responsible-use information."""
    st.header("About Quadron", icon=":material/info:")
    with st.container(border=True):
        st.markdown(
            """
            **Quadron – AI-Powered Engineering Equipment Condition Inspector** is
            the team's solution for **P06 – Lab Equipment Condition Inspector**.

            - **Technology:** Python, Streamlit, Azure AI Foundry, GPT-5 mini
            - **Team:** Quadron, Team 08
            - **Purpose:** Visual condition screening from uploaded equipment images

            The application reports visible evidence only. It does not verify
            internal functionality, calibration, electrical performance, or
            invisible structural damage, and it is not a certified safety inspection.
            """
        )


render_sidebar()
inject_styles()
render_header()

uploaded_file, image_data, content_type, can_inspect = render_upload_section()

st.subheader("Run inspection", anchor=False)
inspect_clicked = st.button(
    "Inspect equipment",
    type="primary",
    disabled=not can_inspect,
    width="stretch",
    icon=":material/search_insights:",
    help="Analyze the uploaded image with the configured Azure AI Foundry agent.",
)

if inspect_clicked and uploaded_file is not None and image_data is not None and content_type:
    try:
        with st.spinner("Analyzing visible equipment evidence with Azure AI Foundry..."):
            result = inspect_equipment(image_data, content_type)
            result_data = result.model_dump()
            history_record = {
                "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                "filename": uploaded_file.name,
                "content_type": content_type,
                "image_base64": base64.b64encode(image_data).decode("utf-8"),
                **result_data,
            }
            save_inspection(history_record)
            st.session_state["latest_inspection"] = history_record
        st.success("Inspection completed successfully.", icon=":material/check_circle:")
    except ClientAuthenticationError:
        st.error(
            "Azure authentication is unavailable. Sign in to Azure through the "
            "VS Code Azure extension, or authenticate with Azure CLI and try again.",
            icon=":material/lock:",
        )
    except ValueError as error:
        st.error(f"Inspection could not be completed: {error}", icon=":material/error:")
    except Exception:
        st.error(
            "Inspection could not be completed. Verify the Azure AI Foundry "
            "configuration and try again.",
            icon=":material/error:",
        )

latest = st.session_state.get("latest_inspection")
if latest:
    render_result(latest)

try:
    inspection_history = load_history()
except Exception as error:
    st.error(f"Could not load inspection history: {error}", icon=":material/error:")
    inspection_history = []

render_history(inspection_history)
render_about()

st.caption("Quadron · P06 · Visual evidence assistant for engineering equipment")
