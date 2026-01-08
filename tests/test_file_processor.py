import os
import tempfile
import unittest
from FastWrite import file_processor

class TestFileProcessor(unittest.TestCase):
    def test_list_code_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create some dummy files
            open(os.path.join(tmp_dir, "test1.py"), "w").close()
            open(os.path.join(tmp_dir, "test2.txt"), "w").close()
            os.makedirs(os.path.join(tmp_dir, "subdir"))
            open(os.path.join(tmp_dir, "subdir", "test3.js"), "w").close()
            
            files = file_processor.list_code_files(tmp_dir)
            self.assertIn("test1.py", files)
            self.assertIn("subdir/test3.js", files)
            self.assertNotIn("test2.txt", files)

    def test_read_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
            tmp_file.write("print('hello')")
            tmp_path = tmp_file.name
        
        try:
            content = file_processor.read_file(tmp_path)
            self.assertEqual(content, "print('hello')")
        finally:
            os.remove(tmp_path)
