const fileInput = document.getElementById('cv');
  const label = document.getElementById('cv-label');

  fileInput.addEventListener('change', function () {
    if (fileInput.files.length > 0) {
      label.textContent = 'Uploaded: ' + fileInput.files[0].name;
    } else {
      label.textContent = 'Upload pdf file';
    }
  });