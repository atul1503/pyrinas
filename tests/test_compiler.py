import subprocess
import os
import pytest

# It is not testing the CLI, but the compiler's output
# an elegant solution would be to create a temporary file and then compile it
# but for now, we can just use the examples folder
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), '..', 'examples')
# a list of all the examples to be tested
# the format is (example_name, expected_output)
EXAMPLES = [
    ('expressions', '13.500000\n5\n7.000000\n2.500000\n1\n0\n'),
    ('for_loop', '0\n1\n2\n3\n4\n5\n'),
    ('functions', '8\n'),
    ('if_else', 'x is greater than y\nx is 10\ny is not 10\n'),
    ('logical_ops', '0\n1\n1\n1\n'),
    ('variables', '10\n3.140000\n'),
    ('while_loop', '0\n1\n2\n3\n4\n'),
    ('hello', 'Hello, Pyrinas!\n'),
    ('break', '0\n1\n2\n3\n4\n'),
    ('continue', '1\n3\n5\n7\n9\n'),
    ('labeled_break', '0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n0\n2\n4\n6\n8\n10\n12\n14\n16\n18\n0\n3\n6\n9\n12\n15\n18\n21\n24\n27\n0\n4\n8\n12\n16\n20\n24\n28\n'),
    ('pointers', '42\n100\n'),
    ('multilevel_pointers', '42\n100\n50\n'),
    ('memory', '255\n'),
]

@pytest.mark.parametrize("example, expected_output", EXAMPLES)
def test_example(example, expected_output):
    """
    Tests a single example from the examples folder.
    """
    input_file = os.path.join(EXAMPLES_DIR, f'{example}.py')
    output_executable = os.path.join(EXAMPLES_DIR, f'{example}')
    
    # Compile the example
    subprocess.run(['python3', '-m', 'pyrinas.cli', input_file, '-o', output_executable], check=True)
    
    # Run the compiled executable and capture the output
    result = subprocess.run([output_executable], capture_output=True, text=True, check=True)
    
    # a.out and its .c file are temporary files, so they should be removed
    os.remove(output_executable)
    os.remove(f'{output_executable}.c')

    assert result.stdout == expected_output