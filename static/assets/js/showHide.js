$(function(){$("#add_div").hide();$('#can_btn').hide();
$('#upd_btn').hide();
$('#pic_div').hide();
$(".met_not_form").hide()
})
function showHide(){
    $("#main_div").toggle(500)
    $("#add_div").toggle(500)
}
function applyJob(land){
    $("#land").val(land)
    showHide()
}
function editProfile(){
    $(".inp").removeAttr('readonly');
    $('#edit_btn').hide(300)
    $('#can_btn').show(300)
    $('#upd_btn').show(300)
}
function cancelEdit(){
    $(".inp").attr('readonly', '');
    $('#edit_btn').show(300)
    $('#can_btn').hide(300)
    $('#upd_btn').hide(300)
}
function genBtn(){
    $("#gen_btn").addClass('btn-primary')
    $("#gen_btn").removeClass('btn-secondary');
    $("#met_btn").addClass('btn-secondary')
    $("#met_btn").removeClass('btn-primary');
    $(".gen_not_form").show()
    $(".met_not_form").hide()
}
function metBtn(){
    $("#met_btn").addClass('btn-primary')
    $("#met_btn").removeClass('btn-secondary');
    $("#gen_btn").addClass('btn-secondary')
    $("#gen_btn").removeClass('btn-primary');
    $(".met_not_form").show()
    $(".gen_not_form").hide()
}