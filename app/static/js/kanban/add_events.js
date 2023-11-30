//скріпт робить поле вибору замовлення не активним

// Отримуємо посилання на елементи DOM
const checkbox = document.getElementById('flexSwitchCheckOrder');
const selectField = document.getElementById('formControlSelectOrder');

// Функція, яка встановлює стан поля select
function setSelectFieldState() {
    // Якщо чекбокс перевірений, робимо поле select неактивним, інакше - активним
    selectField.disabled = checkbox.checked;
}

// Встановлюємо початковий стан при завантаженні сторінки
setSelectFieldState();

// Додаємо обробник події для чекбоксу, щоб оновлювати стан поля select при зміні
checkbox.addEventListener('change', setSelectFieldState);


//скріпт робе поле "название камня" активним при чекнутому "Сляби"

// Отримуємо радіобатони та поле "Название камня"
const radio1 = document.getElementById('customRadio1');
const radio2 = document.getElementById('customRadio2');
const stoneNameField = document.getElementById('stoneName');

// Додаємо обробник подій на зміну вибраного радіобатону
radio1.addEventListener('change', function() {
    if (radio1.checked) {
        stoneNameField.removeAttribute('disabled');
    } else {
        stoneNameField.setAttribute('disabled', 'disabled');
    }
});

radio2.addEventListener('change', function() {
    if (radio2.checked) {
        stoneNameField.setAttribute('disabled', 'disabled');
    } else {
        stoneNameField.removeAttribute('disabled');
    }
});


//JavaScript код для перевірки полів і показу SweetAlert у разі помилки

document.getElementById('form1').addEventListener('submit', function(event) {
  event.preventDefault();

  var slabRadioButton = document.getElementById('customRadio1');
  var isSlabChecked = slabRadioButton.checked;

  var radiofieldWork = ''; // Змінна для зберігання значення полів radiobutton

  if (isSlabChecked) {
    radiofieldWork = slabRadioButton.value; // Якщо "Слябы" обрано, зберігаємо відповідне значення
  } else {
    var partRadioButton = document.getElementById('customRadio2');
    var isPartChecked = partRadioButton.checked;

    if (isPartChecked) {
      radiofieldWork = partRadioButton.value; // Якщо "Детали" обрано, зберігаємо відповідне значення
    }
  }

  var radioButtons = document.getElementsByName('radio_field');
  var isChecked = false;

  for (var i = 0; i < radioButtons.length; i++) {
    if (radioButtons[i].checked) {
      isChecked = true;
      break;
    }
  }

  var selectField = document.getElementById('formControlSelectOrder');
  var selectedValue = selectField.value;

  var checkboxField = document.getElementById('flexSwitchCheckOrder');
  var isCheckboxChecked = checkboxField.checked;

  var thicknessField = document.getElementById('thickness');
  var thicknessValue = thicknessField.value;

  var stoneField = document.getElementById('stone');
  var stoneValue = stoneField.value;

  var inputTextValue = document.getElementById('stoneName').value.trim();

  var work_titleField = document.getElementById('work_title');
  var work_titleValue = work_titleField.value;

  var allowSubmit = false;

  if (isChecked) {
    if (isCheckboxChecked) {
      allowSubmit = true;
    } else {
      if (selectedValue === '0') {
        Swal.fire({
          icon: 'error',
          title: 'Ошибка',
          text: 'Выберите номер заказа, или установите чекбокс "Без номера".',
          confirmButtonColor: '#3085d6',
          confirmButtonText: 'ОК'
        });
      } else {
        allowSubmit = true;
      }
    }
  } else {
    Swal.fire({
      icon: 'error',
      title: 'Ошибка работа не была создана',
      text: 'Выберите направление работ Слябы или Детали.',
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'ОК'
    });
  }

  if (!allowSubmit) {
    return;
  }

  if (stoneValue === '0') {
    Swal.fire({
      icon: 'error',
      title: 'Ошибка',
      text: 'Выберите камень.',
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'ОК'
    });
    return;
  }

  if (isSlabChecked && inputTextValue === '') {
    Swal.fire({
      icon: 'error',
      title: 'Ощибка',
      text: 'Введите название камня.',
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'ОК'
    });
    return;
  }

  if (work_titleValue === '0') {
    Swal.fire({
      icon: 'error',
      title: 'Ошибка',
      text: 'Выберите вид работы.',
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'ОК'
    });
    return;
  }

  if (thicknessValue === '0') {
    Swal.fire({
      icon: 'error',
      title: 'Ошибка',
      text: 'Выберите толщину.',
      confirmButtonColor: '#3085d6',
      confirmButtonText: 'ОК'
    });
    return;
  }

  // Show a confirmation dialog using SweetAlert2
  Swal.fire({
    icon: 'question',
    title: 'Подтверждение',
    text: 'Вы уверены, что хотите отправить форму?',
    showCancelButton: true,
    confirmButtonColor: '#3085d6',
    cancelButtonColor: '#d33',
    confirmButtonText: 'Да',
    cancelButtonText: 'Отмена',
  }).then((result) => {
    if (result.isConfirmed) {
      // If the user confirms, proceed with the form submission


      var checkboxOrder = document.getElementById('flexSwitchCheckOrder').checked;
      var selectOrder = document.getElementById('formControlSelectOrder').value;
      var number = document.getElementById('number').value;
      var selectStone = document.getElementById('stone').value;
      var stoneName = document.getElementById('stoneName').value;
      var selectWorkTitle = document.getElementById('work_title').value;
      var selectWorkType = document.getElementById('work_type').value;
      var selectWorkSubtype = document.getElementById('work_subtype').value;
      var selectThickness = document.getElementById('thickness').options[document.getElementById('thickness').selectedIndex].textContent;
      var valueWork = document.getElementById('value_work').value;

      var formData = {
        'radiofieldwork': radiofieldWork,
        'checkboxorder': checkboxOrder,
        'selectorder': selectOrder,
        'number': number,
        'selectstone': selectStone,
        'stonename': stoneName,
        'selectworktitle': selectWorkTitle,
        'selectworktype': selectWorkType,
        'selectworksubtype': selectWorkSubtype,
        'selectthickness': selectThickness,
        'valuework': valueWork
      };

      $.ajax({
        type: "POST",
        url: "/get_form_kanban",
        data: JSON.stringify(formData),
        contentType: 'application/json',
        success: function(response) {
          var tableBody = document.querySelector(".table tbody");
          var newRow = document.createElement("tr");
          newRow.innerHTML = `
            <td class="align-middle text-sm">${response.sp}</td>
            <td class="align-middle text-sm">${response.number}</td>
            <td class="align-middle text-sm">${response.selectorder}</td>
            <td class="align-middle text-sm">${response.selectstone}</td>
            <td class="align-middle text-sm">${response.stonename}</td>
            <td class="align-middle text-sm">${response.selectworktitle}</td>
            <td class="align-middle text-sm">${response.selectworktype}</td>
            <td class="align-middle text-sm">${response.selectworksubtype}</td>
            <td class="align-middle text-sm">${response.selectthickness}</td>
            <td class="align-middle text-sm">${response.valuework}</td>
            <td>
            <a href="#" data-bs-toggle="tooltip" data-bs-original-title="Удалить">
            <i class="material-icons text-secondary position-relative text-lg">delete</i>
            <input type="hidden" name="work_table" value=${response.sp}>
            <input type="hidden" name="work_id" value=${response.id_table_work}>
             </a>
            </td>
          `;
          tableBody.appendChild(newRow);

          // Clear form fields after successful submission (optional)
          document.getElementById('form1').reset();

          // Optionally, show a success message using SweetAlert2
          Swal.fire({
            icon: 'success',
            title: 'Успех',
            text: 'Данные успешно отправлены на сервер!',
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'ОК',
          });
        },
        error: function(xhr, status, error) {
          // Використовуємо SweetAlert для показу повідомлення про помилку
          Swal.fire({
            icon: 'error',
            title: 'Ошибка',
            text: 'Произошла ошибка при отправке на сервер: ' + error,
          });
        }
      });
    } else {
      // If the user cancels, do nothing (form submission is canceled)
    }
  });
});