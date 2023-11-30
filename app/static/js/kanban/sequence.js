// This function paste html code to <div id='pastselect'> - button and selectfield
// and past data from option list that we response from.
const editLinks = document.querySelectorAll('a[data-bs-original-title="Изменить"]');

editLinks.forEach(function(editLink) {
  editLink.addEventListener('click', function(event) {
    event.preventDefault();

    const td = editLink.closest('td');
    const pastSelectDiv = td.querySelector('#pastselect');
    const selectElement = document.createElement('select');
    selectElement.className = 'form-control';
    selectElement.id = 'selectElement';
    selectElement.name = 'inputFieldName';

    const okButton = document.createElement('button');
    okButton.type = 'button';
    okButton.id = 'okButton';
    okButton.className = 'btn bg-gradient-primary btn-sm';
    okButton.style.cssText = '--bs-btn-padding-y: .15rem; --bs-btn-padding-x: .5rem; --bs-btn-font-size: .60rem;';
    okButton.textContent = 'ок';

    const formHtml = document.createElement('div');
    formHtml.className = 'input-group input-group-static mb-4';
    formHtml.appendChild(selectElement);
    formHtml.insertAdjacentHTML('beforeend', '<div class="text-center"></div>');
    formHtml.lastElementChild.appendChild(okButton);

    pastSelectDiv.innerHTML = '';
    pastSelectDiv.appendChild(formHtml);

    const hiddenInputs = editLink.getElementsByTagName('input');
    const data = {};

    for (let i = 0; i < hiddenInputs.length; i++) {
      const input = hiddenInputs[i];
      const name = input.getAttribute('name');
      const value = input.getAttribute('value');
      data[name] = value;
    }

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/sequence', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.onreadystatechange = function() {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        console.log('Запит успішно відправлено!');
        const response = JSON.parse(xhr.responseText);
        const options = response.options;
        generateSelectOptions(options, selectElement);
      }
    };

    const jsonData = JSON.stringify(data);
    xhr.send(jsonData);
  });
});

// A function for forming a <select> element
function generateSelectOptions(options, selectElement) {
  // Clear existing elements in <select>
  while (selectElement.firstChild) {
    selectElement.removeChild(selectElement.firstChild);
  }

  // Add new items from the options list
  for (let i = 0; i < options.length; i++) {
    const option = document.createElement('option');
    option.value = options[i][0];
    option.textContent = options[i][1];
    selectElement.appendChild(option);
  }
}

//function is get data from <input type"hidden"> and so from selectfield and send it to server
document.addEventListener('click', function(event) {
  if (event.target.matches('#okButton')) {
    const tdElement = event.target.closest('td');
    const selectElement = tdElement.querySelector('#selectElement');
    const hiddenInputs = tdElement.querySelectorAll('input[type="hidden"]');
    console.log(hiddenInputs.length)
    const selectedValue = selectElement.value;
    const inputData = {};

    hiddenInputs.forEach(function(input) {
      const name = input.getAttribute('name');
      const value = input.getAttribute('value');
      inputData[name] = value;
    });

    // AJAX-запит
    $.ajax({
      url: '/sequence',
      type: 'POST',
      contentType: 'application/json',
      data: JSON.stringify({
        selectedValue: selectedValue,
        inputData: inputData
      }),
      success: function(response) {
        console.log('Дані успішно відправлено на сервер!');
        if (response === 'Success') {
          const pastSelectDiv = tdElement.querySelector('#pastselect');
          const valueDiv = document.createElement('div');
          valueDiv.innerHTML = `<h6>${selectedValue}</h6>`;
          pastSelectDiv.innerHTML = '';
          pastSelectDiv.appendChild(valueDiv);
        }
      },
      error: function(error) {
        console.log('Помилка відправки даних на сервер:', error);
      }
    });
  }
});

//this function is dell sequence
// We get all the links
var links = document.querySelectorAll('a[data-bs-original-title="Удалить"]');

// We go through each link
links.forEach(function(link) {
  // We add an event handler for clicking on the link
  link.addEventListener('click', function(event) {
    event.preventDefault(); // We stop the transition by default

    // We get values from <input type="hidden"> tags
    var workType = this.parentNode.querySelector('input[name="work_type"]').value;
    var workId = this.parentNode.querySelector('input[name="work_id"]').value;

    // We create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    //We set the method and URL for the request
    xhr.open('POST', '/dell_sequence', true);

    // We set headers for data transfer in JSON format
    xhr.setRequestHeader('Content-Type', 'application/json');

    // We set the event handler to complete the request
    xhr.onload = function() {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        if (response.status === 'success') {
          //We delete the content of the <div id="pastselect"> tag
          var pastSelectDiv = link.parentNode.querySelector('#pastselect');
          pastSelectDiv.innerHTML = '';
        }
      } else {
        console.log('Помилка при відправленні запиту.');
      }
    };

    // We send data to the server
    xhr.send(JSON.stringify({ workType: workType, workId: workId }));
  });
});



//HTML код знизу

//<td class="d-flex justify-content-between text-sm">
//        {% if work.work_sequence==None %}
//        <div id="pastselect"></div>
//        {% else %}
//        <div id="pastselect">
//            <h6>{{work.work_sequence}}</h6>
//        </div>
//        {% endif %}
//    <a href="javascript:;" class="mx-3" data-bs-toggle="tooltip" data-bs-original-title="Изменить" >
//        <i class="material-icons text-secondary position-relative text-lg">drive_file_rename_outline</i>
//        {% if work.query_preproduct %}
//        <input type="hidden" id="workTypeInput" name="work_type" value="preproduct">
//        {% endif %}
//        {% if work.query_slabworks %}
//        <input type="hidden" id="workTypeInput" name="work_type" value="slabworks">
//        {% endif %}
//        {% if work.query_partworks %}
//        <input type="hidden" id="workTypeInput" name="work_type" value="partworks">
//        {% endif %}
//        <input type="hidden" id="workIdInput" name="work_id" value="{{work.id}}">
//        <input type="hidden" id="workIdOrder" name="order_client" value="{{work.order_of_client}}">
//    </a>
//    <a href="javascript:;" data-bs-toggle="tooltip" data-bs-original-title="Удалить">
//        <i class="material-icons text-secondary position-relative text-lg">delete</i>
//        {% if work.query_preproduct %}
//        <input type="hidden" name="work_type" value="preproduct">
//        {% endif %}
//        {% if work.query_slabworks %}
//        <input type="hidden" name="work_type" value="slabworks">
//        {% endif %}
//        {% if work.query_partworks %}
//        <input type="hidden" name="work_type" value="partworks">
//        {% endif %}
//        <input type="hidden" name="work_id" value="{{work.id}}">
//    </a>
//</td>