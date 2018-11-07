
function show(Id) {
  var list = document.getElementsByClassName('arhiv');
  for (var i = 0; i < list.length; i++) {
    hide(list[i].id);
  }
    var o=document.getElementById(Id);
    o.style.display =  'inline';
}
function hide(Id){
  var o=document.getElementById(Id);
  o.style.display = 'none';
}
$(document).ready(function() {
  var h=$(this).height();
  $(".rowLeft").height(h);
  $(".fon").height(h);  
});
        
$("select" ).change(function() {  
  var data = ($(".sel1").val());
  var week = ($(".sel2").val());  
  s = "stat_data_"+data+"_week_"+week;
  var list = document.getElementsByClassName('stat');
  for (var i = 0; i < list.length; i++) {
    hide(list[i].id);
  }
  var o = document.getElementById(s);
  o.style.display="inline";
  console.log(o);
  console.log(s);
  
});
/* все для заргузки логов*/
$(document).on('change', '.btn-file :file', function() {
  var input = $(this),
      numFiles = input.get(0).files ? input.get(0).files.length : 1,
      label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
  input.trigger('fileselect', [numFiles, label]);
});

$(document).ready( function() {
	$('.btn-file :file').on('fileselect', function(event, numFiles, label) {
		console.log("teste");
		var input_label = $(this).closest('.input-group').find('.file-input-label'),
			log = numFiles > 1 ? numFiles + ' files selected' : label;

		if( input_label.length ) {
			input_label.text(log);
		} else {
			if( log ) alert(log);
		}
	});
});