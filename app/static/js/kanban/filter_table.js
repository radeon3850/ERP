function filterTable() {
  var orderNumberFilter = document.getElementById("orderNumberFilter").value.toLowerCase();
  var statusFilter = document.getElementById("statusFilter").value.toLowerCase();
  var workTitleFilter = document.getElementById("workTitleFilter").value.toLowerCase();
  var workTypeFilter = document.getElementById("workTypeFilter").value.toLowerCase();
  var valueFilter = document.getElementById("valueFilter").value.toLowerCase();
  var workerFilter = document.getElementById("workerFilter").value.toLowerCase();
  var startDateFilter = document.getElementById("startDateFilter").value.toLowerCase();
  var endDateFilter = document.getElementById("endDateFilter").value.toLowerCase();
  var spFilter = document.getElementById("spFilter").value.toLowerCase();
  var numberFilter = document.getElementById("numberFilter").value.toLowerCase();

  var rows = document.querySelectorAll("#datatable-search tbody tr");

  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var orderNumber = row.querySelector("td:nth-child(3)").innerText.toLowerCase();
    var status = row.querySelector("td:nth-child(4)").innerText.toLowerCase();
    var workTitle = row.querySelector("td:nth-child(5)").innerText.toLowerCase();
    var workType = row.querySelector("td:nth-child(6)").innerText.toLowerCase();
    var value = row.querySelector("td:nth-child(7)").innerText.toLowerCase();
    var worker = row.querySelector("td:nth-child(8)").innerText.toLowerCase();
    var startDate = row.querySelector("td:nth-child(9)").innerText.toLowerCase();
    var endDate = row.querySelector("td:nth-child(10)").innerText.toLowerCase();
    var sp = row.querySelector("td:nth-child(1)").innerText.toLowerCase();
    var number = row.querySelector("td:nth-child(2)").innerText.toLowerCase();

    if (
      orderNumber.includes(orderNumberFilter) &&
      status.includes(statusFilter) &&
      workTitle.includes(workTitleFilter) &&
      workType.includes(workTypeFilter) &&
      value.includes(valueFilter) &&
      worker.includes(workerFilter) &&
      startDate.includes(startDateFilter) &&
      endDate.includes(endDateFilter) &&
      sp.includes(spFilter) &&
      number.includes(numberFilter)
    ) {
      row.style.display = "table-row";
    } else {
      row.style.display = "none";
    }
  }
}

document.getElementById("orderNumberFilter").addEventListener("input", filterTable);
document.getElementById("statusFilter").addEventListener("input", filterTable);
document.getElementById("workTitleFilter").addEventListener("input", filterTable);
document.getElementById("workTypeFilter").addEventListener("input", filterTable);
document.getElementById("valueFilter").addEventListener("input", filterTable);
document.getElementById("workerFilter").addEventListener("input", filterTable);
document.getElementById("startDateFilter").addEventListener("input", filterTable);
document.getElementById("endDateFilter").addEventListener("input", filterTable);
document.getElementById("spFilter").addEventListener("input", filterTable);
document.getElementById("numberFilter").addEventListener("input", filterTable);
