import os

def list_files_by_folder(base_path="."):
    base_path = os.path.abspath(base_path)
    print(f"\n📂 Root: {base_path}\n")

    for root, dirs, files in os.walk(base_path):
        rel_root = os.path.relpath(root, base_path)
        if rel_root == ".":
            rel_root = "forex-backend"
        print(f"📂 {rel_root}/")

        if not files:
            print("  (empty)")
        else:
            for f in sorted(files):
                print(f"  - {f}")
        print()

if __name__ == "__main__":
    list_files_by_folder(".")
