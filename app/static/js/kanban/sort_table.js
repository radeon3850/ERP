//code for sorting the table by columns
    document.addEventListener('DOMContentLoaded', function() {
  var sortButtons = document.querySelectorAll('.dataTable-sorter');

  sortButtons.forEach(function(button) {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      var column = this.textContent.trim();
      sortTable(column);
    });
  });

  function sortTable(column) {
    var table = document.getElementById('datatable-search');
    var rows = Array.from(table.rows).slice(1); // Exclude the header row
    var index;

    switch (column) {
      case '#':
        index = 0;
        break;
      case 'Номер заказа':
        index = 1;
        break;
      case 'Статус':
        index = 2;
        break;
      case 'Вид работы':
        index = 3;
        break;
      case 'Значение':
        index = 4;
        break;
      case 'Дата начала':
        index = 5;
        break;
      case 'Дата окончания':
        index = 6;
        break;
      default:
        return;
    }

    rows.sort(function(a, b) {
      var aValue = a.cells[index].textContent.trim();
      var bValue = b.cells[index].textContent.trim();

      if (aValue < bValue) {
        return -1;
      } else if (aValue > bValue) {
        return 1;
      } else {
        return 0;
      }
    });

    table.tBodies[0].append(...rows);
  }
});