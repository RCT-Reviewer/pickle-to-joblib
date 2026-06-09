import streamlit as st
import pickle
import joblib
import os
import tempfile
from io import BytesIO
import humanize 

def format_bytes(size):
    """Helper to format bytes into readable string (KB, MB, GB)"""
    return humanize.naturalsize(size)

st.set_page_config(page_title="Pickle ➔ Joblib", layout="centered")

st.title("🥒 Pickle to 📦 Joblib Converter")
st.write(
    "Upload your `.pickle` or `.pck` files. This app will compress them using joblib "
    "to reduce file size by 50-80%."
)


uploaded_files = st.file_uploader(
    "Choose pickle files", 
    type=['pickle', 'pck'], 
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Found {len(uploaded_files)} file(s) to convert.")
    
   
    for uploaded_file in uploaded_files:
        with st.expander(f"**Processing: {uploaded_file.name}**", expanded=True):
            try:
               
                original_size = uploaded_file.size
                st.text(f"Original Size: {format_bytes(original_size)}")
                
             
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as tmp_in:
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
                    mime="application/octet-stream"
                )
                
              
                os.remove(tmp_in_path)
                os.remove(tmp_out_path)

            except Exception as e:
                st.error(f"❌ Failed to convert {uploaded_file.name}: {e}")

else:
    st.warning("Please upload files to begin.")