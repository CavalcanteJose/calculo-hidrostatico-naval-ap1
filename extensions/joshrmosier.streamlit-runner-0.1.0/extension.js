// extension.js
const vscode = require('vscode');
const path = require('path');
const { spawn } = require('child_process');

async function getPythonEnvironment() {
    // Strategy 1: Use the Python extension API for the actively selected interpreter
    try {
        const pythonExtension = vscode.extensions.getExtension('ms-python.python');
        if (pythonExtension) {
            if (!pythonExtension.isActive) {
                await pythonExtension.activate();
            }
            const pythonApi = pythonExtension.exports;
            const envPath = pythonApi.environments.getActiveEnvironmentPath();
            const resolvedEnv = await pythonApi.environments.resolveEnvironment(envPath);
            if (resolvedEnv) {
                const pythonPath = resolvedEnv.executable?.uri?.fsPath ?? envPath?.path;
                if (pythonPath) {
                    const version = resolvedEnv.version
                        ? `${resolvedEnv.version.major}.${resolvedEnv.version.minor}.${resolvedEnv.version.micro}`
                        : null;
                    const envName = resolvedEnv.environment?.name || null;
                    const envType = resolvedEnv.environment?.type || null;
                    const envFolder = resolvedEnv.environment?.folderUri?.fsPath || null;
                    return { pythonPath, version, envName, envType, envFolder };
                }
            }
        }
    } catch (err) {
        console.warn('Streamlit Runner: Failed to get Python path from Python extension:', err.message);
    }

    // Strategy 2: Read the defaultInterpreterPath setting
    const config = vscode.workspace.getConfiguration('python');
    const defaultPath = config.get('defaultInterpreterPath');
    if (defaultPath && defaultPath !== 'python') {
        return { pythonPath: defaultPath, version: null, envName: null, envType: null, envFolder: null };
    }

    // Strategy 3: Fall back to bare "python"
    return { pythonPath: 'python', version: null, envName: null, envType: null, envFolder: null };
}

function activate(context) {
    // Register the command that will be called from the context menu
    let disposable = vscode.commands.registerCommand('streamlit-runner.runFile', async (uri) => {
        // Get the file path from the URI
        const filePath = uri.fsPath;

        // Only proceed if it's a Python file
        if (!filePath.endsWith('.py')) {
            vscode.window.showErrorMessage('This command only works with Python files.');
            return;
        }

        const env = await getPythonEnvironment();
        const fileName = path.basename(filePath);
        const fileDir = path.dirname(filePath);

        // Use a pseudoterminal to spawn Streamlit ourselves. This completely
        // bypasses VS Code's Python extension auto-activation, which otherwise
        // sends shell activation commands that race with and kill the process.
        const writeEmitter = new vscode.EventEmitter();
        const closeEmitter = new vscode.EventEmitter();
        let childProcess;

        const pty = {
            onDidWrite: writeEmitter.event,
            onDidClose: closeEmitter.event,
            open() {
                // Show environment info so users can verify the right venv is in use
                const envLabel = env.envName || env.envFolder || null;
                const parts = [`Python: ${env.pythonPath}`];
                if (env.version) parts.push(`Version: ${env.version}`);
                if (envLabel) parts.push(`Environment: ${envLabel}`);
                if (env.envType) parts.push(`Type: ${env.envType}`);
                writeEmitter.fire(parts.join('  |  ') + '\r\n');
                writeEmitter.fire(`Running: streamlit run ${filePath}\r\n\r\n`);

                childProcess = spawn(env.pythonPath, ['-m', 'streamlit', 'run', filePath], {
                    cwd: fileDir,
                    // Prevent Streamlit from trying to open a browser since we're
                    // inside VS Code and the user can click the URL in the terminal.
                    env: { ...process.env, BROWSER: 'none' }
                });

                childProcess.stdout.on('data', (data) => {
                    // Replace \n with \r\n for proper terminal rendering
                    writeEmitter.fire(data.toString().replace(/\n/g, '\r\n'));
                });

                childProcess.stderr.on('data', (data) => {
                    writeEmitter.fire(data.toString().replace(/\n/g, '\r\n'));
                });

                childProcess.on('error', (err) => {
                    writeEmitter.fire(`\r\nFailed to start Streamlit: ${err.message}\r\n`);
                    closeEmitter.fire(1);
                });

                childProcess.on('close', (code) => {
                    writeEmitter.fire(`\r\nStreamlit exited with code ${code}\r\n`);
                    closeEmitter.fire(code ?? 0);
                });
            },
            close() {
                if (childProcess && !childProcess.killed) {
                    childProcess.kill();
                }
            },
            handleInput(data) {
                // Forward keyboard input to the child process.
                // Ctrl+C is sent as \x03.
                if (data === '\x03') {
                    if (childProcess && !childProcess.killed) {
                        childProcess.kill('SIGINT');
                    }
                } else if (childProcess && childProcess.stdin.writable) {
                    childProcess.stdin.write(data);
                }
            }
        };

        const terminal = vscode.window.createTerminal({
            name: `Streamlit: ${fileName}`,
            pty
        });
        terminal.show();
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
