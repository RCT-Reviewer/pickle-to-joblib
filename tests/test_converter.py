
import pickle
import pytest
from converter import (
    format_bytes,
    convert_pickle_to_joblib,
    calculate_reduction,
    generate_output_filename,
)


class TestFormatBytes:
    def test_small_size(self):
        result = format_bytes(500)
        assert "500" in result or "Bytes" in result
    
    def test_kilobyte_size(self):
         result = format_bytes(1024)
         assert "KB" in result.upper() or "KIB" in result.upper()
    
    def test_megabyte_size(self):
        result = format_bytes(1024 * 1024)
        assert "MB" in result or "MiB" in result.lower()
    
    def test_zero_bytes(self):
        result = format_bytes(0)
        assert "0" in result


class TestCalculateReduction:
    def test_fifty_percent_reduction(self):
        assert calculate_reduction(100, 50) == 50.0
    
    def test_no_reduction(self):
        assert calculate_reduction(100, 100) == 0.0
    
    def test_increase_in_size(self):
        result = calculate_reduction(100, 150)
        assert result < 0  
    
    def test_zero_original_size(self):
        assert calculate_reduction(0, 0) == 0.0
    
    def test_complete_reduction(self):
        assert calculate_reduction(100, 0) == 100.0


class TestGenerateOutputFilename:
    def test_pickle_extension(self):
        assert generate_output_filename("model.pickle") == "model.joblib"
    
    def test_pck_extension(self):
        assert generate_output_filename("data.pck") == "data.joblib"
    
    def test_no_extension(self):
        assert generate_output_filename("model") == "model.joblib"
    
    def test_nested_path(self):
        assert generate_output_filename("path/to/model.pickle") == "path/to/model.joblib"
    
    def test_multiple_dots(self):
        assert generate_output_filename("model.v1.pickle") == "model.v1.joblib"


class TestConvertPickleToJoblib:
    def test_simple_dict(self):
        data = {"key": "value", "number": 42}
        pickle_bytes = pickle.dumps(data)
        
        joblib_bytes, orig_size, comp_size = convert_pickle_to_joblib(pickle_bytes)
        
        assert orig_size == len(pickle_bytes)
        assert comp_size > 0
        assert len(joblib_bytes) == comp_size

    def test_list_conversion(self):
        data = [1, 2, 3, 4, 5]
        pickle_bytes = pickle.dumps(data)
        
        joblib_bytes, orig_size, comp_size = convert_pickle_to_joblib(pickle_bytes)
        
        assert orig_size > 0
        assert comp_size > 0

    def test_nested_structure(self):
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ],
            "metadata": {"version": "1.0", "count": 2}
        }
        pickle_bytes = pickle.dumps(data)
        
        joblib_bytes, orig_size, comp_size = convert_pickle_to_joblib(pickle_bytes)
        
        assert orig_size > 0
        assert comp_size > 0

    def test_empty_dict(self):
        data = {}
        pickle_bytes = pickle.dumps(data)
        
        joblib_bytes, orig_size, comp_size = convert_pickle_to_joblib(pickle_bytes)
        
        assert orig_size > 0  
        assert comp_size > 0

    def test_large_repetitive_data_compresses_well(self):
        
        data = {"text": "hello world " * 1000}
        pickle_bytes = pickle.dumps(data)
        
        joblib_bytes, orig_size, comp_size = convert_pickle_to_joblib(pickle_bytes, compress=3)
        
        reduction = calculate_reduction(orig_size, comp_size)
        assert reduction > 0 

    def test_invalid_pickle_raises_exception(self):
        invalid_bytes = b"this is not a valid pickle"
        
        with pytest.raises(Exception):
            convert_pickle_to_joblib(invalid_bytes)

    def test_different_compress_levels(self):
        data = {"value": "test" * 500}
        pickle_bytes = pickle.dumps(data)
        
        _, _, comp_low = convert_pickle_to_joblib(pickle_bytes, compress=0)
        _, _, comp_high = convert_pickle_to_joblib(pickle_bytes, compress=9)
        

        assert comp_high <= comp_low