$(document).ready(function(){
  $('#add').click(function(e){
    var lbl_img_html = $("#label_image").html();
    $("#label_image").append(lbl_img_html);
    console.log(lbl_img_html);
  });

  $("#remove").click(function(e){
    console.log($("#label_image"));
    var label_image = document.querySelector('#label_image');
    var num_of_child_nodes = label_image.childNodes.length;
    if (num_of_child_nodes == 3) return;
    label_image.removeChild(label_image.childNodes[num_of_child_nodes-1]);
    label_image.removeChild(label_image.childNodes[num_of_child_nodes-2]);
    label_image.removeChild(label_image.childNodes[num_of_child_nodes-3]);
  });
});

