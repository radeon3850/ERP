
// this function for send data about work-id and work-type to assign a responsible employee
function getInsert(clickedButton) {
  var q1 = clickedButton.getAttribute('data-q1');
  var q2 = clickedButton.getAttribute('data-q2');

  console.log('q1:', q1);
  console.log('q2:', q2);

  // paste value to modal window
  document.getElementById('set_worker').querySelector('[name="value1"]').value = q1;
  document.getElementById('set_worker').querySelector('[name="value2"]').value = q2;
}