
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
  $("div.progress-upload").hide();
  $("div.progress-train").hide();
  var progress_bar_upload = $('div.progress-upload > div.progress > div.progress-bar');
  var progress_bar_train = $('div.progress-train > div.progress > div.progress-bar');
  var status_train = $('div#status-train');
  var status_upload = $('div#status-upload');

  $('form').ajaxForm({
      beforeSubmit: function(arr, $form, options){
        if (isDirty) {
          $('#myModal').modal('toggle');
          return false;
        }
      },
      beforeSend: function() {
        status_train.html("Uploading ...");
        status_upload.html("");
        $("div.progress-train").hide();
        console.log('BeforeSend');
        $("div.progress-upload").show();
        $("div.progress-train").hide();
        status_train.empty();
        var percentVal = 0;
        progress_bar_upload.attr("aria-valuenow", percentVal);
        progress_bar_upload.attr("style","width: "+percentVal+"%");
        progress_bar_upload.html(percentVal+'%');
      },
      uploadProgress: function(event, position, total, percentComplete) {
        var percentVal = percentComplete;
        progress_bar_upload.attr("aria-valuenow", percentVal);
        progress_bar_upload.attr("style","width: "+percentVal+"%");
        progress_bar_upload.html(percentVal+'%');
      },
      complete: function(xhr) {
        status_upload.html("Uploaded successfully !!!");
        json_res = JSON.parse(xhr.responseText);
        uid = json_res.uid;
        console.log("uid = " + uid)

        $("div.progress-upload").show();
        $("div.progress-train").show();
        status_train.html("Training ....");
        
        var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('connect', function() {
            socket.emit('train', json_res);
        });

        socket.on('trainstatus', function(data){
          data = JSON.parse(data);
          console.log('trainstatus');
          console.log(data);
          console.log(data.complete);
          if (data.complete == 'true'){
            socket.disconnect();
            $("h2#test-link").html(data.uid);
            $("div.progress-train").hide();
            $('div#status-train').html("Training Finished !!!");
          }
        });
      }
  });
});

