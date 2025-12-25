"""
Optional Streamlit Demo for BiteSoft AI Treatment Summary Generator

This is a DEMO/VALIDATION tool only - NOT required for production.
The core FastAPI service works independently.

Usage:
    streamlit run streamlit_demo.py
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL")
if not API_BASE_URL:
    try:
        # Accessing st.secrets triggers file read, which might fail if no secrets file exists
        if "API_BASE_URL" in st.secrets:
            API_BASE_URL = st.secrets["API_BASE_URL"]
    except Exception:
        # Fallback if secrets file is missing or any other error
        pass

if not API_BASE_URL:
    API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="BiteSoft AI - Treatment Summary Demo",
    page_icon="🦷",
    layout="wide",
)

st.title("🦷 BiteSoft AI Treatment Summary Generator")
st.markdown("**Demo Tool** - For validation and demonstration purposes only")

# Admin panel link in sidebar
with st.sidebar:
    st.markdown("### 🔧 Admin Tools")
    admin_url = f"{API_BASE_URL}/admin/audit-log/list"
    st.markdown(f"[🏥 Open Admin Panel]({admin_url})")
    st.caption("Manage CDT codes, rules, and view audit logs")
    st.divider()

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Case Input")
    
    with st.expander("Patient Details", expanded=True):
        patient_name = st.text_input("Patient Name (optional)", placeholder="John Smith")
        practice_name = st.text_input("Practice Name (optional)", placeholder="BiteSoft Orthodontics")
        patient_age_input = st.text_input("Patient Age (optional)", placeholder="e.g., 25", max_chars=3)
        
        patient_age = None
        if patient_age_input:
            if patient_age_input.isdigit():
                age_value = int(patient_age_input)
                if 0 <= age_value <= 200:
                    patient_age = age_value
                else:
                    st.error("⚠️ Age must be between 0 and 200")
            else:
                st.error("⚠️ Age must contain only digits")
    
    with st.expander("Clinical Data", expanded=True):
        tier = st.selectbox(
            "Case Tier (for CDT mapping)",
            ["express", "mild", "moderate", "complex"],
            index=2,
            help="Used for automatic CDT code selection"
        )
        
        treatment_type = st.selectbox(
            "Treatment Type",
            ["clear aligners", "traditional braces", "lingual braces", "retainers"],
            index=0
        )
        
        area_treated = st.selectbox(
            "Area Treated",
            ["both", "upper", "lower"],
            index=0
        )
        
        duration_range = st.text_input("Duration Range", value="4-6 months")
        
        case_difficulty = st.selectbox(
            "Case Difficulty",
            ["simple", "moderate", "complex"],
            index=1
        )
        
        monitoring_approach = st.selectbox(
            "Monitoring Approach",
            ["remote", "mixed", "in-clinic"],
            index=1
        )
        
        attachments = st.selectbox(
            "Attachments",
            ["none", "some", "extensive"],
            index=1
        )
        
        whitening_included = st.checkbox("Whitening Included", value=False)
        
        dentist_note = st.text_area(
            "Dentist Note (optional)",
            placeholder="Any additional notes...",
            max_chars=500
        )
    
    with st.expander("Output Controls", expanded=True):
        audience = st.selectbox(
            "Audience",
            ["patient", "internal"],
            index=0
        )
        
        tone = st.selectbox(
            "Tone",
            ["concise", "casual", "reassuring", "clinical"],
            index=2
        )
    
    current_inputs = {
        "tier": tier,
        "treatment_type": treatment_type,
        "area_treated": area_treated,
        "duration_range": duration_range,
        "case_difficulty": case_difficulty,
        "monitoring_approach": monitoring_approach,
        "attachments": attachments,
        "whitening_included": whitening_included,
        "audience": audience,
        "tone": tone,
        "patient_name": patient_name,
        "practice_name": practice_name,
        "patient_age": patient_age,
        "dentist_note": dentist_note,
    }
    
    if "last_inputs" not in st.session_state:
        st.session_state["last_inputs"] = None
    
    inputs_changed = st.session_state["last_inputs"] != current_inputs
    
    if "last_result" in st.session_state and not inputs_changed:
        button_label = "🔄 Regenerate Treatment Summary"
        is_regeneration = True
    else:
        button_label = "🚀 Generate Treatment Summary"
        is_regeneration = False
    
    generate_button = st.button(button_label, type="primary", use_container_width=True)

with col2:
    st.subheader("📄 Generated Summary")
    
    if generate_button:
        spinner_text = "Regenerating treatment summary..." if is_regeneration else "Generating treatment summary..."
        
        with st.spinner(spinner_text):
            payload = {
                "tier": tier,
                "treatment_type": treatment_type,
                "area_treated": area_treated,
                "duration_range": duration_range,
                "case_difficulty": case_difficulty,
                "monitoring_approach": monitoring_approach,
                "attachments": attachments,
                "whitening_included": whitening_included,
                "audience": audience,
                "tone": tone,
            }
            
            if patient_name:
                payload["patient_name"] = patient_name
            if practice_name:
                payload["practice_name"] = practice_name
            if patient_age is not None:
                payload["patient_age"] = patient_age
            if dentist_note:
                payload["dentist_note"] = dentist_note
            
            if is_regeneration and "last_result" in st.session_state:
                payload["is_regeneration"] = True
                payload["previous_version_uuid"] = st.session_state["last_result"].get("uuid")
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/v1/generate-treatment-summary",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    document = result["document"]
                    metadata = result.get("metadata", {})
                    
                    st.session_state["last_result"] = result
                    st.session_state["last_payload"] = payload
                    st.session_state["last_inputs"] = current_inputs
                    if "generation_count" not in st.session_state:
                        st.session_state["generation_count"] = 0
                    st.session_state["generation_count"] += 1
                    
                    if is_regeneration:
                        st.toast("✅ Summary regenerated successfully!")
                    else:
                        st.toast("✅ Summary generated successfully!")
                    
                    # Rerun to update button state immediately
                    st.rerun()
                    
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        document = result["document"]
        metadata = result.get("metadata", {})
        
        st.markdown("**Edit the summary below:**")
        generation_key = st.session_state.get("generation_count", 0)
        edited_summary = st.text_area(
            "Summary Text",
            value=document["summary"],
            height=200,
            key=f"edited_summary_text_{generation_key}",
            label_visibility="collapsed"
        )
        
        original_summary = document["summary"]
        is_edited = edited_summary != original_summary
        
        if is_edited:
            st.info("✏️ Summary has been edited")
        
        # Display CDT codes if available
        if result.get("cdt_codes"):
            st.markdown("---")
            st.markdown("**🏥 CDT Code Suggestions**")
            cdt_codes = result["cdt_codes"]
            
            if cdt_codes.get("primary_code"):
                st.markdown(f"**Primary Code:** `{cdt_codes['primary_code']}`")
                if cdt_codes.get("primary_description"):
                    st.caption(cdt_codes["primary_description"])
            
            if cdt_codes.get("suggested_add_ons"):
                st.markdown("**Suggested Add-ons:**")
                for addon in cdt_codes["suggested_add_ons"]:
                    st.markdown(f"- `{addon['code']}`: {addon['description']}")
            
            if cdt_codes.get("notes"):
                st.caption(f"ℹ️ {cdt_codes['notes']}")
        
        with st.expander("📊 Metadata"):
            metadata_display = metadata.copy()
            if result.get("uuid"):
                metadata_display["uuid"] = result["uuid"]
            if result.get("is_regenerated"):
                metadata_display["is_regenerated"] = result["is_regenerated"]
            if result.get("previous_version_uuid"):
                metadata_display["previous_version_uuid"] = result["previous_version_uuid"]
            st.json(metadata_display)
        
        with st.expander("📋 Full JSON Response"):
            st.json(result)
        
        download_data = {
            "success": result["success"],
            "document": document,
            "metadata": metadata,
            "input_parameters": st.session_state.get("last_payload", {}),
            "is_edited": is_edited,
            "edited_summary": edited_summary if is_edited else ""
        }
        
        st.download_button(
            label="💾 Download JSON",
            data=json.dumps(download_data, indent=2, ensure_ascii=False),
            file_name=f"treatment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

st.divider()

with st.expander("ℹ️ About This Demo"):
    st.markdown("""
    ### Purpose
    This Streamlit app is an **optional demo tool** for validating and demonstrating the BiteSoft AI Treatment Summary API.
    
    ### Important Notes
    - **Not required for production** - The FastAPI service works independently
    - **For validation only** - Portal team handles actual UI and email integration
    - **Demo purposes** - Shows API capabilities and output format
    
    ### v1 Scope
    ✅ AI generates editable treatment summary text  
    ✅ FastAPI returns structured JSON output  
    ❌ No email automation (portal team handles)  
    ❌ No production UI (portal team handles)  
    
    ### How to Run
    ```bash
    # Start FastAPI server
    uvicorn app.main:app --reload
    
    # In another terminal, start Streamlit demo
    streamlit run streamlit_demo.py
    ```
    """)

with st.expander("🔧 API Health Check"):
    if st.button("Check API Status"):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is running")
                st.json(response.json())
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except:
            st.error("❌ API is not reachable. Start the FastAPI server first.")
