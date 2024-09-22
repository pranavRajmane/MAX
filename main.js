const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let pythonProcess;

const pythonPath = 'python3'; // or use the full path like '/usr/bin/python3'

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.loadFile('index.html');
  mainWindow.webContents.openDevTools(); // For debugging
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

ipcMain.handle('startPythonProcess', async (event) => {
  try {
    console.log('Starting Python process...');
    const scriptPath = path.join(__dirname, 'MAX', 'use_shape_extractor.py');

    // Check if the Python script exists
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Python script not found at ${scriptPath}`);
    }

    pythonProcess = spawn(pythonPath, [scriptPath]);

    pythonProcess.stdout.on('data', (data) => {
      console.log(`Python stdout: ${data}`);
      mainWindow.webContents.send('pythonOutput', data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error(`Python stderr: ${data}`);
      mainWindow.webContents.send('pythonError', data.toString());
    });

    pythonProcess.on('close', (code) => {
      console.log(`Python process exited with code ${code}`);
      mainWindow.webContents.send('pythonClosed', code);
    });

    pythonProcess.on('error', (error) => {
      console.error('Failed to start Python process:', error);
      mainWindow.webContents.send('pythonError', error.message);
      throw error;
    });

    return { success: true, message: 'Python process started successfully' };
  } catch (error) {
    console.error('Error in startPythonProcess:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('sendToPython', async (event, message) => {
  try {
    if (pythonProcess && !pythonProcess.killed) {
      pythonProcess.stdin.write(message + '\n');
      return { success: true };
    } else {
      throw new Error('Python process is not running');
    }
  } catch (error) {
    console.error('Error in sendToPython:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stopPythonProcess', async (event) => {
  try {
    if (pythonProcess && !pythonProcess.killed) {
      pythonProcess.kill();
      return { success: true, message: 'Python process stopped' };
    } else {
      return { success: true, message: 'Python process was not running' };
    }
  } catch (error) {
    console.error('Error in stopPythonProcess:', error);
    return { success: false, error: error.message };
  }
});
