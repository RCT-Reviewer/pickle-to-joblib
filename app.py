import streamlit as st
import pickle
import joblib
import os
import sys
import tempfile
import humanize
import importlib

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

def format_bytes(size):
    return humanize.naturalsize(size)

if uploaded_files:
    st.info(f"Found {len(uploaded_files)} file(s) to convert.")
    
    progress_bar = st.progress(0)
    
    for i, uploaded_file in enumerate(uploaded_files):
        # Calculate progress
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        
        with st.expander(f"**Processing: {uploaded_file.name}**", expanded=True):
            try:
         
                original_size = uploaded_file.size
                st.text(f"Original Size: {format_bytes(original_size)}")
                
                
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
                    tmp_in.write(uploaded_file.getbuffer())
                    tmp_in_path = tmp_in.name
                
                
                with open(tmp_in_path, 'rb') as f:
                    obj = pickle.load(f)
                
            
                with tempfile.NamedTemporaryFile(delete=False, suffix=".joblib") as tmp_out:
                    tmp_out_path = tmp_out.name
                
                joblib.dump(obj, tmp_out_path, compress=3)
                
            
                new_size = os.path.getsize(tmp_out_path)
                reduction = 100 - ((new_size / original_size) * 100)
                
                st.metric(
                    label="Compressed Size", 
                    value=format_bytes(new_size),
                    delta=f"-{reduction:.1f}% size reduction"
                )
                
      
                with open(tmp_out_path, "rb") as f:
                    joblib_bytes = f.read()

                new_filename = os.path.splitext(uploaded_file.name)[0] + ".joblib"
                
                st.download_button(
                    label=f"⬇️ Download {new_filename}",
                    data=joblib_bytes,
                    file_name=new_filename,
                    mime="application/octet-stream",
                    key=f"dl_{uploaded_file.name}_{i}"
                )
                
   
                os.remove(tmp_in_path)
                os.remove(tmp_out_path)

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