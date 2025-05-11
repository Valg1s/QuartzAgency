const fileInput = document.getElementById('cv');
const label = document.getElementById('cv-label');

if (fileInput && label){
  fileInput.addEventListener('change', function () {
    if (fileInput.files.length > 0) {
      label.textContent = 'Uploaded: ' + fileInput.files[0].name;
    } else {
      label.textContent = 'Upload pdf file';
    }
  });
}


window.addEventListener('load', function () {

  console.log(window.location.pathname)
  if (window.location.pathname !== '/') {
    return;
  }

  function pollSession() {
    fetch('/api/session-status/')
      .then(response => {
        if (response.status === 401) {
          console.warn("Session expired, redirecting...");
          window.location.href = "/login/";
        } else {
          setTimeout(pollSession, 5000);
        }
      })
      .catch(error => {
        console.error("Session check failed:", error);
        window.location.href = "/login/";
      });
  }

  pollSession();
});
