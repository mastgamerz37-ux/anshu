import psutil
for p in psutil.process_iter(['name', 'cmdline']):
    try:
        if p.info['cmdline'] and any('main.py' in arg for arg in p.info['cmdline']):
            print(f"Killing {p.pid}")
            p.terminate()
        elif p.info['cmdline'] and any('smart_island.py' in arg for arg in p.info['cmdline']):
            print(f"Killing {p.pid}")
            p.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
