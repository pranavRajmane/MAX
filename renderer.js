const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const output = document.getElementById('output');
const gmshView = document.getElementById('gmshView');

let pythonProcessRunning = false;

function log(message) {
  console.log(message);
  output.textContent += message + '\n';
}

startBtn.addEventListener('click', async () => {
  try {
    const result = await window.electronAPI.startPythonProcess();
    if (result.success) {
      log(result.message);
      pythonProcessRunning = true;
      sendBtn.disabled = false;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    log(`Error starting Python process: ${error.message}`);
  }
});

stopBtn.addEventListener('click', async () => {
  try {
    const result = await window.electronAPI.stopPythonProcess();
    if (result.success) {
      log(result.message);
      pythonProcessRunning = false;
      sendBtn.disabled = true;
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    log(`Error stopping Python process: ${error.message}`);
  }
});

sendBtn.addEventListener('click', async () => {
  if (!pythonProcessRunning) {
    log('Error: Python process is not running. Please start it first.');
    return;
  }
  const message = userInput.value;
  try {
    const result = await window.electronAPI.sendToPython(message);
    if (result.success) {
      userInput.value = '';
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    log(`Error sending message to Python: ${error.message}`);
  }
});

window.electronAPI.onPythonOutput((event, data) => {
  log(data);
  if (data.includes('MESH_DATA:')) {
    try {
      const meshData = JSON.parse(data.split('MESH_DATA:')[1]);
      updateGmshView(meshData);
    } catch (error) {
      log(`Error parsing mesh data: ${error.message}`);
    }
  }
});

window.electronAPI.onPythonError((event, data) => {
  log('Error: ' + data);
});

window.electronAPI.onPythonClosed((event, code) => {
  log(`Python process exited with code ${code}`);
  pythonProcessRunning = false;
  sendBtn.disabled = true;
});

function updateGmshView(meshData) {
  gmshView.textContent = JSON.stringify(meshData, null, 2);
}

// Initially disable the send button
sendBtn.disabled = true;
