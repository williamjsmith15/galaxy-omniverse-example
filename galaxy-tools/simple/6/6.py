"""
This script takes a string via commandline argument and writes it to a file.
"""

import argparse

parser = argparse.ArgumentParser(prog="2-7.py", description='Take input, write to file.')
parser.add_argument('Text_To_Write', help='Text to write to file')
parser.add_argument('file_to_append', help='text file to append')
parser.add_argument('Output_File', help='Name of file to write to')


args = parser.parse_args()

text_to_write = args.Text_To_Write
append_file = args.file_to_append
output_file = args.Output_File

text_to_append = ""
with open(append_file, 'r') as readfile:
    text_to_append = readfile.read()



with open(output_file, 'w', encoding='utf8') as f:
    f.write(text_to_write + text_to_append)