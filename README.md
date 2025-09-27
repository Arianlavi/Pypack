
# 🐍 PyPack
![PyPack](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-lightgrey)

**PyPack** is a powerful GUI tool for building Python executables using **PyInstaller**, with optional **PyArmor** integration for code obfuscation. It simplifies the process by providing an intuitive interface to select project directories, entry scripts, icons, and additional data files, with support for single-file builds, console/windowed modes, and more.

---

## 🚀 Features

- **Project Configuration**:
  - Select project directory, main Python script, and icon (.ico) file.
  - Add additional data files (e.g., JSON, images).
- **PyInstaller Options**:
  - **Onefile**: Create a single executable file.
  - **Windowed**: Build a GUI application without a console.
  - **Console**: Include a console for debugging output.
  - **UPX Compression**: Reduce executable size using UPX.
- **PyArmor Obfuscation**: Optional code protection with PyArmor.
- **Live Log Window**: Real-time build process monitoring.
- **Intuitive GUI**: User-friendly interface built with Tkinter.

---
## 🖥️ Screenshots

![App Screenshot](screenshot.png)

---
## 🛠 Prerequisites

- **Python**: Version 3.7 or higher.
- **Required Packages**: Listed in `requirements.txt`.
- **Optional**: PyArmor (for obfuscation).
- **Optional**: UPX (for compression).

---

## 📥 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Arianlavi/PyPack.git
   cd PyPack

2. Install dependencies:
	```bash
	pip install -r requirements.txt
	```
3. Run the application:
	```bash
	python pypack.py
	```



## 🖥 Usage

1. Run the application:
   ```bash
   python pypack.py
   ```

2. Configure your project:
   - **Project Directory**: Select the folder containing your Python project.
   - **Entry Script**: Choose the main `.py` file.
   - **Icon File**: Optionally select an `.ico` file.
   - **Build Options**:
     - [x] Onefile
     - [x] Windowed (GUI only)
     - [x] Console
     - [x] Use UPX
     - [x] Obfuscate with PyArmor
   - **Additional Data Files**: Add files like JSON or images.

3. Click **Build EXE** to start the build.

4. Monitor progress in the log window.

5. Find the executable in the `dist/` folder.

---

## 📦 Requirements

Key packages:
- `pyinstaller`: For building executables.
- `pyarmor` (optional): For code obfuscation.
- `tkinter`: For the GUI (included with Python).

Full list in `requirements.txt`.




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

---

## ⚠️ Disclaimer

* Use responsibly. Only for your own Telegram accounts.
* Do not use for spam, phishing, or any illegal activity.
* Telegram may restrict accounts if abused.

---

## 💡 Contributing

Contributions are welcome!

* Fork the repository
* Create a new branch
* Submit a pull request

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

Created by **Arian Lavi**

* GitHub: [ArianLavi](https://github.com/arianlavi)
* Telegram: [@Arianlavi](https://t.me/Arianlvi)
