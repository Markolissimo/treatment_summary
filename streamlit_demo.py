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
from datetime import datetime

import streamlit as st
import requests
import json
import os
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", st.secrets.get("API_BASE_URL", "http://localhost:8000"))

st.set_page_config(
    page_title="BiteSoft AI - Treatment Summary Demo",
    page_icon="🦷",
    layout="wide",
)

st.title("🦷 BiteSoft AI Treatment Summary Generator")
st.markdown("**Demo Tool** - For validation and demonstration purposes only")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Case Input")
    
    with st.expander("Patient Details", expanded=True):
        patient_name = st.text_input("Patient Name (optional)", placeholder="John Smith")
        practice_name = st.text_input("Practice Name (optional)", placeholder="BiteSoft Orthodontics")
        patient_age = st.number_input("Patient Age (optional)", min_value=0, max_value=120, value=None, step=1)
    
    with st.expander("Clinical Data", expanded=True):
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
    
    generate_button = st.button("🚀 Generate Treatment Summary", type="primary", use_container_width=True)

with col2:
    st.subheader("📄 Generated Summary")
    
    if generate_button:
        if "last_result" in st.session_state:
            del st.session_state["last_result"]
        if "last_payload" in st.session_state:
            del st.session_state["last_payload"]
        
        with st.spinner("Generating treatment summary..."):
            payload = {
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
                    if "generation_count" not in st.session_state:
                        st.session_state["generation_count"] = 0
                    st.session_state["generation_count"] += 1
                    
                    st.success("✅ Summary generated successfully!")
                    
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
        
        with st.expander("📊 Metadata"):
            st.json(metadata)
        
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
