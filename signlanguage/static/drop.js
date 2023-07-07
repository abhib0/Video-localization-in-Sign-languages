
// Get the input field
var input = document.getElementById("myInput");

// Execute a function when the user presses a key on the keyboard
input.addEventListener("keypress", function(event) {
  // If the user presses the "Enter" key on the keyboard
  if (event.key === "Enter") {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    document.getElementById("myBtn").click();
  }
});



function getCount(foldername) { 
  var myObject, f, filesCount; 
  // Create an instance of the FileSystemObject 
  myObject = new ActiveXObject("Scripting.FileSystemObject"); 
  f = myObject.GetFolder(foldername); 
  // gets the number of files in a folder 
  filesCount = f.files.Count; 
  document.write("The number of files in this folder is: " + filesCount);
}







const events = ['dragenter', 'dragover', 'dragleave', 'drop'];

const dropArea = document.getElementById('drop-area');

const handleFiles = files => {
    uploadFiles(files);
}

const uploadFiles = files => {
    console.log(files);
}

const handleDrop = event => {
    const files = event;
    console.log(event);
}

dropArea.addEventListener('drop', handleDrop);