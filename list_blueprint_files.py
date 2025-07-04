import os

EXCLUDED_DIRS = {"venv", "__pycache__"}

def list_local_code_files(base_path):
    base_path = os.path.abspath(base_path)
    print(f"\n📂 Scanning .py and .txt files under: {base_path}")
    print("🧾 Ignoring: venv\\, __pycache__\\\n")

    for root, dirs, files in os.walk(base_path):
        # Skip excluded folders
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if file.endswith((".py", ".txt")):
                full_path = os.path.join(root, file)
                print(full_path)

if __name__ == "__main__":
    # Set this to your actual path if not running from forex-backend root
    list_local_code_files(r"C:\Users\PC\forex-backend")
