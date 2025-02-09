# SwiftUI AI Context Generator

This repository provides a **fully automated AI context generator for SwiftUI projects**, enabling **Cursor AI** to have **full project awareness** dynamically.

## 🚀 Features

✅ **Automatically generates `dependencies.json` for AI context tracking.**  
✅ **Detects function calls, state management, API calls, navigation, and CoreData usage.**  
✅ **Supports `Info.plist`, `StoreKitConfig.storekit`, `.xcconfig`, `.pbxproj`.**  
✅ **Auto-updates Cursor AI context dynamically.**  
✅ **Works seamlessly with `.cursorrules` for integration.**  
✅ **Waits for Cursor AI to finish editing before regenerating `dependencies.json`.**

---

## 📌 How It Works

This script scans all SwiftUI files in a project, maps dependencies, and updates `dependencies.json`. Cursor AI uses this file to dynamically load relevant files when needed.

### **1️⃣ Abstract Syntax Tree (AST) Parsing**

The script uses `sourcekitten` to analyze Swift files and extract information about:

- **Imports**: Detects all imported modules.
- **Functions & Calls**: Tracks which functions call each other.
- **State Management**: Identifies `@State`, `@EnvironmentObject`, `@ObservedObject`, and `@AppStorage`.
- **CoreData Models**: Detects all `NSManagedObject` subclasses.
- **Navigation Links**: Finds `NavigationLink`, `.sheet()`, and `pushViewController` calls.
- **API Calls**: Extracts `URLSession` requests and detects backend interactions.

By traversing the AST, the script builds a **map of the project structure**, showing how files interact.

### **2️⃣ User Flow: How the Script Works**

1. **Scans all Swift files in the project root directory (auto-detected or manually specified).**
2. **Parses each file's structure using AST analysis.**
3. **Extracts dependencies, function calls, navigation links, and state management.**
4. **Generates `dependencies.json`, which stores this structured project data.**
5. **If enabled, the script updates Cursor AI in real time, ensuring AI always has full context.**
6. **Waits for Cursor AI to finish modifying files before regenerating `dependencies.json`.**
7. **Logs AI-loaded files directly in the terminal.**

### **3️⃣ How Cursor Interacts with the Script**

When a user types a prompt in Cursor, the following steps occur:

#### **Flow of AI Context Handling:**

1️⃣ **User enters a prompt in Cursor.**  
2️⃣ **Cursor AI modifies one or more Swift files.**  
3️⃣ **Script detects file modifications but waits until AI finishes editing.**  
4️⃣ **After AI finishes editing, `dependencies.json` is updated.**  
5️⃣ **Cursor AI reads `dependencies.json` and `.cursorrules`.**  
6️⃣ **AI processes the context, identifying dependencies and file relationships.**  
7️⃣ **Cursor generates a response based on the structured context.**  
8️⃣ **Cursor displays the AI-generated solution, referencing the correct files.**

---

## 📌 Installation Guide

### **1️⃣ Install Dependencies**

Before using the script, install the necessary tools:

```sh
brew install sourcekitten
pip install watchdog
```

### **2️⃣ Clone the Repository**

Clone the repository into your local machine:

```sh
git clone https://github.com/uziwuzzy/konteks.git
cd konteks
```

### **3️⃣ Run the Script to Generate AI Context**

Navigate to your SwiftUI project and run the script:

```sh
python3 /path/to/konteks/context-cli.py
```

✅ This scans all Swift files and generates `dependencies.json`. AI will now have a **full map** of your SwiftUI project.

### **4️⃣ Automate AI Context Loading in Cursor**

Create or modify `.cursorrules` in your project:

```json
{
  "name": "SwiftUI AI Context",
  "rules": [
    {
      "trigger": "edit",
      "filePattern": "**/*.swift",
      "action": "executeCommand",
      "command": "python3 /path/to/konteks/context-cli.py"
    }
  ]
}
```

✅ **Now, every time Cursor AI edits a file, the script will wait for it to finish before regenerating AI context.**  
✅ **Loaded files will be displayed in the terminal in real time.**

---

## 📌 Available Commands

### **1️⃣ Auto-Detect Project Root and Run the Script**

```sh
python3 context-cli.py
```

🚀 **Automatically detects the project root and updates AI context dynamically.**

### **2️⃣ Manually Specify a Project Root**

```sh
python3 context-cli.py --root /path/to/custom/project
```

✅ **Forces the script to scan a custom directory instead of auto-detecting.**

### **3️⃣ View AI Context Log in Real Time**

```sh
tail -f cursor_ai_log.txt
```

✅ **Shows the list of files loaded into Cursor AI dynamically.**

---

## 📌 Why Use This?

✅ **Ensures AI context updates only after Cursor AI finishes modifying files.**  
✅ **Prevents unnecessary regenerations and improves performance.**  
✅ **Cursor AI will always have the latest project structure dynamically.**  
✅ **No need to manually reference files—AI loads them automatically.**  
✅ **AI debugging is more accurate, reducing missing context issues.**  
✅ **Fully automated, no manual updates required.**

---

## 📌 FAQ

### **Q: Do I need to manually update `dependencies.json`?**

**A:** No! The script **automatically updates it every time Cursor AI finishes modifying files.**

### **Q: Can I use this for multiple projects?**

**A:** Yes! Just **clone the script into any SwiftUI project** and run it.

### **Q: Does this work with UIKit projects?**

**A:** Yes, but it is optimized for **SwiftUI projects**.

### **Q: How does this save tokens in Cursor AI?**

**A:** The script ensures **Cursor loads only relevant files**, reducing unnecessary token usage.

---

## 📌 Contributing

Pull requests are welcome! If you have suggestions, feel free to contribute.

---

## 📌 License

This project is open-source under the **MIT License**.

---

🚀 **Now Cursor AI will always have full project knowledge automatically!** 🎯

