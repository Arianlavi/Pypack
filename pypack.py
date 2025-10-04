import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import shutil
from pathlib import Path
import modulefinder
import importlib.util
import webbrowser
import os
from PIL import Image


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

DATA_SEP = ";" if sys.platform.startswith("win") else ":"
GITHUB_ICON = resource_path("github.png")  

def detect_imports(folder):
    py_files = list(Path(folder).rglob("*.py"))
    imports = set()
    for file in py_files:
        try:
            finder = modulefinder.ModuleFinder()
            finder.run_script(str(file))
            imports.update(finder.modules.keys())
        except Exception:
            pass
    return list(imports)

def check_installed(mod_name):
    return importlib.util.find_spec(mod_name) is not None

class BuildGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🐍 PyPack V2")
        self.geometry("877x738")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.project_dir = ctk.StringVar()
        self.entry_file = ctk.StringVar()
        self.icon_file = ctk.StringVar()
        self.upx_path = ctk.StringVar()
        self.onefile = ctk.BooleanVar(value=True)
        self.windowed = ctk.BooleanVar(value=True)
        self.console = ctk.BooleanVar(value=False)
        self.use_upx = ctk.BooleanVar(value=False)
        self.use_pyarmor = ctk.BooleanVar(value=False)
        self.data_files = []

        try:
            self.github_image = ctk.CTkImage(Image.open(GITHUB_ICON), size=(40, 40))
        except Exception:
            self.github_image = None

        self._build_ui()

    def _build_ui(self):
        top_frame = ctk.CTkFrame(self, corner_radius=15)
        top_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top_frame, text="🐍 PyPack V2 ", font=("Segoe UI", 20, "bold")).pack(side="left", padx=10)
        if self.github_image:
            github_btn = ctk.CTkButton(
                top_frame,
                text="",
                image=self.github_image,
                width=40,
                height=40,
                fg_color="transparent",
                hover_color="#2f2f2f",
                command=lambda: webbrowser.open("https://github.com/Arianlavi/Pypack")
            )
            github_btn.pack(side="right", padx=10)

        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.pack(pady=10, padx=10, fill="x")

        def add_row(row, text, var, cmd=None):
            ctk.CTkLabel(frame, text=text).grid(row=row, column=0, sticky="w", pady=5, padx=5)
            ctk.CTkEntry(frame, textvariable=var, width=600).grid(row=row, column=1, padx=5)
            if cmd:
                ctk.CTkButton(frame, text="Browse", command=cmd).grid(row=row, column=2, padx=5)

        add_row(0, "📂 Project Dir:", self.project_dir, self._browse_project)
        add_row(1, "▶ Entry Script:", self.entry_file, self._browse_entry)
        add_row(2, "🖼 Icon (.ico):", self.icon_file, self._browse_icon)
        add_row(3, "🗜 UPX Path:", self.upx_path, self._browse_upx)

        # Options
        opt_frame = ctk.CTkFrame(self, corner_radius=15)
        opt_frame.pack(fill="x", padx=10, pady=10)
        for text, var in [
            ("Onefile", self.onefile),
            ("Windowed (no console)", self.windowed),
            ("Console", self.console),
            ("Use UPX", self.use_upx),
            ("Obfuscate with PyArmor", self.use_pyarmor)
        ]:
            ctk.CTkCheckBox(opt_frame, text=text, variable=var).pack(side="left", padx=15)

        # Data Files
        data_frame = ctk.CTkFrame(self, corner_radius=15)
        data_frame.pack(fill="x", padx=10, pady=5)
        self.data_listbox = ctk.CTkTextbox(data_frame, width=730, height=100)
        self.data_listbox.pack(side="left", padx=5, pady=5)
        btn_frame = ctk.CTkFrame(data_frame, corner_radius=15)
        btn_frame.pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="➕ Add File", command=self._add_data_file).pack(pady=5)
        ctk.CTkButton(btn_frame, text="❌ Clear Files", command=self._clear_data_files).pack(pady=5)

        ctk.CTkButton(
            self,
            text="🚀 Build EXE",
            font=("Segoe UI", 16, "bold"),
            fg_color="#d83b01",
            hover_color="#a52a2a",
            command=self._start_build
        ).pack(pady=15)

        self.log_box = ctk.CTkTextbox(self, width=850, height=320, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    def _browse_project(self):
        path = filedialog.askdirectory()
        if path: self.project_dir.set(path)

    def _browse_entry(self):
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path: self.entry_file.set(path)

    def _browse_icon(self):
        path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        if path: self.icon_file.set(path)

    def _browse_upx(self):
        path = filedialog.askdirectory()
        if path: self.upx_path.set(path)

    def _add_data_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.data_files.append(path)
            self.data_listbox.insert("end", path + "\n")

    def _clear_data_files(self):
        self.data_files.clear()
        self.data_listbox.delete("1.0", "end")

    def _log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.update_idletasks()

    def _start_build(self):
        threading.Thread(target=self._build, daemon=True).start()

    def _build(self):
        proj = Path(self.project_dir.get())
        entry = Path(self.entry_file.get())
        icon = self.icon_file.get()

        if not proj.exists() or not entry.exists():
            messagebox.showerror("Error", "Project or Entry file not found!")
            return

        self._log("🚧 Starting build...")

        upx_dir = self.upx_path.get()
        if self.use_upx.get():
            if shutil.which("upx") or (upx_dir and Path(upx_dir).exists()):
                self._log(f"🗜 Using UPX at {upx_dir if upx_dir else 'PATH'}")
            else:
                self._log("⚠ UPX not found, disabling UPX")
                self.use_upx.set(False)

        self._log("🔍 Analyzing imports with modulefinder...")
        try:
            imports = detect_imports(str(proj))
            self._log(f"Detected imports: {', '.join(imports)}")
        except Exception as e:
            self._log(f"❌ Import detection failed: {e}")
            imports = []

        for mod in imports:
            if not check_installed(mod):
                self._log(f"⚠ Missing module: {mod} (pip install {mod})")

        self._log("⚡ Running PyInstaller...")
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
        elif self.upx_path.get():
            cmd.extend(["--upx-dir", self.upx_path.get()])

        for df in self.data_files:
            src = Path(df)
            dest = src.name
            cmd.extend(["--add-data", f"{src}{DATA_SEP}{dest}"])

        for mod in imports:
            cmd.extend(["--hidden-import", mod])

        cmd.extend(["--paths", str(proj)])
        cmd.extend(["--name", "Pypack", str(entry)])

        self._run_cmd(cmd, cwd=str(proj))
        self._log("✅ Build finished! Check 'dist' folder.")

    def _run_cmd(self, cmd, cwd=None):
        try:
            self._log("RUN: " + " ".join(cmd))
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, shell=True)
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
    app = BuildGUI()
    app.mainloop()
