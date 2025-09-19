@echo off
:: Activate virtual environment
call venv\Scripts\activate.bat   :: Change to match the path to your virtual environment on Windows

:: Run the Python app
python -m streamlit run "FULL PATH HERE\cocobot\project_contents\Home.py" --server.port 8000 --server.address 127.0.0.2

