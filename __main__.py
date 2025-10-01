from argparse import ArgumentParser
import subprocess

input_process = subprocess.Popen(
    ['venv/Scripts/python.exe', '-u', 'input.py'], stdout=subprocess.PIPE
)

llm_process = subprocess.Popen(
    ['node', 'llm.js'], stdin=input_process.stdout, stdout=subprocess.PIPE
)

# llm_process = subprocess.Popen(
#     ['node', 'llm.js'], stdout=subprocess.PIPE
# )

output_process = subprocess.Popen(
    ['venv/Scripts/python.exe', '-u', 'output.py'], stdin=llm_process.stdout
)

llm_process.stdout.close()
output_process.communicate()