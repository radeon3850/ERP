// проверка поля выбора клиента - если пусто всплывает алерт
var clientIdSelect = document.getElementById("clientIdmControlSelect1");
var form = document.getElementById("form_addorder"); // Замініть "yourForm" на ідентифікатор вашої форми

form.addEventListener("submit", function(event) {
  var clientIdValue = clientIdSelect.value;

  if (!clientIdValue || clientIdValue === '0') {
    event.preventDefault(); // Зупинити відправку форми

    Swal.fire({
      title: "Заказ не был создан!",
      text: "Не указан клиент заказа",
      icon: "error",
      confirmButtonText: "OK"
    });
  }
});