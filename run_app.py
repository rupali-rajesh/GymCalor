import os
import subprocess
import sys
import time

def main():
    python_exec = sys.executable

    print("Starting FastAPI backend on port 8002...")
    backend_proc = subprocess.Popen([python_exec, "-m", "uvicorn", "backend:app", "--port", "8002", "--host", "0.0.0.0"])
    
    # Wait a bit for backend to initialize
    time.sleep(3)

    print("Starting Streamlit frontend (port auto-assigned)...")
    frontend_proc = subprocess.Popen([python_exec, "-m", "streamlit", "run", "app.py"])

    print("Both servers are running. Press Ctrl+C to terminate.")
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("Shutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
