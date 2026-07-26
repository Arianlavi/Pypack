import os
import sys
import ast
import shutil
import string
import marshal
import secrets
import importlib.util
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

IGNORE_DIRS = {
    "__pycache__", ".git", ".hg", ".svn", ".idea", ".vscode",
    "venv", ".venv", "env", ".env", "build", "dist",
    "_ppk_stage", "node_modules", "tests", "test",
    ".pytest_cache", ".mypy_cache", ".tox", "htmlcov", ".ruff_cache",
}


KNOWN_SUBMODULES = {
    "tkinter": [
        "tkinter", "tkinter.ttk", "tkinter.filedialog", "tkinter.messagebox",
        "tkinter.simpledialog", "tkinter.colorchooser", "tkinter.font",
        "tkinter.scrolledtext", "tkinter.commondialog", "_tkinter",
    ],
    "PIL": ["PIL", "PIL.Image", "PIL.ImageTk", "PIL.ImageDraw", "PIL.ImageFont"],
    "customtkinter": ["customtkinter"],
}

# Packages that need PyInstallers --collect-all to bring along their data
# files / shared libraries once hidden-import alone would not surface them
COLLECT_ALL_PACKAGES = {"tkinter", "customtkinter"}


def _is_ignored(rel_parts):
    return any(p in IGNORE_DIRS for p in rel_parts)


def collect_imports(project_dir):
    """
    Walk every .py file in the project and collect top-level imported
    module names via the AST, ignoring relative (intra-project) imports.
    Far more reliable than modulefinder, which silently drops modules it
    fails to trace (tkinter, C-extension heavy packages, etc.).
    """
    project_dir = Path(project_dir).resolve()
    found = set()
    for py_file in project_dir.rglob("*.py"):
        rel = py_file.relative_to(project_dir)
        if _is_ignored(rel.parts):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"), filename=str(py_file))
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                if node.module:
                    found.add(node.module.split(".")[0])
    return found


def expand_known_packages(names):
    expanded = set(names)
    for name in list(names):
        if name in KNOWN_SUBMODULES:
            expanded.update(KNOWN_SUBMODULES[name])
    return expanded


def collect_all_targets(names):
    return sorted(n for n in names if n in COLLECT_ALL_PACKAGES)


def is_external_module(mod_name, project_dir: Path):
    if mod_name in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(mod_name)
    except Exception:
        return False
    if spec is None or not spec.origin:
        return mod_name in KNOWN_SUBMODULES or mod_name == "_tkinter"
    try:
        origin = Path(spec.origin).resolve()
    except Exception:
        return False
    try:
        origin.relative_to(project_dir.resolve())
        return False
    except ValueError:
        return True


QT_PRIORITY = ["PyQt6", "PySide6", "PyQt5", "PySide2"]


def resolve_qt_conflict(imports):
    present = [q for q in QT_PRIORITY if q in imports]
    if len(present) <= 1:
        return set(imports), []
    drop = present[1:]
    return set(imports) - set(drop), drop


def _rand_name(length=9):
    alphabet = string.ascii_lowercase
    return "_" + "".join(secrets.choice(alphabet) for _ in range(length))


def _rand_ext():
    return "." + "".join(secrets.choice(string.ascii_lowercase) for _ in range(3))


class ProjectEncryptor:
    """
    Compiles every .py file in a project to bytecode and seals it with
    AES-256-GCM under a key generated fresh for the current build. The
    staged output, container extension, data folder name, and the runtime
    loaders internal names are all randomized per build, so no two builds
    share a fingerprint.
    """

    def __init__(self, project_dir: Path, entry_file: Path):
        self.project_dir = Path(project_dir).resolve()
        self.entry_file = Path(entry_file).resolve()
        self.key = AESGCM.generate_key(bit_length=256)
        self._aead = AESGCM(self.key)
        self.container_ext = _rand_ext()
        self.root_name = "d" + secrets.token_hex(4)

    def stage(self, stage_root: Path) -> Path:
        stage_root = Path(stage_root)
        app_dir = stage_root / self.root_name
        if stage_root.exists():
            shutil.rmtree(stage_root)
        app_dir.mkdir(parents=True)

        for src in self.project_dir.rglob("*"):
            rel = src.relative_to(self.project_dir)
            if _is_ignored(rel.parts):
                continue
            dest = app_dir / rel
            if src.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            if src.suffix == ".py":
                self._encrypt_file(src, dest.with_suffix(self.container_ext))
            else:
                shutil.copy2(src, dest)

        entry_rel = self.entry_file.relative_to(self.project_dir).with_suffix(self.container_ext)
        self.app_dir = app_dir
        return entry_rel

    def _encrypt_file(self, src: Path, dest: Path):
        source = src.read_text(encoding="utf-8")
        code_obj = compile(source, src.name, "exec")
        payload = marshal.dumps(code_obj)
        nonce = secrets.token_bytes(12)
        aad = dest.name.encode()
        ciphertext = self._aead.encrypt(nonce, payload, aad)
        dest.write_bytes(nonce + ciphertext)

    def _scatter_key(self):
        # Split the 32-byte key into a handful of uneven chunks, mask each
        # one with its own random pad, and shuffle the storage order. The
        # bootstrap reassembles them using an embedded index map.
        boundaries = sorted(secrets.randbelow(31) + 1 for _ in range(3))
        boundaries = sorted(set(boundaries)) or [8]
        cuts = [0] + boundaries + [32]
        chunks = [self.key[cuts[i]:cuts[i + 1]] for i in range(len(cuts) - 1)]
        order = list(range(len(chunks)))
        secrets.SystemRandom().shuffle(order)

        stored = [None] * len(chunks)
        for pos, orig_idx in enumerate(order):
            chunk = chunks[orig_idx]
            mask = secrets.token_bytes(len(chunk))
            masked = bytes(a ^ b for a, b in zip(chunk, mask))
            stored[pos] = (masked, mask)

        recover_map = [0] * len(chunks)
        for pos, orig_idx in enumerate(order):
            recover_map[orig_idx] = pos

        return stored, recover_map

    def write_bootstrap(self, stage_root: Path) -> Path:
        stored, recover_map = self._scatter_key()
        names = {k: _rand_name() for k in (
            "aead_var", "parts_var", "map_var", "ext_var", "root_var",
            "entry_var", "rebuild_fn", "read_fn", "base_fn", "run_fn",
            "loader_cls", "finder_cls",
        )}

        source = _BOOTSTRAP_TEMPLATE.format(
            parts=repr(stored),
            recover_map=repr(recover_map),
            root_name=repr(self.root_name),
            container_ext=repr(self.container_ext),
            entry_rel=repr(str(self._entry_rel).replace(os.sep, "/")),
            **names,
        )

        boot_path = Path(stage_root) / "_ppk_bootstrap.py"
        boot_path.write_text(source, encoding="utf-8")
        return boot_path

    def stage_and_bootstrap(self, stage_root: Path):
        entry_rel = self.stage(stage_root)
        self._entry_rel = entry_rel
        return self.write_bootstrap(stage_root)


_BOOTSTRAP_TEMPLATE = '''import os
import sys
import marshal
import importlib.util

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

{parts_var} = {parts}
{map_var} = {recover_map}
{root_var} = {root_name}
{ext_var} = {container_ext}
{entry_var} = {entry_rel}


def {rebuild_fn}():
    chunks = []
    for orig_idx in range(len(({map_var}))):
        pos = {map_var}[orig_idx]
        masked, mask = {parts_var}[pos]
        chunks.append(bytes(a ^ b for a, b in zip(masked, mask)))
    return b"".join(chunks)


{aead_var} = AESGCM({rebuild_fn}())


def {base_fn}():
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, {root_var})
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), {root_var})


def {read_fn}(path):
    with open(path, "rb") as fh:
        blob = fh.read()
    nonce = blob[:12]
    ciphertext = blob[12:]
    aad = os.path.basename(path).encode()
    payload = {aead_var}.decrypt(nonce, ciphertext, aad)
    return marshal.loads(payload)


class {loader_cls}:
    def __init__(self, path, is_package):
        self._path = path
        self._is_package = is_package

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        code_obj = {read_fn}(self._path)
        module.__file__ = self._path
        if self._is_package:
            module.__path__ = [os.path.dirname(self._path)]
        exec(code_obj, module.__dict__)


class {finder_cls}:
    def __init__(self, root):
        self._root = root

    def find_spec(self, fullname, path=None, target=None):
        parts = fullname.split(".")
        base = os.path.join(self._root, *parts)
        pkg_init = os.path.join(base, "__init__" + {ext_var})
        mod_file = base + {ext_var}

        if os.path.isdir(base) and os.path.isfile(pkg_init):
            loader = {loader_cls}(pkg_init, True)
            spec = importlib.util.spec_from_loader(fullname, loader, is_package=True)
            spec.submodule_search_locations = [base]
            return spec

        if os.path.isfile(mod_file):
            loader = {loader_cls}(mod_file, False)
            return importlib.util.spec_from_loader(fullname, loader, is_package=False)

        return None


def {run_fn}():
    root = {base_fn}()
    sys.meta_path.insert(0, {finder_cls}(root))
    entry_path = os.path.join(root, *{entry_var}.split("/"))
    code_obj = {read_fn}(entry_path)
    main_mod = sys.modules["__main__"]
    main_mod.__file__ = entry_path
    exec(code_obj, main_mod.__dict__)


if __name__ == "__main__":
    {run_fn}()
'''
