import os
import json
import subprocess
import argparse
from collections import defaultdict
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import threading

LOG_FILE = "cursor_ai_log.txt"

# Function to find the Xcode project root (assumes .xcodeproj folder exists)
def find_project_root():
    current_dir = os.getcwd()
    while current_dir != "/":
        if any(fname.endswith(".xcodeproj") for fname in os.listdir(current_dir)):
            return current_dir  # Found the Xcode project root
        current_dir = os.path.dirname(current_dir)  # Move up one level
    return os.getcwd()  # Default to current directory if not found

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Generate AI context for SwiftUI projects")
parser.add_argument("--root", type=str, help="Manually specify the project root folder")
args = parser.parse_args()

# Determine project root (default: auto-detect)
PROJECT_ROOT = args.root if args.root else find_project_root()
print(f"📍 Project Root Set To: {PROJECT_ROOT}")

# Global flag for tracking last modification time
last_modified_time = 0
lock = threading.Lock()

# Function to log AI context loading (Prints to Terminal)
def log_context_updates(loaded_files):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - 🔍 AI Loaded Context: {', '.join(loaded_files)}"
    print(log_message)

# Extract AST using sourcekitten and debug AST output
def analyze_swift_file(file_path):
    print(f"🔍 Analyzing {file_path}...")

    # Run sourcekitten to get AST data
    result = subprocess.run(["sourcekitten", "structure", "--file", file_path], capture_output=True, text=True)

    try:
        ast_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse {file_path}")
        return {}

    dependencies = defaultdict(list)

    # Deep recursive function to traverse AST nodes
    def traverse(node, parent=None):
        kind = node.get("key.kind", "")
        name = node.get("key.name", "")

        if not kind:
            return

        if kind == "source.lang.swift.import":
            dependencies["imports"].append(name)

        elif kind == "source.lang.swift.decl.var.global":
            dependencies["globalVariables"].append(name)

        elif kind == "source.lang.swift.decl.var.static" and "shared" in name.lower():
            dependencies["singletons"].append(name)

        elif kind == "source.lang.swift.decl.function.method.static":
            dependencies["staticFunctions"].append(name)

        elif kind == "source.lang.swift.expr.call":
            dependencies["functionCalls"].append(name)

        elif kind == "source.lang.swift.decl.var.instance":
            attributes = node.get("key.attributes", [])
            for attr in attributes:
                if attr.get("key.attribute") == "source.decl.attribute.@EnvironmentObject":
                    dependencies["environmentObjects"].append(name)
                elif attr.get("key.attribute") == "source.decl.attribute.@StateObject":
                    dependencies["stateObjects"].append(name)
                elif attr.get("key.attribute") == "source.decl.attribute.@ObservedObject":
                    dependencies["observedObjects"].append(name)
                elif attr.get("key.attribute") == "source.decl.attribute.@AppStorage":
                    dependencies["appStorageKeys"].append(name)

        elif kind == "source.lang.swift.decl.class" and "NSManagedObject" in node.get("key.inheritedtypes", []):
            dependencies["coreDataModels"].append(name)

        elif kind == "source.lang.swift.expr.call" and "UserDefaults" in name:
            dependencies["userDefaultsKeys"].append(name)

        elif kind == "source.lang.swift.expr.call" and "URLSession" in name:
            dependencies["networkClients"].append(name)

        elif kind == "source.lang.swift.expr.call" and any(kw in name.lower() for kw in ["log", "debug", "trace", "print"]):
            dependencies["loggers"].append(name)

        # Process deeper structures
        for sub_node in node.get("key.substructure", []):
            traverse(sub_node, parent=name)

    for root_node in ast_data.get("key.substructure", []):
        traverse(root_node)

    if dependencies:
        print(f"✅ Extracted Data from {file_path}: {dependencies}")

    return dependencies

# Function to generate dependency JSON
def generate_dependency_json():
    project_dependencies = defaultdict(dict)

    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".swift"):
                file_path = os.path.join(root, file)
                file_dependencies = analyze_swift_file(file_path)

                if file_dependencies:
                    project_dependencies[file] = file_dependencies

    if project_dependencies:
        with open("dependencies.json", "w") as f:
            json.dump(project_dependencies, f, indent=4)
        print("✅ AI Context Dependency Graph Updated")
    else:
        print("❌ No dependencies extracted. Something is wrong!")

# Function to simulate AI context loading & log it
def simulate_ai_context_loading():
    if not os.path.exists("dependencies.json"):
        print("❌ dependencies.json not found. Running dependency update now...")
        generate_dependency_json()

    with open("dependencies.json", "r") as f:
        dependencies = json.load(f)

    loaded_files = []
    max_files = 5  # Match `.cursorrules` settings

    for file, data in dependencies.items():
        if len(loaded_files) >= max_files:
            break
        loaded_files.append(file)

    log_context_updates(loaded_files)

# Watchdog: Watches for file changes and updates AI context
class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_modified_time
        if event.src_path.endswith(".swift"):
            with lock:
                last_modified_time = time.time()

# Monitor edits and delay dependency generation
def monitor_cursor_edits():
    """Waits for Cursor AI to finish modifying files before regenerating dependencies.json"""
    global last_modified_time  

    while True:
        with lock:
            if last_modified_time != 0 and time.time() - last_modified_time >= 3:
                print("🔄 Cursor AI finished editing. Updating AI context...")
                generate_dependency_json()
                last_modified_time = 0  # Reset

        time.sleep(1)  # Prevents high CPU usage

def watch_project():
    observer = Observer()
    event_handler = FileChangeHandler()
    observer.schedule(event_handler, PROJECT_ROOT, recursive=True)
    observer.start()

    print("👀 Watching for Cursor AI edits... (Batch updates every 3 seconds)")
    monitor_thread = threading.Thread(target=monitor_cursor_edits, daemon=True)
    monitor_thread.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    print(f"📍 Project Root Set To: {PROJECT_ROOT}")
    generate_dependency_json()  # **Ensures dependencies.json is created when the script starts**
    watch_project()  # Keep script running and delay AI context updates until edits are finished
