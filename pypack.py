import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess
import threading
import sys
import shutil
from pathlib import Path
import importlib.util
import webbrowser
import os
from PIL import Image

from pypack_crypt import (
    ProjectEncryptor,
    collect_imports,
    expand_known_packages,
    collect_all_targets,
    is_external_module,
    resolve_qt_conflict,
)

APP_VERSION = "3.0"

COLORS = {
    "bg": "#0e0f13",
    "card": "#171922",
    "card_alt": "#1c2230",
    "border": "#262b3a",
    "accent": "#7c5cff",
    "accent_hover": "#6a4ce0",
    "accent_soft": "#232047",
    "cyan": "#22d3ee",
    "dim": "#8b93a7",
    "text": "#eef0f5",
    "ok": "#22c55e",
    "warn": "#f59e0b",
    "bad": "#ef4444",
}


def resource_path(rel):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, rel)
    return os.path.join(os.path.abspath("."), rel)


DATA_SEP = ";" if sys.platform.startswith("win") else ":"
GITHUB_ICON = resource_path("github.png")


def check_installed(mod_name):
    return importlib.util.find_spec(mod_name) is not None


class Section(ctk.CTkFrame):
    def __init__(self, master, title, subtitle=None, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=COLORS["card"],
                          border_width=1, border_color=COLORS["border"], **kwargs)
        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(10, 2))
        ctk.CTkLabel(head, text=title, font=("Segoe UI", 13, "bold"),
                     text_color=COLORS["text"]).pack(side="left")
        if subtitle:
            ctk.CTkLabel(head, text=subtitle, font=("Segoe UI", 10),
                         text_color=COLORS["dim"]).pack(side="left", padx=(8, 0))
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="x", padx=16, pady=(0, 12))


class BuildGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PyPack V3")
        self.geometry("920x880")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg"])

        self.app_name = ctk.StringVar()
        self.project_dir = ctk.StringVar()
        self.entry_file = ctk.StringVar()
        self.icon_file = ctk.StringVar()
        self.upx_path = ctk.StringVar()
        self.onefile = ctk.BooleanVar(value=True)
        self.windowed = ctk.BooleanVar(value=True)
        self.console = ctk.BooleanVar(value=False)
        self.use_upx = ctk.BooleanVar(value=False)
        self.use_pyarmor = ctk.BooleanVar(value=False)
        self.use_ppkcrypt = ctk.BooleanVar(value=False)
        self.data_files = []

        try:
            self.github_image = ctk.CTkImage(Image.open(GITHUB_ICON), size=(26, 26))
        except Exception:
            self.github_image = None

        self._build_ui()

    def _build_ui(self):
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=14, pady=14)

        self._build_header(root)
        self._build_project_section(root)
        self._build_options_section(root)
        self._build_data_section(root)
        self._build_action_row(root)
        self._build_log_section(root)

    def _build_header(self, parent):
        header = ctk.CTkFrame(parent, corner_radius=14, fg_color=COLORS["card_alt"],
                               border_width=1, border_color=COLORS["border"], height=64)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=18, fill="y")

        title_row = ctk.CTkFrame(left, fg_color="transparent")
        title_row.pack(anchor="w", pady=(10, 0))
        ctk.CTkLabel(title_row, text="PyPack", font=("Segoe UI", 20, "bold"),
                     text_color=COLORS["text"]).pack(side="left")
        ctk.CTkLabel(title_row, text=" V3", font=("Segoe UI", 20, "bold"),
                     text_color=COLORS["accent"]).pack(side="left")
        ctk.CTkLabel(title_row, text=f"  {APP_VERSION}", font=("Segoe UI", 10, "bold"),
                     text_color=COLORS["cyan"]).pack(side="left")

        ctk.CTkLabel(left, text="Build, protect and ship Python apps as native executables",
                     font=("Segoe UI", 11), text_color=COLORS["dim"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=18, fill="y")

        status_wrap = ctk.CTkFrame(right, fg_color="transparent")
        status_wrap.pack(side="left", pady=20)
        self.status_dot = ctk.CTkLabel(status_wrap, text="\u25cf", font=("Segoe UI", 14),
                                        text_color=COLORS["dim"])
        self.status_dot.pack(side="left", padx=(0, 6))
        self.status_label = ctk.CTkLabel(status_wrap, text="Idle", font=("Segoe UI", 12, "bold"),
                                          text_color=COLORS["dim"])
        self.status_label.pack(side="left", padx=(0, 14))

        if self.github_image:
            ctk.CTkButton(right, text="", image=self.github_image, width=32, height=32,
                          fg_color="transparent", hover_color=COLORS["card"], corner_radius=8,
                          command=lambda: webbrowser.open("https://github.com/Arianlavi/Pypack")
                          ).pack(side="left", pady=16)

    def _build_project_section(self, parent):
        sec = Section(parent, "Project", "source, entry point, icon")
        sec.pack(fill="x", pady=(0, 10))
        body = sec.body
        body.grid_columnconfigure(1, weight=1)

        def row(r, label, var, cmd=None, hint=""):
            ctk.CTkLabel(body, text=label, font=("Segoe UI", 11), text_color=COLORS["dim"],
                         anchor="w", width=120).grid(row=r, column=0, sticky="w", pady=4)
            entry = ctk.CTkEntry(body, textvariable=var, placeholder_text=hint,
                                  fg_color=COLORS["card_alt"], border_color=COLORS["border"],
                                  height=30, corner_radius=7)
            entry.grid(row=r, column=1, sticky="ew", padx=8, pady=4)
            if cmd:
                ctk.CTkButton(body, text="Browse", command=cmd, width=84, height=30,
                              fg_color=COLORS["card_alt"], hover_color=COLORS["border"],
                              corner_radius=7).grid(row=r, column=2, pady=4)

        row(0, "App Name", self.app_name, hint="defaults to project folder name")
        row(1, "Project Dir", self.project_dir, self._browse_project)
        row(2, "Entry Script", self.entry_file, self._browse_entry)
        row(3, "Icon (.ico)", self.icon_file, self._browse_icon)
        row(4, "UPX Path", self.upx_path, self._browse_upx)

    def _build_options_section(self, parent):
        sec = Section(parent, "Build Options", "packaging & protection")
        sec.pack(fill="x", pady=(0, 10))
        body = sec.body

        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x")
        opts = [
            ("One File", self.onefile),
            ("Windowed", self.windowed),
            ("Console", self.console),
            ("Use UPX", self.use_upx),
            ("PyArmor Obfuscation", self.use_pyarmor),
        ]
        for i, (text, var) in enumerate(opts):
            r, c = divmod(i, 3)
            ctk.CTkCheckBox(grid, text=text, variable=var, font=("Segoe UI", 11),
                             fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                             checkmark_color="#0e0f13", border_color=COLORS["border"]
                             ).grid(row=r, column=c, sticky="w", padx=8, pady=6)

        crypt_row = ctk.CTkFrame(body, fg_color=COLORS["accent_soft"], corner_radius=10)
        crypt_row.pack(fill="x", pady=(6, 0))
        ctk.CTkCheckBox(crypt_row, text="PyPack Crypt (AES-256, unique per build)",
                         variable=self.use_ppkcrypt, font=("Segoe UI", 12, "bold"),
                         text_color=COLORS["cyan"], fg_color=COLORS["accent"],
                         hover_color=COLORS["accent_hover"], checkmark_color="#0e0f13",
                         border_color=COLORS["border"]).pack(side="left", padx=14, pady=8)

    def _build_data_section(self, parent):
        sec = Section(parent, "Extra Data Files", "bundled assets & resources")
        sec.pack(fill="x", pady=(0, 10))

        row = ctk.CTkFrame(sec.body, fg_color="transparent")
        row.pack(fill="x")
        self.data_listbox = ctk.CTkTextbox(row, height=60, fg_color=COLORS["card_alt"],
                                            border_width=1, border_color=COLORS["border"],
                                            corner_radius=7)
        self.data_listbox.pack(side="left", fill="x", expand=True)

        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(side="left", padx=(10, 0))
        ctk.CTkButton(btns, text="Add File", command=self._add_data_file, width=100, height=28,
                      fg_color=COLORS["card_alt"], hover_color=COLORS["border"],
                      corner_radius=7).pack(pady=(0, 6))
        ctk.CTkButton(btns, text="Clear", command=self._clear_data_files, width=100, height=28,
                      fg_color=COLORS["card_alt"], hover_color=COLORS["border"],
                      corner_radius=7).pack()

    def _build_action_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 10))

        self.build_btn = ctk.CTkButton(row, text="Build Executable", font=("Segoe UI", 14, "bold"),
                                        fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                                        height=42, corner_radius=10, command=self._start_build)
        self.build_btn.pack(side="left", fill="x", expand=True)

        self.progress = ctk.CTkProgressBar(row, mode="indeterminate", height=6,
                                            progress_color=COLORS["cyan"], fg_color=COLORS["card_alt"])
        self.progress.pack(side="left", fill="x", expand=True, padx=(12, 0))
        self.progress.set(0)

    def _build_log_section(self, parent):
        sec = Section(parent, "Build Log", "live PyInstaller output")
        sec.pack(fill="both", expand=True)
        self.log_box = ctk.CTkTextbox(sec.body, font=("Consolas", 11), fg_color="#0a0b0f",
                                       border_width=1, border_color=COLORS["border"], corner_radius=7)
        self.log_box.pack(fill="both", expand=True)

    def _browse_project(self):
        path = filedialog.askdirectory()
        if path:
            self.project_dir.set(path)
            if not self.app_name.get():
                self.app_name.set(Path(path).name)

    def _browse_entry(self):
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            self.entry_file.set(path)

    def _browse_icon(self):
        path = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        if path:
            self.icon_file.set(path)

    def _browse_upx(self):
        path = filedialog.askdirectory()
        if path:
            self.upx_path.set(path)

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

    def _set_status(self, text, color_key):
        self.status_label.configure(text=text, text_color=COLORS[color_key])
        self.status_dot.configure(text_color=COLORS[color_key])

    def _start_build(self):
        self.build_btn.configure(state="disabled")
        self._set_status("Building", "warn")
        self.progress.start()
        threading.Thread(target=self._build_wrapper, daemon=True).start()

    def _build_wrapper(self):
        ok = False
        try:
            ok = self._build()
        finally:
            self.progress.stop()
            self.progress.set(0)
            self.build_btn.configure(state="normal")
            self._set_status("Success" if ok else "Failed", "ok" if ok else "bad")

    def _build(self):
        proj = Path(self.project_dir.get())
        entry = Path(self.entry_file.get())
        icon = self.icon_file.get()
        exe_name = self.app_name.get().strip() or (proj.name if proj.exists() else "PyPackBuild")

        if not proj.exists() or not entry.exists():
            messagebox.showerror("Error", "Project or Entry file not found!")
            return False

        self._log("Starting build...")

        upx_dir = self.upx_path.get()
        if self.use_upx.get():
            if shutil.which("upx") or (upx_dir and Path(upx_dir).exists()):
                self._log(f"Using UPX at {upx_dir if upx_dir else 'PATH'}")
            else:
                self._log("UPX not found, disabling UPX")
                self.use_upx.set(False)

        self._log("Scanning imports...")
        try:
            raw_imports = collect_imports(proj)
            imports = expand_known_packages(raw_imports)
        except Exception as e:
            self._log(f"Import scan failed: {e}")
            imports = set()

        exclude_modules = []
        imports, qt_dropped = resolve_qt_conflict(imports)
        if qt_dropped:
            self._log(f"Multiple Qt bindings found, keeping one and excluding: {', '.join(qt_dropped)}")
            exclude_modules.extend(qt_dropped)

        self._log(f"Detected imports: {', '.join(sorted(imports)) or 'none'}")

        entry_for_build = entry
        cwd_for_build = str(proj)
        extra_add_data = []
        collect_all = []

        if self.use_ppkcrypt.get():
            if importlib.util.find_spec("cryptography") is None:
                self._log("The 'cryptography' package is missing. Run: pip install cryptography")
                return False
            self._log("Sealing project with PyPack Crypt...")
            try:
                stage_root = proj / "_ppk_stage"
                encryptor = ProjectEncryptor(proj, entry)
                boot_path = encryptor.stage_and_bootstrap(stage_root)
                sealed_count = sum(1 for _ in encryptor.app_dir.rglob(f"*{encryptor.container_ext}"))
                self._log(f"Key generated ({len(encryptor.key) * 8}-bit), {sealed_count} module(s) sealed")
                entry_for_build = boot_path
                cwd_for_build = str(stage_root)
                extra_add_data.append((str(encryptor.app_dir), encryptor.root_name))
                imports = {m for m in imports if is_external_module(m, proj)}
                collect_all = collect_all_targets(imports)
            except Exception as e:
                self._log(f"Encryption failed: {e}")
                return False

        for mod in sorted(imports):
            if mod == "__main__":
                continue
            if not check_installed(mod):
                self._log(f"Missing module: {mod} (pip install {mod})")

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
        elif self.upx_path.get():
            cmd.extend(["--upx-dir", self.upx_path.get()])

        for src_dir, dest_dir in extra_add_data:
            cmd.extend(["--add-data", f"{src_dir}{DATA_SEP}{dest_dir}"])

        for df in self.data_files:
            src = Path(df)
            cmd.extend(["--add-data", f"{src}{DATA_SEP}{src.name}"])

        for mod in sorted(imports):
            cmd.extend(["--hidden-import", mod])

        for pkg in collect_all:
            cmd.extend(["--collect-all", pkg])

        for mod in exclude_modules:
            cmd.extend(["--exclude-module", mod])

        cmd.extend(["--distpath", str(proj / "dist")])
        cmd.extend(["--workpath", str(proj / "build")])
        cmd.extend(["--specpath", str(proj)])
        cmd.extend(["--paths", str(proj)])
        cmd.extend(["--name", exe_name, str(entry_for_build)])

        success = self._run_cmd(cmd, cwd=cwd_for_build)
        if success:
            self._log(f"Build finished. Executable in: {proj / 'dist'}")
        else:
            self._log("Build did not complete successfully, see log above.")
        return success

    def _run_cmd(self, cmd, cwd=None):
        try:
            self._log("RUN: " + " ".join(cmd))
            proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self._log(line.strip())
            proc.wait()
            if proc.returncode != 0:
                self._log(f"Command failed with exit code {proc.returncode}")
            return proc.returncode == 0
        except Exception as e:
            self._log(f"ERROR: {e}")
            return False


if __name__ == "__main__":
    app = BuildGUI()
    app.mainloop()
