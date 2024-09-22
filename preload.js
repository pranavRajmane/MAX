const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  startPythonProcess: () => ipcRenderer.invoke('startPythonProcess'),
  sendToPython: (message) => ipcRenderer.invoke('sendToPython', message),
  stopPythonProcess: () => ipcRenderer.invoke('stopPythonProcess'),
  onPythonOutput: (callback) => ipcRenderer.on('pythonOutput', callback),
  onPythonError: (callback) => ipcRenderer.on('pythonError', callback),
  onPythonClosed: (callback) => ipcRenderer.on('pythonClosed', callback),
});
