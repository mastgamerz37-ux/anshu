import os
import shutil
import subprocess

def main():
    print("Building executable with PyInstaller...")
    cmd = [
        "py", "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", "AnshAI",
        "--add-data", "dashboard/static;dashboard/static",
        "main.py"
    ]
    subprocess.run(cmd, check=True)

    print("Creating release folder...")
    release_dir = "AnshAI_Release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    print("Copying files to release folder...")
    shutil.copytree(os.path.join("dist", "AnshAI"), release_dir)
    
    # Copy extra files
    if os.path.exists("face.png"):
        shutil.copy("face.png", release_dir)
    os.makedirs(os.path.join(release_dir, "core"), exist_ok=True)
    if os.path.exists(os.path.join("core", "prompt.txt")):
        shutil.copy(os.path.join("core", "prompt.txt"), os.path.join(release_dir, "core"))
    
    print("Done! You can now run Inno Setup on setup.iss")

if __name__ == "__main__":
    main()
