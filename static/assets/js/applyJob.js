$(function(){
    jid = location.href.split("/")
    jid = jid[jid.length - 2]
    $.post("/mate/getJobDetails/get/", {jid},
        function (res) {
            res = JSON.parse(res)
            if(res[0] == 1)
            $("#e_type").text('All')
            else
            $("#e_type").text('Below 60 and good health')
            $("#e_no").text(res[1])
        }
    );
})