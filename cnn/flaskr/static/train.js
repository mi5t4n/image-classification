
$(document).ready(function(){
  var isDirty = true;

  function changeFileInputName(){
    var labels = [];
  
    // Get labels
    $("input[type='text']").each(function(index,element){
      labels.push($(this).val());
      console.log($(this).val());
    });
  
    //Reverse the labels
    labels.reverse();
  
    //Set labels of file uploads
    $("input[type='file']").each(function(index,element){
      $(this).attr('name',labels.pop());
    });

    isDirty = false;
  }

  $('#add').click(function(e){
    var lbl_img_html = $("#label_image").html();
    $("#label_image").append(lbl_img_html);
    // console.log(lbl_img_html);
  });

  $("#remove").click(function(e){
    // console.log($("#label_image"));
    var label_image = document.querySelector('#label_image');
    var num_of_child_nodes = label_image.childNodes.length;
    if (num_of_child_nodes == 3) return;
    label_image.removeChild(label_image.childNodes[num_of_child_nodes-1]);
    label_image.removeChild(label_image.childNodes[num_of_child_nodes-2]);
    label_image.removeChild(label_image.childNodes[num_of_child_nodes-3]);
  });

  $('#apply').click(function(e){
    changeFileInputName();
  });

  // Form Upload Handle
  $("div.progress").hide();
  var progress_bar = $('div.progress-bar');
  var status = $('#status');

  $('form').ajaxForm({
      beforeSubmit: function(arr, $form, options){
        if (isDirty) {
          $('#myModal').modal('toggle')
          return false;
        }
      },
      beforeSend: function() {
        console.log('BeforeSend');
        $("div.progress").show();
          status.empty();
          var percentVal = 0;
          progress_bar.attr("aria-valuenow", percentVal);
          progress_bar.attr("style","width: "+percentVal+"%");
          progress_bar.html(percentVal+'%');
      },
      uploadProgress: function(event, position, total, percentComplete) {
          var percentVal = percentComplete;
          progress_bar.attr("aria-valuenow", percentVal);
          progress_bar.attr("style","width: "+percentVal+"%");
          progress_bar.html(percentVal+'%');
      },
      complete: function(xhr) {
          status.html(xhr.responseText);
      }
  });
});

