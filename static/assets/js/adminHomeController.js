$(function(){
    $("#job").change(function(){
        let data = {'jid':$(this).val()}
        $.post("/admin/getMates/get/", data,
            function (res) {
                res = JSON.parse(res)
                s = ''
                $.each(res, function (i, v) { 
                     s += '<option value="'+v[0]+'">'+v[1]+'</option>'
                });
                $("#mate").html(s)
            }
        );
    })
})
