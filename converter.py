
import pickle
import joblib
import os
import tempfile
import humanize


def format_bytes(size):
    """Format bytes to human readable string."""
    return humanize.naturalsize(size)


def convert_pickle_to_joblib(input_bytes: bytes, compress: int = 3) -> tuple[bytes, int, int]:
    """
    Convert pickle bytes to joblib bytes.
    
    Returns:
        tuple: (joblib_bytes, original_size, compressed_size)
    """
    original_size = len(input_bytes)
    

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pickle") as tmp_in:
        tmp_in.write(input_bytes)
        tmp_in_path = tmp_in.name
    
    try:

        with open(tmp_in_path, 'rb') as f:
            obj = pickle.load(f)
        

        with tempfile.NamedTemporaryFile(delete=False, suffix=".joblib") as tmp_out:
            tmp_out_path = tmp_out.name
        
        joblib.dump(obj, tmp_out_path, compress=compress)
        

        with open(tmp_out_path, "rb") as f:
            joblib_bytes = f.read()
        
        compressed_size = len(joblib_bytes)
        
        return joblib_bytes, original_size, compressed_size
    
    finally:

        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)
        if 'tmp_out_path' in locals() and os.path.exists(tmp_out_path):
            os.remove(tmp_out_path)


def calculate_reduction(original_size: int, new_size: int) -> float:
    """Calculate percentage reduction in size."""
    if original_size == 0:
        return 0.0
    return 100 - ((new_size / original_size) * 100)


def generate_output_filename(input_filename: str) -> str:
    """Convert .pickle/.pck filename to .joblib."""
    base = os.path.splitext(input_filename)[0]
    return f"{base}.joblib"