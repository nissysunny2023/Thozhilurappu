$(function () {
    d = location.href.split('/')
    d = d[d.length - 2]
    st = 0
    switch (d) {
        case 'approved':
            st = 1
            break
        case 'pending':
            st = 0
            break
        case 'rejected':
            st = 2
            break
        case 'completed':
            st = 3
            break
    }
    $("#job").change(function () {
        data = { "jid": $(this).val(), st }
        $.post("/admin/jobRequests/get/", data,
            function (res) {
                res = JSON.parse(res)
                s = ''
                x = 1
                $.each(res, function (i, v) {
                    s += '<tr>' +
                        '<td>' + x + '</td>' +
                        '<td>' + v[5] + '</td>' +
                        '<td>' + v[6] + '</td>' +
                        '<td>' + v[2] + '</td>' +
                        '<td>' + v[3] + '</td>' +
                        '<td>'
                    if (v[4] == 0) {
                        s += '<button class="btn btn-sm btn-success" onclick=location.href="/admin/job/requests/manage/1/' + v[0] + '/">Approve</button>' +
                            '<button class="btn btn-sm btn-danger" onclick=location.href="/admin/job/requests/manage/2/' + v[0] + '/">Reject</button>'
                    } else if (v[4] == 1) {
                        s += '<button class="btn btn-sm btn-primary" onclick=location.href="/admin/job/requests/details/' + v[0] + '/">Details</button>'
                    } else if (v[4] == 3) {
                        s += '<button class="btn btn-sm btn-primary" onclick=location.href="/admin/job/requests/payment/' + v[0] + '/">Payment</button>'
                    }
                    s += '</td>' +
                        '</tr>'
                    x++
                });
                $("#tb").html(s)
            }
        );
    })
})