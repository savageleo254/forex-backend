import os

def print_tree(start_path, prefix=""):
    files = []
    dirs = []

    for item in sorted(os.listdir(start_path)):
        if item.startswith("."):  # skip .git, .env, etc. unless needed
            continue
        full_path = os.path.join(start_path, item)
        if os.path.isdir(full_path):
            dirs.append(item)
        else:
            files.append(item)

    for idx, folder in enumerate(dirs):
        is_last = (idx == len(dirs) - 1 and not files)
        connector = "└── " if is_last else "├── "
        print(prefix + connector + folder + "/")
        sub_prefix = "    " if is_last else "│   "
        print_tree(os.path.join(start_path, folder), prefix + sub_prefix)

    for idx, file in enumerate(files):
        connector = "└── " if idx == len(files) - 1 else "├── "
        print(prefix + connector + file)

if __name__ == "__main__":
    root = os.path.abspath(".")  # or set to r"C:\Users\PC\forex-backend"
    print(f"📁 Project Tree: {root}\n")
    print_tree(root)
