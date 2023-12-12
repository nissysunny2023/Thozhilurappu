$(function () {
    $("#msg").hide()
    je_id = location.href.split('/')
    je_id = je_id[je_id.length - 2]
    $.post("/employee/attendance/", { 'je_id': je_id },
        function (res) {
            res = JSON.parse(res)
            if (res.length > 0) {
                $("#msg").hide()
                $(".table").show()
                s = ''
                $.each(res, function (i, v) {
                    s += '<tr>' +
                        '<td>' + (i+1) + '</td>' +
                        '<td>' + v[0] + '</td>' +
                        '<td>' + v[1] + '</td>' +
                        '<td>'+
                        '<button class="btn btn-sm btn-primary" id="'+v[2]+'" onclick="reportClick(this)">Report</button>'+
                        '</td>'+
                        '</tr>'
                });
                $("#tb").html(s)
            } else {
                $(".table").hide()
                $("#msg").show()
            }
        }
    );

    $("#form").submit(function (e) { 
        e.preventDefault();
        if($(this).valid()){
            $.post("/employee/report/", {'aid':$("#aid").val(),'desc':$('#desc').val()},
                function (res) {
                    if(res==1){
                        alert("Report Submited")
                        location.reload()
                    }else{
                        alert("You have already submited this.")
                        location.reload()
                    }
                }
            );
        }
    });
})

function reportClick(e){
    $('#aid').val($(e).attr('id'))
    showHide()
}