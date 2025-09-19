import streamlit as st 
from PIL import Image
import base64
import pandas as pd
import streamlit as st
from util_functions import *
from streamlit_option_menu import option_menu
from streamlit_tree_select import tree_select
import os
import json
import subprocess
import psutil
import time
import pygetwindow as gw
import pyautogui
import random
import threading
from dotenv import load_dotenv


load_dotenv()
SCRIPT_PATH = "random_trigger.py"  # Path to your random entrance script

# Ensure session state exists
if "script_pid" not in st.session_state:
    st.session_state.script_pid = None
if "log_lines" not in st.session_state:
    st.session_state.log_lines = []  # Stores console logs

    

# Function to check if the script is running
def is_script_running():
    """Check if the stored PID is active."""
    if st.session_state.script_pid:
        try:
            proc = psutil.Process(st.session_state.script_pid)
            return proc.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            st.session_state.script_pid = None  # Reset if process is gone
    return False

# Function to read subprocess output in real-time
def stream_output(process):
    """Reads and stores output from the subprocess."""
    if "log_lines" not in st.session_state:
        st.session_state.log_lines = []  # Stores console logs

    for line in iter(process.stdout.readline, ''):  # Reads line by line
        st.session_state.log_lines.append(line.strip())  # Store log lines
        st.rerun()  # Refresh UI to show new logs
    process.stdout.close()

# Function to start the script
def start_script():
    """Starts the script, captures output, and tracks PID."""
    if not is_script_running():
        try:
            process = subprocess.Popen(
                ["python", "-u", SCRIPT_PATH],  # `-u` forces unbuffered output
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,  # Ensures text output (not bytes)
                bufsize=1  # Line buffering
            )
            st.session_state.script_pid = process.pid
            if "log_lines" not in st.session_state:
                st.session_state.log_lines = []  # Stores console logs

            st.session_state.log_lines.append(f"✅ Started script (PID: {process.pid})")

            # Start a thread to capture logs
            thread = threading.Thread(target=stream_output, args=(process,), daemon=True)
            thread.start()
        except Exception as e:
            st.error(f"Failed to start script: {e}")

# Function to stop the script
def stop_script():
    """Stops the script if it's running."""
    if "log_lines" not in st.session_state:
        st.session_state.log_lines = []  # Stores console logs

    if is_script_running():
        try:
            os.kill(st.session_state.script_pid, 9)  # Force kill process
            st.session_state.script_pid = None
            st.session_state.log_lines.append("❌ Script stopped.")
            st.rerun()
        except Exception as e:
            st.error(f"Error stopping script: {e}")

def sample_dict(data: dict[str, list], n: int) -> dict[str, list]:
    return {
        key: random.sample(values, n)   # no replacement
        for key, values in data.items()
        if len(values) >= n             # avoid errors if list too short
    }

# Get the directory where the main script is located
script_directory = os.path.dirname(os.path.abspath(__file__))
# Set the current working directory to the script's directory
os.chdir(script_directory)

st.set_page_config(page_title="CocoBot Interface", page_icon=":coconut:", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
        /* Set the background color to white */
        body {
            background-color: white !important;
        }
        /* Remove the Streamlit default gray background */
        .stApp {
            background-color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)



col1, col2,col3 = st.columns([1,10,1])

with st.container():
    col1.image("assets/coconuts.png",width=100)

    col2.markdown("""
        <h1>CocoBot - Graphical User Interface</h1>
        <p class="subtext">Bababooeying since 2021.</p>
        """, unsafe_allow_html=True)



st.markdown("""
<style>
    .stApp {
        background-image: url("https://www.freshworks.com/static-assets/images/pattern.svg?bcce5df45a3eef1232095a82b2bbc1f1");
        background-size: cover;
            width: 100%;
    }
</style>
        """, unsafe_allow_html=True)


if st.button("Kill myself 🤡"):
    window = gw.getWindowsWithTitle("cocobot app")
    if window:
        window[0].close()  # Tries to close the window



col1, col2, col3 = st.columns(3)



# Path to the sound folder
sound_folder = r"sounds"

# Build the file tree and convert it to tree_select nodes
file_tree = build_file_tree(sound_folder)
nodes = tree_to_treeselect(file_tree)
# Iterate through the dictionary
rows = []

for Folder in file_tree.keys():
    if Folder not in ['desktop.ini']:
        inner_dict=file_tree[Folder]
        for File in inner_dict.keys():
            value=inner_dict[File]
            rows.append([Folder, File])

# Create a DataFrame
df_files = pd.DataFrame(rows, columns=['Folder', 'File'])
df_files['Path'] = df_files['Folder'] + '/' + df_files['File']
df_files['Name'] = df_files['File'].str.split('.').str[0]

try:
    console_string  # Check if it exists
except NameError:
    console_string = ""

with col1:

    bot_col1, text_col1 = st.columns([1, 9])  # Adjust ratio as needed
    with bot_col1:
        st.image('assets/butler_avatar.png',width=100)  # Bot Avatar
    with text_col1:
        st.subheader("Cocobot Butler")  # Title next to image



    st.markdown("""<p class="subtext">Select sound files from tree:</p>""", unsafe_allow_html=True)
    # Use tree_select with appropriate arguments
    selected_files = tree_select(
        nodes=nodes,         # Hierarchical data
        check_model="all",   # Return all selected nodes
        checked=None,        # No pre-selected nodes
        expand_on_click=True, # Enable expanding nodes when clicked
        show_expand_all=True # Show "Expand All" button
    )

    checked_files=selected_files["checked"]


    multiselect_files=st.multiselect(
    'or select by text search',
    df_files['Name'].tolist(),
    default=[],
    )


    df_selected_paths = df_files[df_files['File'].isin(checked_files) | df_files['Name'].isin(multiselect_files)]  
    selected_paths=df_selected_paths['Path'].tolist()


    selected_paths_str = json.dumps(selected_paths)






    if st.button('Call CocoBot'):
        # When the button is pressed, run the subprocess
        with st.spinner():
            result = subprocess.run(
            ['python', 'manual_trigger.py', selected_paths_str],  # Pass the JSON string to the subprocess
            capture_output=True, 
            text=True
            )
            print(result)
            # Check the return code to see if the subprocess ran successfully
            if result.returncode == 0:
                print(f"Subprocess ran successfully:\n{result.stdout}")
            else:
                print(f"Subprocess failed with error:\n{result.stderr}")

# Column 2: Auto Mode
with col2:
    bot_col2, text_col2 = st.columns([1, 9])  # Adjust ratio as needed
    with bot_col2:
        st.image('assets/prime_avatar.png',width=100)  # Bot Avatar
    with text_col2:
        st.subheader("Cocobot Prime")  # Title next to image

    # Check if script is running
    script_running = is_script_running()

    if not script_running:
        start_script()
        st.rerun()
    else:
        st.success(f"✅ Script is running! (PID: {st.session_state.script_pid})")
        if st.button("Stop Script"):
            stop_script()
            st.rerun()
    if st.button("Refresh Console"):
        with open('logs/random_log.txt', 'r') as file:
            console_string = file.read()
    st.code(console_string, language="bash")




# Column 3:  Genshin Weekly
with col3:
    bot_col3, text_col3 = st.columns([1, 9])  # Adjust ratio as needed
    with bot_col3:
        st.image('assets/randomizer_avatar.png',width=100)  # Bot Avatar
    with text_col3:
        st.subheader("Cocobot Randomizer")  # Title next to image

    randomizer_parameters=os.getenv("randomizer_parameters")
    rand_parsed=json.loads(randomizer_parameters)    

    if st.button("Roll"):
        selected_challenges=sample_dict(rand_parsed,3)
        df_selected_challenges=pd.DataFrame(selected_challenges)
        st.dataframe(df_selected_challenges,width='stretch')

