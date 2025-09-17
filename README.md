PyPack
PyPack is a graphical user interface (GUI) tool designed to simplify the process of building Python executables using PyInstaller and PyArmor. It allows users to select project directories, entry scripts, icons, and additional data files, and supports options like creating a single executable file, enabling/disabling console, and obfuscating code with PyArmor.
Features

Select project directory, entry script, and icon file (.ico) for the executable.
Support for PyInstaller options: onefile, windowed (no console), console, and UPX compression.
Optional code obfuscation with PyArmor.
Add additional data files to the executable (e.g., JSON, images).
Log window to monitor the build process in real-time.

Prerequisites

Python 3.7 or higher
Required Python packages (see requirements.txt)

Installation

Clone the repository:git clone https://github.com/your-username/PyPack.git
cd PyPack


Install dependencies:pip install -r requirements.txt


Run the application:python pypack.py



Usage

Launch the application by running python pypack.py.
Select the Project Directory containing your Python project.
Choose the Entry Script (the main .py file to build).
Optionally select an Icon File (.ico) for the executable.
Check desired options:
Onefile: Create a single executable file.
Windowed: Build without a console window (GUI mode).
Console: Include a console window.
Use UPX: Enable UPX compression to reduce executable size.
Obfuscate with PyArmor: Obfuscate the code before building.


Add any additional data files (e.g., JSON, images) using the Add Data File button.
Click Build EXE to start the build process.
Monitor the build progress in the log window. The output executable will be in the dist folder.

Requirements
See requirements.txt for a complete list of dependencies. Key packages include:

tkinter (included with Python for GUI)
pyinstaller (for building executables)
pyarmor (optional, for code obfuscation)

Notes

Ensure the project directory contains all necessary Python files and resources.
PyArmor requires a separate installation and configuration if obfuscation is enabled.
The --add-data option uses a platform-specific separator (; for Windows, : for Linux/macOS).
The output executable is placed in the dist folder within the project or obfuscated directory.

Contributing
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.
License
This project is licensed under the MIT License.
