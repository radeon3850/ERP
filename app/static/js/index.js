var acc = document.getElementsByClassName("accordion");
var i;

for (i = 0; i < acc.length; i++) {
  acc[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var panel = this.nextElementSibling;
    if (panel.style.maxHeight){
      panel.style.maxHeight = null;
    } else {
      panel.style.maxHeight = panel.scrollHeight + "px";
    }
  });
}

// code for sorting the table by columns
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
  case 'Заказ':
    index = 0;
    break;
  case 'Название':
    index = 1;
    break;
  case 'Статус':
    index = 2;
    break;
  case 'Камень':
    index = 3;
    break;
  case 'Адрес':
    index = 4;
    break;
  case 'Дедлайн':
    index = 5;
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

// table search code
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

//using filters
document.addEventListener('DOMContentLoaded', function() {
  var filterPaid = document.getElementById('filter-paid');
  var filterRefunded = document.getElementById('filter-refunded');
  var filterCanceled = document.getElementById('filter-canceled');
  var filterRemove = document.getElementById('filter-remove');

  filterPaid.addEventListener('click', function(e) {
    e.preventDefault();
    filterTable('В работе');
  });

  filterRefunded.addEventListener('click', function(e) {
    e.preventDefault();
    filterTable('Ожидает');
  });

  filterCanceled.addEventListener('click', function(e) {
    e.preventDefault();
    filterTable('Завершён');
  });

  filterRemove.addEventListener('click', function(e) {
    e.preventDefault();
    clearFilter();
  });

  function filterTable(status) {
    var table = document.getElementById('datatable-search');
    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
      var row = rows[i];
      var statusCell = row.cells[2].querySelector('span');

      if (statusCell.textContent !== status) {
        row.style.display = 'none';
      } else {
        row.style.display = '';
      }
    }
  }

  function clearFilter() {
    var table = document.getElementById('datatable-search');
    var rows = table.getElementsByTagName('tr');

    for (var i = 1; i < rows.length; i++) {
      rows[i].style.display = '';
    }
  }
});

//this code sends data to the server about order approval with a confirmation window + controls the logic of button activity
function showConfirmation(index) {
    event.preventDefault(); // Prevents the page from reloading
    Swal.fire({
        title: 'Вы уверенны?',
        text: 'Утвердить заказ клиента!',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#5cb360',
        cancelButtonColor: '#e94441',
        confirmButtonText: 'Да, утвердить заказ!',
        cancelButtonText: 'Нет, отменить!'
    }).then(result => {
        if (result.isConfirmed) {
            const form = document.getElementById('orderForm' + index);
            const orderId = form.elements["q"].value;
            window.location.href = "/approved?q=" + encodeURIComponent(orderId);
        }
    });

    // Change the text of the cancel button
    $('.swal2-cancel').removeClass('bg-gradient-danger').addClass('bg-gradient-primary btn').text('Нет, отменить!');

    // Change the confirmation button text
    $('.swal2-confirm').removeClass('bg-gradient-success').addClass('bg-gradient-primary btn').text('Да, утвердить заказ!');
}