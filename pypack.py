import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
from pathlib import Path
import re
import pkgutil

DATA_SEP = ";" if sys.platform.startswith("win") else ":"


class BuildGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PyPack V1")
        self.root.geometry("950x700")
        self.root.configure(bg="#2b2b2b")

        # Vars
        self.project_dir = tk.StringVar()
        self.entry_file = tk.StringVar()
        self.icon_file = tk.StringVar()
        self.onefile = tk.BooleanVar(value=True)
        self.windowed = tk.BooleanVar(value=True)
        self.console = tk.BooleanVar(value=False)
        self.use_upx = tk.BooleanVar(value=False)
        self.use_pyarmor = tk.BooleanVar(value=False)
        self.data_files = []

        # UI
        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root, bg="#2b2b2b")
        frame.pack(pady=10, fill="x")

        # Project Dir
        tk.Label(frame, text="Project Dir:", bg="#2b2b2b", fg="white").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.project_dir, width=65, bg="#3c3f41", fg="white", insertbackground="white").grid(row=0, column=1)
        tk.Button(frame, text="Browse", command=self._browse_project, bg="#555555", fg="white").grid(row=0, column=2, padx=5)

        # Entry Script
        tk.Label(frame, text="Entry Script:", bg="#2b2b2b", fg="white").grid(row=1, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.entry_file, width=65, bg="#3c3f41", fg="white", insertbackground="white").grid(row=1, column=1)
        tk.Button(frame, text="Browse", command=self._browse_entry, bg="#555555", fg="white").grid(row=1, column=2, padx=5)

        # Icon
        tk.Label(frame, text="Icon (.ico):", bg="#2b2b2b", fg="white").grid(row=2, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.icon_file, width=65, bg="#3c3f41", fg="white", insertbackground="white").grid(row=2, column=1)
        tk.Button(frame, text="Browse", command=self._browse_icon, bg="#555555", fg="white").grid(row=2, column=2, padx=5)

        # Options
        opt_frame = tk.LabelFrame(self.root, text="Options", bg="#2b2b2b", fg="white")
        opt_frame.pack(fill="x", padx=10, pady=5)
        tk.Checkbutton(opt_frame, text="Onefile", variable=self.onefile, bg="#2b2b2b", fg="white", selectcolor="#2b2b2b").pack(side="left", padx=5)
        tk.Checkbutton(opt_frame, text="Windowed (no console)", variable=self.windowed, bg="#2b2b2b", fg="white", selectcolor="#2b2b2b").pack(side="left", padx=5)
        tk.Checkbutton(opt_frame, text="Console", variable=self.console, bg="#2b2b2b", fg="white", selectcolor="#2b2b2b").pack(side="left", padx=5)
        tk.Checkbutton(opt_frame, text="Use UPX", variable=self.use_upx, bg="#2b2b2b", fg="white", selectcolor="#2b2b2b").pack(side="left", padx=5)
        tk.Checkbutton(opt_frame, text="Obfuscate with PyArmor", variable=self.use_pyarmor, bg="#2b2b2b", fg="white", selectcolor="#2b2b2b").pack(side="left", padx=5)

        # Data files
        data_frame = tk.LabelFrame(self.root, text="Data Files (--add-data)", bg="#2b2b2b", fg="white")
        data_frame.pack(fill="x", padx=10, pady=5)
        self.data_listbox = tk.Listbox(data_frame, height=5, bg="#3c3f41", fg="white")
        self.data_listbox.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(data_frame, text="Add Data File", command=self._add_data_file, bg="#555555", fg="white").pack(side="left", padx=5)
        tk.Button(data_frame, text="Clear", command=self._clear_data_files, bg="#555555", fg="white").pack(side="left", padx=5)
        tk.Button(self.root, text="🚀 Build EXE", font=("Arial", 14, "bold"), bg="#DE3424", fg="white", command=self._start_build).pack(pady=10)

        # Log 
        self.log_box = tk.Text(self.root, wrap="word", bg="black", fg="lime", height=20)
        self.log_box.pack(fill="both", expand=True, padx=10, pady=5)

    #functions
    def _browse_project(self):
        path = filedialog.askdirectory()
        if path:
            self.project_dir.set(path)

    def _browse_entry(self):
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            self.entry_file.set(path)

    def _browse_icon(self):
        path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        if path:
            self.icon_file.set(path)

    # Data files
    def _add_data_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.data_files.append(path)
            self.data_listbox.insert("end", path)

    def _clear_data_files(self):
        self.data_files.clear()
        self.data_listbox.delete(0, "end")

    # Logging
    def _log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.root.update_idletasks()

    # Build process
    def _start_build(self):
        threading.Thread(target=self._build, daemon=True).start()

    # Scan all .py files
    def _scan_python_files(self, folder):
        py_files = []
        for path in Path(folder).rglob("*.py"):
            py_files.append(path)
        return py_files

    # Extract imports from file
    def _extract_imports(self, file_path):
        imports = set()
        pattern = re.compile(r'^\s*(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)')
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = pattern.findall(content)
                for mod in matches:
                    imports.add(mod)
        except Exception as e:
            self._log(f"Error reading {file_path}: {e}")
        return imports

    # Build function
    def _build(self):
        proj = Path(self.project_dir.get())
        entry = Path(self.entry_file.get())
        icon = self.icon_file.get()

        if not proj.exists() or not entry.exists():
            messagebox.showerror("Error", "Project or entry file not found!")
            return

        self._log("Starting build process...")
        workdir = proj

        # PyArmor obfuscate
        if self.use_pyarmor.get():
            self._log("Running PyArmor obfuscation...")
            obf_dir = proj / "obf_src"
            obf_dir.mkdir(exist_ok=True)
            cmd = ["pyarmor", "gen", str(entry), "--output", str(obf_dir)]
            ok = self._run_cmd(cmd, cwd=str(proj))
            if not ok:
                self._log("❌ PyArmor failed. Aborting build.")
                return
            workdir = obf_dir
            entry = workdir / entry.name

        # Scan project for imports
        self._log("Scanning project for local Python files...")
        py_files = self._scan_python_files(proj)
        hidden_imports = set()
        for py_file in py_files:
            hidden_imports.update(self._extract_imports(py_file))
        self._log(f"Detected imports: {', '.join(hidden_imports)}")

        # PyInstaller command
        self._log("Running PyInstaller...")
        cmd = ["pyinstaller"]
        cmd.append("--onefile" if self.onefile.get() else "--onedir")
        if self.windowed.get() and not self.console.get():
            cmd.append("--windowed")
        if self.console.get():
            cmd.append("--console")
        if icon:
            cmd.extend(["--icon", str(icon)])
        if not self.use_upx.get():
            cmd.append("--noupx")

        # Add-data for resources (json, ico, etc)
        for df in self.data_files:
            src = Path(df)
            dest = src.name
            cmd.extend(["--add-data", f"{src}{DATA_SEP}{dest}"])

        # Add hidden imports for all local .py files
        local_modules = [f.stem for f in py_files if f != entry]
        for mod in local_modules:
            cmd.extend(["--hidden-import", mod])

        # Add project path to PyInstaller
        cmd.extend(["--paths", str(proj)])
        cmd.extend(["--name", "Pypack", str(entry)])
        self._run_cmd(cmd, cwd=str(workdir))
        self._log("✅ Build finished! Check the 'dist' folder.")

    # Run command
    def _run_cmd(self, cmd, cwd=None):
        try:
            self._log("RUN: " + " ".join(cmd))
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
            for line in proc.stdout:
                self._log(line.strip())
            proc.wait()
            if proc.returncode != 0:
                self._log(f"❌ Command failed with exit code {proc.returncode}")
            return proc.returncode == 0
        except Exception as e:
            self._log(f"ERROR: {e}")
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = BuildGUI(root)
    root.mainloop()
