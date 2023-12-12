$(function(){
    $.post("/getUserData/", null,
        function (res) {
            res = JSON.parse(res)
            $("#menu_user_name").text(res[0][0])
            $("#menu_user_role").text(res[0][1])
            $("#menu_user_image").prop("src","/static/uploads/profile_pic/"+res[0][2])
        }
    );
})