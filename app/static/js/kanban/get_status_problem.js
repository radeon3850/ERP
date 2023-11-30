function updateTaskStyles(taskStatuses) {
        $(".task-row").each(function() {
            var taskId = $(this).data("task-id");
            if (taskStatuses[taskId]) {
                $(this).css("background-color", "rgba(235, 62, 120, 0.5)");
                $(this).css("color", "black");
            } else {
                $(this).css("background-color", "");
                $(this).css("color", "");
            }
        });
    }

    $(document).ready(function() {
        setInterval(function() {
            $.ajax({
                url: "/get_task_statuses",
                method: "GET",
                dataType: "json", // Додайте цей рядок для вказання на очікуваний формат відповіді
                success: function(response) {
                    updateTaskStyles(response);
                }
            });
        }, 6000); // Оновлювати кожну хвилину
    });