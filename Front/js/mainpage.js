
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
            $(".nedeli").height(h);
        });
        
$("select" ).change(function() {  
    console.log(s);
});