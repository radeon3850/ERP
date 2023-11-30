window.onload = function() {
    if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.href);
    }
}

//refresh page if does nothing on the page
let timeoutId;

function resetTimer() {
  clearTimeout(timeoutId);
  timeoutId = setTimeout(function() {
    location.reload();
  }, 60000); //1 minute in milliseconds
}

document.addEventListener('mousemove', resetTimer);
document.addEventListener('keydown', resetTimer);
document.addEventListener('scroll', resetTimer);

resetTimer(); // call the resetTimer function to set the timer immediately on page load