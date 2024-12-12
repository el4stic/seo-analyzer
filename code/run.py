import os
import sys
import subprocess

# Set environment variables to bypass Streamlit's email collection
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_PORT'] = '8502'
os.environ['STREAMLIT_SERVER_ADDRESS'] = '127.0.0.1'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'true'

# Get the Python executable path
python_path = sys.executable

# Run streamlit with minimal flags
cmd = [
    python_path,
    "-m",
    "streamlit",
    "run",
    "app.py",
    "--server.port=8502",
    "--server.address=127.0.0.1",
    "--server.headless=true"
]

# Run the command
subprocess.run(cmd) 