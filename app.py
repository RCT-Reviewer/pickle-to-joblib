
import streamlit as st
import os
import sys
import tempfile

from converter import convert_pickle_to_joblib, format_bytes, calculate_reduction, generate_output_filename

st.set_page_config(page_title="Pickle ➔ Joblib", layout="centered")

st.title("🥒 Pickle to 📦 Joblib Converter")
st.write(
    "Upload your `.pickle` or `.pck` files. This app compresses them to reduce size. "
    "If your files use custom classes (like 'rationale_CNN'), upload the missing .py files below first."
)

st.subheader("Custom Dependencies")
st.info(
    "If you see errors like 'No module named X', upload the missing .py file here."
)
dependency_files = st.file_uploader(
    "Upload missing .py modules (Optional)",
    type=['py'],
    accept_multiple_files=True,
    help="e.g., Upload 'rationale_CNN.py' if the error says 'No module named rationale_CNN'"
)

if dependency_files:
    temp_dep_dir = tempfile.mkdtemp()
    if temp_dep_dir not in sys.path:
        sys.path.append(temp_dep_dir)
    
    for dep in dependency_files:
        dep_path = os.path.join(temp_dep_dir, dep.name)
        with open(dep_path, "wb") as f:
            f.write(dep.getbuffer())
        st.success(f"✅ Loaded module: {dep.name}")

st.divider()

uploaded_files = st.file_uploader(
    "Choose pickle files to convert", 
    type=['pickle', 'pck'], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Found {len(uploaded_files)} file(s) to convert.")
    progress_bar = st.progress(0)
    
    for i, uploaded_file in enumerate(uploaded_files):
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        
        with st.expander(f"**Processing: {uploaded_file.name}**", expanded=True):
            try:
                original_size = uploaded_file.size
                st.text(f"Original Size: {format_bytes(original_size)}")
                
                joblib_bytes, orig, comp = convert_pickle_to_joblib(uploaded_file.getbuffer())
                
                reduction = calculate_reduction(orig, comp)
                
                st.metric(
                    label="Compressed Size", 
                    value=format_bytes(comp),
                    delta=f"-{reduction:.1f}% size reduction"
                )
                
                new_filename = generate_output_filename(uploaded_file.name)
                
                st.download_button(
                    label=f"⬇️ Download {new_filename}",
                    data=joblib_bytes,
                    file_name=new_filename,
                    mime="application/octet-stream",
                    key=f"dl_{uploaded_file.name}_{i}"
                )

            except ModuleNotFoundError as e:
                missing_module = str(e).split("'")[-2]
                st.error(f"❌ **Missing Python Module:** `{missing_module}`")
                st.warning(
                    f"This pickle file contains an object defined in a file named `{missing_module}.py`. "
                    f"Please upload that file in the **'Custom Dependencies'** section above and try again."
                )
            
            except Exception as e:
                st.error(f"❌ Failed to convert {uploaded_file.name}")
                st.code(str(e))
                
    progress_bar.empty()
else:
    st.warning("Please upload files to begin.")

st.markdown(
    """
    <div style='text-align: center; margin-top: 50px; color: gray; font-size: 14px;'>
        © aurumz-rgb 2025 – AGPL-3.0 License.
    </div>
    """,
    unsafe_allow_html=True
)