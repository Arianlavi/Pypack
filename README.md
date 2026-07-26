# PyPack V3

A desktop GUI for turning Python projects into standalone executables. It wraps PyInstaller, fixes a bunch of its rough edges around import detection and Qt conflicts, and adds an optional encryption layer for people who want to ship closed-source builds without dragging in a third-party obfuscator.

Built with CustomTkinter, so it looks like an actual app instead of a Tk dialog from 2004.

## Why this exists

PyInstaller is solid but the CLI workflow gets old fast, especially once a project has icons, extra data files, hidden imports, and UPX in the mix. PyPack wraps all of that into one window: pick your project, hit build, watch the log. Under the hood it also does a few things the plain CLI doesn't:

- Scans your entire project with the `ast` module instead of `modulefinder`, which in practice misses things like `tkinter` submodules and silently produces broken builds.
- Detects when a project accidentally pulls in more than one Qt binding (PyQt5 + PyQt6 is a common one if you've got leftover code from a migration) and excludes the extra one automatically instead of letting PyInstaller crash mid-build.
- Always writes `dist` and `build` next to your project folder, even when the encryption step stages files somewhere else first.

## Features

- One-file or one-folder builds, windowed or console
- Custom `.ico` icon and app name
- UPX compression, with an optional custom path
- Arbitrary extra data files bundled alongside the executable
- PyArmor support if you'd rather use that
- PyPack Crypt — a built-in AES-256 source protection layer (details below)
- Live build log with a real success/failure status, not just a spinner that lies to you

## PyPack Crypt

This is the part I'm actually proud of. Instead of shipping your `.py` files as-is or bolting on PyArmor, PyPack can compile every module in your project to bytecode and encrypt it with AES-256-GCM before handing anything to PyInstaller.

A few things that make it different from a typical "obfuscator":

- The encryption key is generated fresh for every single build. There's no shared runtime key sitting in a DLL somewhere.
- The container file extension, the staging folder name, and every internal variable/class name in the generated loader are randomized per build. Two builds of the same project won't look alike on disk or in a decompiler.
- Decrypted code is never written to disk. Modules are decrypted straight into memory through a custom import hook as they're imported, then discarded.
- Every container is authenticated (GCM), so a corrupted or tampered file fails to decrypt instead of silently loading garbage.

I'll be upfront about what this isn't: it's not unbreakable. Nothing that runs Python bytecode on someone else's machine can be. What it actually buys you is the absence of a fixed signature — there's no shared "PyPack runtime" for a reverse engineer to fingerprint once and reuse against every app built with this tool.

## Getting started

```bash
git clone https://github.com/Arianlavi/PyPack.git
cd PyPack
pip install -r requirements.txt
python pypack.py
```

Requires Python 3.10+. If you're using PyPack Crypt you'll also need the `cryptography` package (it's in requirements.txt already).

## Using it

Point it at your project folder and entry script, set an icon if you have one, pick your build options, and hit Build. If you want source protection, flip on PyPack Crypt before building — everything else stays the same. The finished executable lands in `<your project>/dist`.

If your project needs data files that aren't already inside the project folder, add them under Extra Data Files. If you're using UPX, either have it on your PATH or point PyPack at the folder.

## A note on Qt projects

If you've got both PyQt5 and PyQt6 imported anywhere in your codebase (even in a `try/except` fallback), PyInstaller will refuse to build — it doesn't support bundling two Qt bindings at once. PyPack detects this automatically now and keeps only one, but the cleaner fix long-term is just uninstalling whichever binding you're not using.

## Requirements

```
pyinstaller
customtkinter
Pillow
cryptography
pyarmor        # optional
```

## Support

If this saved you some time and you feel like throwing a few dollars at it:

| Currency | Address |
|---|---|
| BTC | `bc1q3r79a2t3tuada56zv722ykrwjadgsh79m5pthz` |
| ETH / USDT (ERC-20) | `0x66D74F4b7527ea9eD5BA5e2E02fa93fB7a90325d` |
| SOL | `9irdHFdeWVb6cnu8HTdKAs3Lg1PD8HiQQLhVHLSAQq6X` |

Double-check addresses before sending anything — donations aren't refundable.

Otherwise, a star on the repo or a bug report is just as appreciated.

## License

MIT. See [LICENSE](LICENSE).

## Author

Arian Lavi — [github.com/arianlavi](https://github.com/arianlavi)
