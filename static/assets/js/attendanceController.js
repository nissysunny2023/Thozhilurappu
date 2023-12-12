$(function () {
    $("#msg").hide()
    $("#msg1").hide()
    $(".table").hide()
    $("#main_div").show()
    $("#add_div").hide()
})

function showHideAtt() {
    $.post("/mate/getAttDate/", { 'jm_id': $("#jm_id").val() },
        function (res) {
            if (res == 1) {
                $.post("/mate/getAttEmployee/", { 'jm_id': $("#jm_id").val() },
                    function (data) {
                        data = JSON.parse(data)
                        if (data.length > 0) {
                            $("#msg").hide()
                            $("#t2").show()
                            s = ''
                            x = 1
                            $.each(data, function (i, v) {
                                s += '<tr>' +
                                    '<td>' + x + '</td>' +
                                    '<td>' + v[1] + '</td>' +
                                    '<td>' +
                                    '<input type="radio" required name="emp' + v[0] + '" value="1">Present' +
                                    '<input type="radio" required name="emp' + v[0] + '" value="0">Absent' +
                                    '</td>' +
                                    '</tr>'
                                x++
                            });
                            $("#tb1").html(s)
                        } else {
                            $("#msg").show()
                            $("#t2").hide()
                        }
                    }
                );
                $("#main_div").toggle(500)
                $("#add_div").toggle(500)
            } else if (res == 2) alert("You Have Already Marked Today's Attendance.")
            else if (res == 0) alert("Work Not Yet Started.")
            else if (res == 3) alert("Work Has Been Ended.")
        }
    );
}

function getAttendance(date) {
    data = { 'date': date, 'jm_id': $("#jm_id").val() }
    $.post("/mate/getAttendance/", data,
        function (res) {
            res = JSON.parse(res)
            if (res.length > 0) {
                $("#msg").hide()
                $(".table").show()
                s = ''
                d = ''
                x = 1
                $.each(res, function (i, v) {
                    s += '<tr>' +
                        '<td>' + x + '</td>' +
                        '<td>' + v[0] + '</td>' +
                        '<td>' + v[1] + '</td>' +
                        '<td>' +
                        '<button class="btn btn-sm btn-primary" onclick=location.href="/mate/attendance/reports/' + v[2] + '/">Reports</button>' +
                        '</td>' +
                        '</tr>'
                    d += '<tr>' +
                        '<td>' + x + '</td>' +
                        '<td>' + v[0] + '</td>' +
                        '<td>' + v[1] + '</td>' +
                        '</tr>'
                    x++
                });
                $("#tb").html(s)
                $("#tb2").html(d)
                $('#report_date').text(date);
            } else {
                $("#msg").show()
                $("#t1").hide()
            }
        }
    );
}

function reportGenerate() {
    var style = "<style>";
    style = style + "table {width: 100%;font: 17px Calibri;}";
    style = style + "table, th, td {border: solid 1px #DDD; border-collapse: collapse;";
    style = style + "padding: 2px 3px;}";
    style = style + "</style>";
    var data = document.getElementById('report_table').innerHTML;
    var obj = window.open('', '', 'height=700,width=700');
    obj.document.write('<html><head>');
    obj.document.write('<title>Attendance Report</title>');
    obj.document.write(style);
    obj.document.write('</head>');
    obj.document.write('<body>');
    obj.document.write(data)
    obj.document.write('</body></html>');
    obj.document.close()
    obj.print()
}