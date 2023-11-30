const tableContainer = document.querySelector('.table-responsive');

tableContainer.addEventListener('click', (event) => {
  if (event.target.tagName === 'I' && event.target.parentElement.tagName === 'A') {
    event.preventDefault();

    const deleteLink = event.target.parentElement;
    const workTable = deleteLink.querySelector('input[name="work_table"]').value;
    const workId = deleteLink.querySelector('input[name="work_id"]').value;

    Swal.fire({
      title: 'Вы уверенны что хотите удалить задание?',
      text: 'Данные будут удалены без возможности востановления!',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#3085d6',
      cancelButtonColor: '#d33',
      confirmButtonText: 'Да, удалить!',
      cancelButtonText: 'Отмена'
    }).then((result) => {
      if (result.isConfirmed) {
        axios.post('/dell_data_kanban', { workTable, workId })
          .then((response) => {
            console.log('Відповідь сервера:', response.data);

            // Видалення <tr> з вмістом після успішної відповіді сервера
            deleteLink.closest('tr').remove();

            // Показати повідомлення про успішне видалення
            Swal.fire({
              title: 'Успешно удалено!',
              text: 'Задание успешно удалено.',
              icon: 'success',
              timer: 2000,
              showConfirmButton: false
            });
          })
          .catch((error) => {
            console.error('Помилка відправки POST-запиту:', error);
            Swal.fire({
              title: 'Ошибка!',
              text: 'Возникла ошибка при удалении.',
              icon: 'error',
              timer: 2000,
              showConfirmButton: false
            });
          });
      }
    });
  }
});
//this function manage a proces of dell data from DB and table main window not modal window
document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".delete-button");

    deleteButtons.forEach(button => {
        button.addEventListener("click", async function () {
            const workType = this.querySelector("input[name='work_type']").value;
            const workId = this.querySelector("input[name='work_id']").value;

            if (workType === "preproduct") {
                Swal.fire("Ошибка!", "Удалать можно работы только для слябов или деталей.", "error");
                return;
            }

            const result = await Swal.fire({
                title: "Вы уверены?",
                text: "Данные будут удалены.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#d33",
                cancelButtonColor: "#3085d6",
                confirmButtonText: "Да, удалить!",
                cancelButtonText: "Отмена"
            });

            if (result.isConfirmed) {
                try {
                    const response = await fetch("/dell_data_kanban", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            workTable: workType,
                            workId: workId
                        })
                    });

                    const data = await response.json();

                    if (data.status === "successfully" || data.status === "success") {
                       Swal.fire({
                            title: "Успешно!",
                            text: data.message || "Задание успешно удалено",
                            icon: "success",
                            confirmButtonColor: "#3085d6",
                            confirmButtonText: "ОК"
                        });
                        // dell row from table
                        const row = button.closest("tr");
                        row.remove();
                    } else if (data.status === "error") {
                        Swal.fire("Ошибка!", data.message || "Задание не может быть удалено - начат процес производства", "error");
                    }
                } catch (error) {
                    console.error("Ошибка при удалении данных:", error);
                }
            }
        });
    });
});
