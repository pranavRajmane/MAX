const { exec } = require('child_process');
const file = require('./renderer');
console.log('code reaching here');
// The data you want to send to Python
const data = file.userInput;

// Execute the Python script and pass the data as a command-line argument
exec(
  `python3  ../MAX/shape_extractor.py "${data}"`,
  (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error}`);
      return;
    }

    // Handle the output from the Python script
    console.log(`Python script output: ${stdout}`);
  },
);
