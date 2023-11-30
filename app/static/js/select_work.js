// all functions below to track selection change for type of jobs, type of jobs, subtype of jobs
$(document).ready(function() {
  // Tracking change in `work_title`
  $('#work_title').change(function() {
    updateWorkTypes();
  });

  // Tracking change in `work_type`
  $('#work_type').change(function() {
    updateWorkSubtypes();
  });

  // A function to query the server and update the `work_subtype`
  function updateWorkSubtypes() {
    var workTitle = $('#work_title').val();
    var workType = $('#work_type').val();

    $.ajax({
      url: '/get_work_subtypes',  // URL for your `/get_work_subtypes` route
      method: 'POST',
      data: {
        work_title: workTitle,
        work_type: workType
      },
      success: function(response) {
        // Update `work_subtype` with list received from server
        $('#work_subtype').empty();
        for (var i = 0; i < response.choices.length; i++) {
          var choice = response.choices[i];
          $('#work_subtype').append($('<option>', {
            value: choice[0],
            text: choice[1]
          }));
        }
      }
    });
  }

  // A function to update the `work_type` list based on the selection of `work_title`
  function updateWorkTypes() {
    var workTitle = $('#work_title').val();

    $.ajax({
      url: '/get_work_types',  // URL for your `/get_work_types route`
      method: 'POST',
      data: {
        work_title: workTitle
      },
      success: function(response) {
        // Updating `work_type` with the list received from the server
        $('#work_type').empty();
        for (var i = 0; i < response.choices.length; i++) {
          var choice = response.choices[i];
          $('#work_type').append($('<option>', {
            value: choice[0],
            text: choice[1]
          }));
        }
        updateWorkSubtypes(); // Update work_subtypes after update work_types
      }
    });
  }

  // Call the function to update the `work_type` list when the page is loaded
  updateWorkTypes();
});
