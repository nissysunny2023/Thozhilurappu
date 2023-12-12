$(function () {
    jm_id = location.href.split('/')
    jm_id = jm_id[jm_id.length - 2]
    $.post("/admin/totalAttendance/", { jm_id },
        function (res) {
            $("#total_att").text(res)
        }
    );
    $.post("/admin/employee/attendance/", { 'jm_id': jm_id },
        function (res) {
            res = JSON.parse(res)
            s = ''
            total = 0
            $.each(res, function (i, v) {
                s += '<tr>' +
                    '<td>' + (i + 1) + '</td>' +
                    '<td>' + v[0] + '</td>' +
                    '<td>' + v[2] + '</td>' +
                    '<td>' + v[3] + '</td>' +
                    '</tr>'
                total += Number(v[3])
            });
            $("#tb").html(s)
            $("#total").text(total)

            $.post("/admin/paymentStatus/", { jm_id },
                function (res) {
                    if (res == 1) {
                        amount = $("#total").text()
                        $("#payment_btn").html(
                            '<button class="btn btn-primary" onclick=location.href="/admin/payment/' + jm_id + '/' + amount + '00/">Pay Now</button>'
                        )
                    }
                }
            );
        }
    );

})