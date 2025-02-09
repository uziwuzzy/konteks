import os
import json
import subprocess
import graphviz
import re
import plistlib
import argparse
from collections import defaultdict
from datetime import datetime

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

# Function to log AI context loading (Prints to Terminal)
def log_context_updates(loaded_files):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} - 🔍 AI Loaded Context: {', '.join(loaded_files)}"
    print(log_message)

# Extract AST using sourcekitten
def analyze_swift_file(file_path):
    result = subprocess.run(["sourcekitten", "structure", "--file", file_path], capture_output=True, text=True)
    
    try:
        ast_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"❌ Failed to parse {file_path}")
        return {}

    dependencies = {
        "imports": set(),
        "environmentObjects": set(),
        "stateObjects": set(),
        "observedObjects": set(),
        "appStorageKeys": set(),
        "functions": defaultdict(lambda: {"calls": [], "modifies": []}),
        "coreDataModels": set(),
        "userDefaultsKeys": set(),
        "singletons": set(),
        "globalVariables": set(),
        "staticFunctions": set(),
        "networkClients": set(),
        "apiEndpoints": set(),
        "loggers": set(),
        "navigatesTo": set(),
        "triggersOnAppear": set(),
        "configurations": defaultdict(dict),
        "file": file_path  # Store file reference
    }

    def traverse(node, parent=None):
        kind = node.get("kind", "")
        name = node.get("name", "")

        if kind == "source.lang.swift.import":
            dependencies["imports"].add(name)

        if kind == "source.lang.swift.decl.var.global":
            dependencies["globalVariables"].add(name)

        if kind == "source.lang.swift.decl.var.static" and "shared" in name.lower():
            dependencies["singletons"].add(name)

        if kind == "source.lang.swift.decl.function.method.static":
            dependencies["staticFunctions"].add(name)

        if kind == "source.lang.swift.expr.call" and parent:
            dependencies["functions"][parent]["calls"].append(name)

        if kind == "source.lang.swift.decl.var.instance":
            attributes = node.get("attributes", [])
            for attr in attributes:
                if attr.get("name") == "EnvironmentObject":
                    dependencies["environmentObjects"].add(name)
                elif attr.get("name") == "StateObject":
                    dependencies["stateObjects"].add(name)
                elif attr.get("name") == "ObservedObject":
                    dependencies["observedObjects"].add(name)
                elif attr.get("name") == "AppStorage":
                    dependencies["appStorageKeys"].add(name)

        if kind == "source.lang.swift.decl.class" and "NSManagedObject" in node.get("inheritedtypes", []):
            dependencies["coreDataModels"].add(name)

        if kind == "source.lang.swift.expr.call" and "UserDefaults" in name:
            key_match = node.get("key.usr", "").split(".")[-1]
            if key_match:
                dependencies["userDefaultsKeys"].add(key_match)

        if kind == "source.lang.swift.expr.call" and "URLSession" in name:
            dependencies["networkClients"].add("Detected Networking Code")

        if kind == "source.lang.swift.expr.call" and any(kw in name.lower() for kw in ["log", "debug", "trace", "print"]):
            dependencies["loggers"].add("Detected Logging Code")

        for sub_node in node.get("substructure", []):
            traverse(sub_node, parent=name if kind == "source.lang.swift.decl.function.method.instance" else parent)

    for root_node in ast_data.get("key.substructure", []):
        traverse(root_node)

    return dependencies

# Function to generate dependency graph
def generate_dependency_graph():
    project_dependencies = defaultdict(dict)
    dot = graphviz.Digraph("SwiftUI_Dependencies", format="png")

    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".swift"):
                file_path = os.path.join(root, file)
                file_dependencies = analyze_swift_file(file_path)
                project_dependencies[file] = file_dependencies

                dot.node(file, file.replace(".swift", ""))

                for dep_type, dep_list in file_dependencies.items():
                    if isinstance(dep_list, list):
                        for dep in dep_list:
                            dot.edge(file, dep, label=dep_type)

    with open("dependencies.json", "w") as f:
        json.dump(project_dependencies, f, indent=4)

    dot.render("dependencies")  # Generates dependencies.png
    print("✅ AI Context Dependency Graph Updated (dependencies.png)")

# Function to simulate AI context loading & log it
def simulate_ai_context_loading():
    if not os.path.exists("dependencies.json"):
        print("❌ dependencies.json not found. Running dependency update now...")
        generate_dependency_graph()

    with open("dependencies.json", "r") as f:
        dependencies = json.load(f)

    loaded_files = []
    max_files = 5  # Match `cursor-rules.json` settings

    for file, data in dependencies.items():
        if len(loaded_files) >= max_files:
            break
        loaded_files.append(file)

    log_context_updates(loaded_files)

# Run everything automatically
if __name__ == "__main__":
    generate_dependency_graph()  # Update dependency graph on every run
    simulate_ai_context_loading()  # Log AI-loaded files
