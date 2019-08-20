// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable1').DataTable({
    "order": [[ 0, "desc" ]]
  });
  $('#dataTable2').DataTable({
    "order": [[ 3, "desc" ]]
  });
});
