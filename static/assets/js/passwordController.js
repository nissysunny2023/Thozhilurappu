$(function () {
    $('#form').submit(function (e) {
        e.preventDefault()
        if ($(this).valid()) {
            if ($("#cpword").val() === $("#npword").val()) {
                $.post("/password/change/", { 'pword': $("#pword").val(), 'npword': $("#npword").val() },
                    function (res) {
                        if (res == 1) {
                            $("#form")[0].reset()
                            $("#msg").addClass('alert-success')
                            $("#msg").removeClass('alert-danger')
                            $("#msg").text('Password Changed')
                        } else {
                            $("#msg").removeClass('alert-success')
                            $("#msg").addClass('alert-danger')
                            $("#msg").text("Wrong Password")
                        }
                    }
                );
            } else {
                $("#msg").removeClass('alert-success')
                $("#msg").addClass('alert-danger')
                $("#msg").text("Password Not Matching")
            }
        }
    })
})