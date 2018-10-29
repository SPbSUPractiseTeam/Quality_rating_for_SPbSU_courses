
    $(document).ready(function() {
            var h=$(this).height();
            var h2=$(".logo").height();
            $(".auth").height(h-h2);
            console.log(h-h2);
        });
