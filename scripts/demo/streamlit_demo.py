"""
Optional Streamlit Demo for BiteSoft AI Document Generation

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
        if "API_BASE_URL" in st.secrets:
            API_BASE_URL = st.secrets["API_BASE_URL"]
    except Exception:
        pass

if not API_BASE_URL:
    API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="BiteSoft AI - Document Generation Demo",
    page_icon="🦷",
    layout="wide",
)

st.title("🦷 BiteSoft AI Document Generation")
st.markdown("**Demo Tool** - For validation and demonstration purposes only")

# Admin panel link in sidebar
with st.sidebar:
    st.markdown("### 🔧 Admin Tools")
    admin_url = f"{API_BASE_URL}/admin/audit-log/list"
    st.markdown(f"[🏥 Open Admin Panel]({admin_url})")
    st.caption("Manage CDT codes, rules, and view audit logs")
    st.divider()

# Tab navigation
tab1, tab2 = st.tabs(["📋 Treatment Summary", "📄 Insurance Summary"])

# ============================================================================
# TAB 1: TREATMENT SUMMARY
# ============================================================================
with tab1:
    st.subheader("Treatment Summary Generator")
    st.divider()
    
    ts_col1, ts_col2 = st.columns([1, 1])
    
    with ts_col1:
        st.markdown("### 📋 Case Input")
        
        with st.expander("Patient Details", expanded=True):
            patient_name = st.text_input("Patient Name (optional)", placeholder="John Smith", key="ts_patient_name")
            practice_name = st.text_input("Practice Name (optional)", placeholder="BiteSoft Orthodontics", key="ts_practice_name")
            patient_age_input = st.text_input("Patient Age (optional)", placeholder="e.g., 25", max_chars=3, key="ts_patient_age")
            
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
                help="Used for automatic CDT code selection",
                key="ts_tier"
            )
            
            treatment_type = st.selectbox(
                "Treatment Type",
                ["clear aligners", "traditional braces", "lingual braces", "retainers"],
                index=0,
                key="ts_treatment_type"
            )
            
            area_treated = st.selectbox(
                "Area Treated",
                ["both", "upper", "lower"],
                index=0,
                key="ts_area_treated"
            )
            
            duration_range = st.text_input("Duration Range", value="4-6 months", key="ts_duration")
            
            case_difficulty = st.selectbox(
                "Case Difficulty",
                ["simple", "moderate", "complex"],
                index=1,
                key="ts_difficulty"
            )
            
            monitoring_approach = st.selectbox(
                "Monitoring Approach",
                ["remote", "mixed", "in-clinic"],
                index=1,
                key="ts_monitoring"
            )
            
            attachments = st.selectbox(
                "Attachments",
                ["none", "some", "extensive"],
                index=1,
                key="ts_attachments"
            )
            
            whitening_included = st.checkbox("Whitening Included", value=False, key="ts_whitening")
            
            dentist_note = st.text_area(
                "Dentist Note (optional)",
                placeholder="Any additional notes...",
                max_chars=500,
                key="ts_dentist_note"
            )
        
        with st.expander("Output Controls", expanded=True):
            audience = st.selectbox(
                "Audience",
                ["patient", "internal"],
                index=0,
                key="ts_audience"
            )
            
            tone = st.selectbox(
                "Tone",
                ["concise", "casual", "reassuring", "clinical"],
                index=2,
                key="ts_tone"
            )
        
        # Track inputs for regeneration
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
        
        # Convert dict to hashable string for set storage
        current_inputs_key = json.dumps(current_inputs, sort_keys=True)
        
        if "last_inputs" not in st.session_state:
            st.session_state["last_inputs"] = None

        if "ts_last_confirmed_inputs" not in st.session_state:
            st.session_state["ts_last_confirmed_inputs"] = None
        
        inputs_changed = st.session_state["last_inputs"] != current_inputs_key
        
        # Maintain regeneration state: if inputs haven't changed and we've not just confirmed this input set
        if (
            "last_result" in st.session_state
            and not inputs_changed
            and st.session_state.get("ts_last_confirmed_inputs") != current_inputs_key
        ):
            button_label = "🔄 Regenerate Treatment Summary"
            is_regeneration = True
        else:
            button_label = "🚀 Generate Treatment Summary"
            is_regeneration = False
            if inputs_changed:
                # Clear confirmation history when inputs change
                if "ts_confirmations" in st.session_state:
                    del st.session_state["ts_confirmations"]
        
        generate_button = st.button(button_label, type="primary", use_container_width=True, key="ts_generate")
    
    with ts_col2:
        st.markdown("### 📄 Generated Summary")
        
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
                        
                        st.session_state["last_result"] = result
                        st.session_state["last_payload"] = payload
                        st.session_state["last_inputs"] = current_inputs_key

                        if not is_regeneration:
                            if "ts_confirmations" in st.session_state:
                                del st.session_state["ts_confirmations"]
                            if "ts_last_confirmation" in st.session_state:
                                del st.session_state["ts_last_confirmation"]
                            st.session_state["ts_last_confirmed_inputs"] = None
                        
                        # Track input history for regeneration detection
                        if "ts_input_history" not in st.session_state:
                            st.session_state["ts_input_history"] = set()
                        st.session_state["ts_input_history"].add(current_inputs_key)
                        
                        if "generation_count" not in st.session_state:
                            st.session_state["generation_count"] = 0
                        st.session_state["generation_count"] += 1
                        
                        if is_regeneration:
                            st.toast("✅ Summary regenerated successfully!")
                        else:
                            st.toast("✅ Summary generated successfully!")
                        
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

            confirm_notes = st.text_area(
                "Approval Notes (optional)",
                placeholder="Optional approval notes...",
                max_chars=1000,
                key=f"ts_confirm_notes_{generation_key}",
            )

            generation_id = result.get("uuid")
            approve_disabled = not generation_id
            approve_button = st.button(
                "✅ Approve (Log Confirmation)",
                type="secondary",
                use_container_width=True,
                disabled=approve_disabled,
                key=f"ts_approve_{generation_key}",
            )

            if approve_button:
                st.session_state["ts_pending_approve"] = True
                st.session_state["ts_pending_generation_id"] = generation_id
                st.session_state["ts_pending_confirm_notes"] = confirm_notes
                # Match output_data structure: {"treatment_summary": "text"}
                st.session_state["ts_pending_confirmed_payload"] = {
                    "treatment_summary": edited_summary
                }
                st.rerun()

            if st.session_state.get("ts_pending_approve") and st.session_state.get("ts_pending_generation_id") == generation_id:
                st.warning("Are you sure you want to approve/confirm this document?", icon="⚠️")
                confirm_col, cancel_col = st.columns([1, 1])
                with confirm_col:
                    confirm_now = st.button(
                        "Yes, confirm",
                        type="primary",
                        use_container_width=True,
                        key=f"ts_confirm_yes_{generation_key}",
                    )
                with cancel_col:
                    cancel_now = st.button(
                        "Cancel",
                        type="secondary",
                        use_container_width=True,
                        key=f"ts_confirm_cancel_{generation_key}",
                    )

                if cancel_now:
                    st.session_state["ts_pending_approve"] = False
                    st.session_state["ts_pending_generation_id"] = None
                    st.session_state["ts_pending_confirm_notes"] = None
                    st.session_state["ts_pending_confirmed_payload"] = None
                    st.rerun()

                if confirm_now:
                    try:
                        confirm_response = requests.post(
                            f"{API_BASE_URL}/api/v1/documents/{generation_id}/confirm",
                            json={
                                "confirmed_payload": st.session_state.get("ts_pending_confirmed_payload"),
                                "notes": st.session_state.get("ts_pending_confirm_notes") or None,
                            },
                            timeout=30,
                        )

                        if confirm_response.status_code == 200:
                            confirmation_data = confirm_response.json()

                            if "ts_confirmations" not in st.session_state:
                                st.session_state["ts_confirmations"] = []
                            st.session_state["ts_confirmations"].append(confirmation_data)
                            st.session_state["ts_last_confirmation"] = confirmation_data
                            st.session_state["ts_last_confirmed_inputs"] = current_inputs_key

                            st.session_state["ts_pending_approve"] = False
                            st.session_state["ts_pending_generation_id"] = None
                            st.session_state["ts_pending_confirm_notes"] = None
                            st.session_state["ts_pending_confirmed_payload"] = None

                            st.toast("✅ Document approved and logged")
                            st.rerun()
                        else:
                            st.error(f"❌ Approval failed: {confirm_response.status_code}")
                            try:
                                st.json(confirm_response.json())
                            except Exception:
                                st.write(confirm_response.text)
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Show all confirmations for this input set
            if "ts_confirmations" in st.session_state and st.session_state["ts_confirmations"]:
                with st.expander(f"✅ Approval / Confirmation History ({len(st.session_state['ts_confirmations'])} approvals)"):
                    for idx, conf in enumerate(reversed(st.session_state["ts_confirmations"]), 1):
                        st.markdown(f"**Approval #{len(st.session_state['ts_confirmations']) - idx + 1}** (Generation: `{conf.get('generation_id', 'N/A')[:8]}...`)")
                        st.json(conf)
                        if idx < len(st.session_state["ts_confirmations"]):
                            st.markdown("---")
            
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
                mime="application/json",
                key="ts_download"
            )

# ============================================================================
# TAB 2: INSURANCE SUMMARY
# ============================================================================
with tab2:
    st.subheader("Insurance Summary Generator")
    st.markdown("*Administrative support tool for insurance documentation*")
    st.divider()
    
    ins_col1, ins_col2 = st.columns([1, 1])
    
    with ins_col1:
        st.markdown("### 📋 Case Input")
        
        with st.expander("Case Details", expanded=True):
            ins_tier = st.selectbox(
                "Tier",
                ["express_mild", "moderate", "complex"],
                index=1,
                help="Express/Mild → D8010, Moderate/Complex → D8080/D8090",
                key="ins_tier"
            )
            
            ins_arches = st.selectbox(
                "Arches",
                ["both", "upper", "lower"],
                index=0,
                key="ins_arches"
            )
            
            ins_age_group = st.selectbox(
                "Age Group",
                ["adolescent", "adult"],
                index=1,
                help="Adolescent (<18) or Adult (≥18)",
                key="ins_age_group"
            )
            
            ins_retainers = st.checkbox(
                "Retainers Included (Bundled)",
                value=True,
                key="ins_retainers"
            )
            
            ins_monitoring = st.selectbox(
                "Monitoring Approach",
                ["remote", "mixed", "in-clinic"],
                index=1,
                key="ins_monitoring"
            )
        
        with st.expander("Diagnostic Assets", expanded=True):
            st.caption("Only flagged assets will generate CDT codes")
            ins_photos = st.checkbox("Intraoral Photos", value=True, key="ins_photos")
            ins_pano = st.checkbox("Panoramic X-ray", value=True, key="ins_pano")
            ins_fmx = st.checkbox("FMX - Full Mouth X-rays", value=False, key="ins_fmx")
        
        with st.expander("Additional Notes", expanded=False):
            ins_notes = st.text_area(
                "Dentist/Admin Notes (optional)",
                placeholder="Any additional notes...",
                max_chars=500,
                key="ins_notes"
            )
        
        # Track inputs for regeneration
        ins_current_inputs = {
            "tier": ins_tier,
            "arches": ins_arches,
            "age_group": ins_age_group,
            "retainers_included": ins_retainers,
            "monitoring_approach": ins_monitoring,
            "intraoral_photos": ins_photos,
            "panoramic_xray": ins_pano,
            "fmx": ins_fmx,
            "notes": ins_notes,
        }
        
        # Convert dict to hashable string for set storage
        ins_current_inputs_key = json.dumps(ins_current_inputs, sort_keys=True)
        
        if "ins_last_inputs" not in st.session_state:
            st.session_state["ins_last_inputs"] = None

        if "ins_last_confirmed_inputs" not in st.session_state:
            st.session_state["ins_last_confirmed_inputs"] = None
        
        ins_inputs_changed = st.session_state["ins_last_inputs"] != ins_current_inputs_key
        
        # Maintain regeneration state: if inputs haven't changed and we've not just confirmed this input set
        if (
            "ins_last_result" in st.session_state
            and not ins_inputs_changed
            and st.session_state.get("ins_last_confirmed_inputs") != ins_current_inputs_key
        ):
            ins_button_label = "🔄 Regenerate Insurance Summary"
            ins_is_regeneration = True
        else:
            ins_button_label = "🚀 Generate Insurance Summary"
            ins_is_regeneration = False
            if ins_inputs_changed:
                # Clear confirmation history when inputs change
                if "ins_confirmations" in st.session_state:
                    del st.session_state["ins_confirmations"]
        
        ins_generate_button = st.button(ins_button_label, type="primary", use_container_width=True, key="ins_generate")
    
    with ins_col2:
        st.markdown("### 📄 Generated Summary")
        
        if ins_generate_button:
            spinner_text = "Regenerating insurance summary..." if ins_is_regeneration else "Generating insurance summary..."
            
            with st.spinner(spinner_text):
                payload = {
                    "tier": ins_tier,
                    "arches": ins_arches,
                    "age_group": ins_age_group,
                    "retainers_included": ins_retainers,
                    "monitoring_approach": ins_monitoring,
                    "diagnostic_assets": {
                        "intraoral_photos": ins_photos,
                        "panoramic_xray": ins_pano,
                        "fmx": ins_fmx,
                    },
                }
                
                if ins_notes:
                    payload["notes"] = ins_notes
                
                if ins_is_regeneration and "ins_last_result" in st.session_state:
                    payload["is_regeneration"] = True
                    payload["previous_version_uuid"] = st.session_state["ins_last_result"].get("uuid")
                
                try:
                    ins_response = requests.post(
                        f"{API_BASE_URL}/api/v1/generate-insurance-summary",
                        json=payload,
                        timeout=30
                    )
                    
                    if ins_response.status_code == 200:
                        ins_result = ins_response.json()
                        
                        st.session_state["ins_last_result"] = ins_result
                        st.session_state["ins_last_payload"] = payload
                        st.session_state["ins_last_inputs"] = ins_current_inputs_key

                        if not ins_is_regeneration:
                            if "ins_confirmations" in st.session_state:
                                del st.session_state["ins_confirmations"]
                            if "ins_last_confirmation" in st.session_state:
                                del st.session_state["ins_last_confirmation"]
                            st.session_state["ins_last_confirmed_inputs"] = None
                        
                        # Track input history for regeneration detection
                        if "ins_input_history" not in st.session_state:
                            st.session_state["ins_input_history"] = set()
                        st.session_state["ins_input_history"].add(ins_current_inputs_key)
                        
                        if "ins_generation_count" not in st.session_state:
                            st.session_state["ins_generation_count"] = 0
                        st.session_state["ins_generation_count"] += 1
                        
                        if ins_is_regeneration:
                            st.toast("✅ Insurance summary regenerated!")
                        else:
                            st.toast("✅ Insurance summary generated!")
                        
                        st.rerun()
                        
                    else:
                        st.error(f"❌ Error: {ins_response.status_code}")
                        st.json(ins_response.json())
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        if "ins_last_result" in st.session_state:
            result = st.session_state["ins_last_result"]
            document = result["document"]
            metadata = result.get("metadata", {})
            cdt_codes = result.get("cdt_codes", [])
            
            # Insurance Summary Header
            st.markdown("**Insurance Summary (Draft – Admin Use Only)**")
            
            # Editable summary text
            ins_gen_key = st.session_state.get("ins_generation_count", 0)
            edited_summary = st.text_area(
                "Summary Text",
                value=document["insurance_summary"],
                height=250,
                key=f"ins_edited_summary_{ins_gen_key}",
                label_visibility="collapsed"
            )
            
            original_summary = document["insurance_summary"]
            is_edited = edited_summary != original_summary
            
            if is_edited:
                st.info("✏️ Summary has been edited")

            ins_confirm_notes = st.text_area(
                "Approval Notes (optional)",
                placeholder="Optional approval notes...",
                max_chars=1000,
                key=f"ins_confirm_notes_{ins_gen_key}",
            )

            ins_generation_id = result.get("uuid")
            ins_approve_disabled = not ins_generation_id
            ins_approve_button = st.button(
                "✅ Approve (Log Confirmation)",
                type="secondary",
                use_container_width=True,
                disabled=ins_approve_disabled,
                key=f"ins_approve_{ins_gen_key}",
            )

            if ins_approve_button:
                st.session_state["ins_pending_approve"] = True
                st.session_state["ins_pending_generation_id"] = ins_generation_id
                st.session_state["ins_pending_confirm_notes"] = ins_confirm_notes
                confirmed_payload = {
                    "insurance_summary": edited_summary,
                    "cdt_codes": cdt_codes  # List of code strings from the generation response
                }
                st.session_state["ins_pending_confirmed_payload"] = confirmed_payload
                st.rerun()

            if st.session_state.get("ins_pending_approve") and st.session_state.get("ins_pending_generation_id") == ins_generation_id:
                st.warning("Are you sure you want to approve/confirm this document?", icon="⚠️")
                ins_confirm_col, ins_cancel_col = st.columns([1, 1])
                with ins_confirm_col:
                    ins_confirm_now = st.button(
                        "Yes, confirm",
                        type="primary",
                        use_container_width=True,
                        key=f"ins_confirm_yes_{ins_gen_key}",
                    )
                with ins_cancel_col:
                    ins_cancel_now = st.button(
                        "Cancel",
                        type="secondary",
                        use_container_width=True,
                        key=f"ins_confirm_cancel_{ins_gen_key}",
                    )

                if ins_cancel_now:
                    st.session_state["ins_pending_approve"] = False
                    st.session_state["ins_pending_generation_id"] = None
                    st.session_state["ins_pending_confirm_notes"] = None
                    st.session_state["ins_pending_confirmed_payload"] = None
                    st.rerun()

                if ins_confirm_now:
                    try:
                        confirm_response = requests.post(
                            f"{API_BASE_URL}/api/v1/documents/{ins_generation_id}/confirm",
                            json={
                                "confirmed_payload": st.session_state.get("ins_pending_confirmed_payload"),
                                "notes": st.session_state.get("ins_pending_confirm_notes") or None,
                            },
                            timeout=30,
                        )

                        if confirm_response.status_code == 200:
                            confirmation_data = confirm_response.json()

                            if "ins_confirmations" not in st.session_state:
                                st.session_state["ins_confirmations"] = []
                            st.session_state["ins_confirmations"].append(confirmation_data)
                            st.session_state["ins_last_confirmation"] = confirmation_data
                            st.session_state["ins_last_confirmed_inputs"] = ins_current_inputs_key

                            st.session_state["ins_pending_approve"] = False
                            st.session_state["ins_pending_generation_id"] = None
                            st.session_state["ins_pending_confirm_notes"] = None
                            st.session_state["ins_pending_confirmed_payload"] = None

                            st.toast("✅ Document approved and logged")
                            st.rerun()
                        else:
                            st.error(f"❌ Approval failed: {confirm_response.status_code}")
                            try:
                                st.json(confirm_response.json())
                            except Exception:
                                st.write(confirm_response.text)
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # Show all confirmations for this input set
            if "ins_confirmations" in st.session_state and st.session_state["ins_confirmations"]:
                with st.expander(f"✅ Approval / Confirmation History ({len(st.session_state['ins_confirmations'])} approvals)"):
                    for idx, conf in enumerate(reversed(st.session_state["ins_confirmations"]), 1):
                        st.markdown(f"**Approval #{len(st.session_state['ins_confirmations']) - idx + 1}** (Generation: `{conf.get('generation_id', 'N/A')[:8]}...`)")
                        st.json(conf)
                        if idx < len(st.session_state["ins_confirmations"]):
                            st.markdown("---")
            
            # CDT Codes Section
            if cdt_codes:
                st.markdown("---")
                st.markdown("**🏥 Referenced CDT Codes (for administrative reference)**")
                for code_info in cdt_codes:
                    # Backward compatible:
                    # - New API returns List[str]
                    # - Old API returned List[dict] with code/description/category
                    if isinstance(code_info, str):
                        st.markdown(f"🟢 `{code_info}`")
                        continue

                    if isinstance(code_info, dict):
                        category_badge = "🔵" if code_info.get("category") == "primary" else "🟢"
                        code = code_info.get("code", "")
                        desc = code_info.get("description", "")
                        if desc:
                            st.markdown(f"{category_badge} `{code}` – {desc}")
                        else:
                            st.markdown(f"{category_badge} `{code}`")
                        continue

                    st.markdown(f"🟢 `{str(code_info)}`")
                
                if metadata.get("cdt_notes"):
                    st.caption(f"ℹ️ {metadata['cdt_notes']}")
            
            # Disclaimer
            st.markdown("---")
            st.warning(document.get("disclaimer", "This document is provided for administrative support only."))
            
            # Metadata
            with st.expander("📊 Metadata"):
                metadata_display = metadata.copy()
                if result.get("uuid"):
                    metadata_display["uuid"] = result["uuid"]
                if result.get("is_regenerated"):
                    metadata_display["is_regenerated"] = result["is_regenerated"]
                st.json(metadata_display)
            
            with st.expander("📋 Full JSON Response"):
                st.json(result)
            
            # Download button
            download_data = {
                "success": result["success"],
                "document": document,
                "cdt_codes": cdt_codes,
                "metadata": metadata,
                "input_parameters": st.session_state.get("ins_last_payload", {}),
                "is_edited": is_edited,
                "edited_summary": edited_summary if is_edited else ""
            }
            
            st.download_button(
                label="💾 Download JSON",
                data=json.dumps(download_data, indent=2, ensure_ascii=False),
                file_name=f"insurance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="ins_download"
            )

# ============================================================================
# FOOTER SECTION (Outside tabs)
# ============================================================================
st.divider()

with st.expander("ℹ️ About This Demo"):
    st.markdown("""
    ### Purpose
    This Streamlit app is an **optional demo tool** for validating and demonstrating the BiteSoft AI Document Generation API.
    
    ### Available Modules
    - **Treatment Summary**: Patient-facing or internal treatment explanations
    - **Insurance Summary**: Admin-facing insurance documentation support
    
    ### Important Notes
    - **Not required for production** - The FastAPI service works independently
    - **For validation only** - Portal team handles actual UI integration
    - **Demo purposes** - Shows API capabilities and output format
    
    ### Insurance Summary Notes
    - This is NOT a diagnosis, claim submission, or coverage guarantee
    - CDT codes are selected deterministically based on tier and age
    - Tone is always neutral, factual, and non-promissory
    
    ### How to Run
    ```bash
    # Start FastAPI server
    uvicorn app.main:app --reload
    
    # In another terminal, start Streamlit demo
    streamlit run streamlit_demo.py
    ```
    """)

with st.expander("🔧 API Health Check"):
    if st.button("Check API Status", key="health_check"):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is running")
                st.json(response.json())
            else:
                st.error(f"❌ API returned status {response.status_code}")
        except:
            st.error("❌ API is not reachable. Start the FastAPI server first.")
