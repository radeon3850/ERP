function filterTableByWorkerName(name) {
    var rows = document.querySelectorAll("#datatable-search tbody tr");

    for (var i = 0; i < rows.length; i++) {
      var workerName = rows[i].querySelector("td:nth-child(6)").innerText.trim();
      if (name === "" || workerName === name) {
        rows[i].style.display = "";
      } else {
        rows[i].style.display = "none";
      }
    }
  }
  var dropdownItems = document.querySelectorAll(".dropdown-item[data-filter]");
  for (var i = 0; i < dropdownItems.length; i++) {
    dropdownItems[i].addEventListener("click", function(event) {
      event.preventDefault();
      var name = this.getAttribute("data-filter");
      filterTableByWorkerName(name);
    });
  }

  // Обработчик клика по элементу "Remove Filter"
  var removeFilterLink = document.querySelector("#filter-remove");
  removeFilterLink.addEventListener("click", function(event) {
    event.preventDefault();
    filterTableByWorkerName(""); // Пустое имя - отображать все записи
  });