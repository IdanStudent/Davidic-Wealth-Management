import subprocess
import sys
import os
import time
import webbrowser
from urllib.request import urlopen

ROOT = os.path.dirname(__file__)
VENV_PY = sys.executable

def start_backend():
    cmd = [VENV_PY, '-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '0.0.0.0', '--port', '8000', '--reload']
    print('Starting backend:', ' '.join(cmd))
    return subprocess.Popen(cmd, cwd=ROOT)

def start_frontend():
    npm = shutil_which('npm')
    if not npm:
        print('npm not found on PATH; please run frontend manually (cd frontend; npm run dev)')
        return None
    cmd = [npm, 'run', 'dev']
    print('Starting frontend:', ' '.join(cmd))
    return subprocess.Popen(cmd, cwd=os.path.join(ROOT, 'frontend'))

def shutil_which(name):
    from shutil import which
    return which(name)

def wait_for(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urlopen(url, timeout=2) as r:
                return True
        except Exception:
            time.sleep(0.5)
    return False

def main():
    backend = start_backend()
    try:
        if wait_for('http://localhost:8000/'):
            print('Backend ready')
        else:
            print('Backend did not start in time')
    except Exception as e:
        print('Backend check failed:', e)

    frontend = None
    try:
        frontend = start_frontend()
        # Vite default port
        if wait_for('http://localhost:5173/'):
            print('Frontend ready')
            webbrowser.open('http://localhost:5173')
        else:
            print('Frontend did not start in time; open http://localhost:5173 manually')
    except Exception as e:
        print('Frontend start failed:', e)

    try:
        print('Press Ctrl+C to stop')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Shutting down...')
    finally:
        if frontend:
            frontend.terminate()
        if backend:
            backend.terminate()

if __name__ == '__main__':
    main()
