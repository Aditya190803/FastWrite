import unittest
from FastWrite import data_flow

class TestDataFlow(unittest.TestCase):
    def test_generate_data_flow(self):
        code = """
x = 10
def my_func():
    y = 20
    z = x + y
    return z
"""
        graph_code = data_flow.generate_data_flow(code)
        self.assertIn("digraph G", graph_code)
        self.assertIn('"Global"', graph_code)
        self.assertIn('"x" [shape=box];', graph_code)
        self.assertIn('"my_func"', graph_code)
        self.assertIn('"y"', graph_code)
        self.assertIn('"Global" -> "x";', graph_code)
        self.assertIn('"my_func" -> "y";', graph_code)
