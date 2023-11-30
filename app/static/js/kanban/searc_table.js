// This function for Search by table of page "kanban"
document.addEventListener('DOMContentLoaded', function() {
  var searchInput = document.getElementById('searchInput');

  searchInput.addEventListener('input', function() {
    var searchText = this.value.trim().toLowerCase();
    filterTable(searchText);
  });

  function filterTable(searchText) {
    var table = document.getElementById('datatable-search');
    var rows = Array.from(table.querySelectorAll('tbody tr'));

    rows.forEach(function(row) {
      var columns = Array.from(row.cells);
      var match = false;

      columns.forEach(function(column) {
        var cellText = column.textContent.trim().toLowerCase();
        if (cellText.includes(searchText)) {
          match = true;
          return;
        }
      });

      row.style.display = match ? 'table-row' : 'none';
    });
  }
});