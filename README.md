# PyPack

PyPack is a graphical user interface (GUI) tool designed to simplify the process of building Python executables using PyInstaller and PyArmor. It allows users to select project directories, entry scripts, icons, and additional data files, and supports options like creating a single executable file, enabling/disabling console, and obfuscating code with PyArmor.

## Features
- Select project directory, entry script, and icon file (.ico) for the executable.
- Support for PyInstaller options: onefile, windowed (no console), console, and UPX compression.
- Optional code obfuscation with PyArmor.
- Add additional data files to the executable (e.g., JSON, images).
- Log window to monitor the build process in real-time.

## Prerequisites
- Python 3.7 or higher
- Required Python packages (see `requirements.txt`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Arianlavi/PyPack.git
   cd PyPack
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python pypack.py
   ```

## Usage
1. Launch the application by running `python pypack.py`.
2. Select the **Project Directory** containing your Python project.
3. Choose the **Entry Script** (the main `.py` file to build).
4. Optionally select an **Icon File** (.ico) for the executable.
5. Check desired options:
   - **Onefile**: Create a single executable file.
   - **Windowed**: Build without a console window (GUI mode).
   - **Console**: Include a console window.
   - **Use UPX**: Enable UPX compression to reduce executable size.
   - **Obfuscate with PyArmor**: Obfuscate the code before building.
6. Add any additional data files (e.g., JSON, images) using the **Add Data File** button.
7. Click **Build EXE** to start the build process.
8. Monitor the build progress in the log window. The output executable will be in the `dist` folder.

## Requirements
See `requirements.txt` for a complete list of dependencies. Key packages include:
- `tkinter` (included with Python for GUI)
- `pyinstaller` (for building executables)
- `pyarmor` (optional, for code obfuscation)

## Notes
- Ensure the project directory contains all necessary Python files and resources.
- PyArmor requires a separate installation and configuration if obfuscation is enabled.
- The `--add-data` option uses a platform-specific separator (`;` for Windows, `:` for Linux/macOS).
- The output executable is placed in the `dist` folder within the project or obfuscated directory.

## Support & Donations
If you find PyPack helpful, please consider supporting the project with a donation! Your contributions help keep the project alive and improve its features.
You can send donations to the following wallet addresses. **Always verify the address before sending!**

| Cryptocurrency | Address | Network |
|---------------|---------|---------|
| **Bitcoin (BTC)** | `bc1q3r79a2t3tuada56zv722ykrwjadgsh79m5pthz` | Bitcoin |
| **Ethereum (ETH) / USDT** | `0x66D74F4b7527ea9eD5BA5e2E02fa93fB7a90325d` | ERC-20 |
| **Solana (SOL)** | `9irdHFdeWVb6cnu8HTdKAs3Lg1PD8HiQQLhVHLSAQq6X` | Solana |

**Important**:
- **Replace the above addresses with your own wallet addresses.**
- Copy-paste addresses exactly to avoid errors.
- Donations are non-refundable, so double-check before sending.
- For security, use a trusted wallet like [Exodus](https://exodus.com) or [Trust Wallet](https://trustwallet.com).

### Other Ways to Support
- Give the project a ⭐ on GitHub.
- Share PyPack with your friends or on social media.
- Contribute by submitting pull requests or reporting issues.

## Contributing
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.
