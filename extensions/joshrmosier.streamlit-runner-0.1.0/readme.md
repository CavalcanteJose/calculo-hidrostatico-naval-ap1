# Streamlit Runner for VS Code

A Visual Studio Code extension that allows you to run Streamlit apps directly from the context menu. Perfect for data scientists and developers who work with Streamlit frequently.

<p align="center">
  <img src="https://github.com/JoshuaMosier/vscode-streamlit-runner/raw/HEAD/example-window.png" alt="Context menu showing Run with Streamlit option"/>
</p>

<p align="center">
  <img src="https://github.com/JoshuaMosier/vscode-streamlit-runner/raw/HEAD/example-terminal2.png" alt="Streamlit running in terminal with venv info"/>
</p>

## Features

- Right-click any Python file and run it with Streamlit
- Automatically detects and uses the active Python environment (venv, conda, uv, pyenv, pipenv, etc.)
- Displays environment info in the terminal so you can verify the correct interpreter is in use
- Each app runs in its own terminal, allowing multiple Streamlit apps to run simultaneously
- Clean terminal output with Ctrl+C support to stop the server

## Requirements

- Visual Studio Code v1.93.0 or higher
- Python
- Streamlit (`pip install streamlit`)
- [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (recommended, for automatic environment detection)

## Usage

1. Right-click on any Python file in the VS Code explorer
2. Select "Run with Streamlit" from the context menu
3. The app will start in a new terminal window

The extension automatically uses whichever Python interpreter is selected in VS Code's status bar. If you're using a virtual environment, just make sure it's selected as the active interpreter.

## Extension Settings

This extension does not add any VS Code settings.

## Known Issues

None reported yet.

## Release Notes

### 0.1.0

- Added Python environment detection (venv, conda, uv, pyenv, pipenv, etc.)
- Environment info banner displayed in terminal
- Fixed race condition with VS Code Python extension auto-activation

### 0.0.1

Initial release of Streamlit Runner

## License

MIT
