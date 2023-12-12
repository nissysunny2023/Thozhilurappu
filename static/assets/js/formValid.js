$(function(){
    $("#form").validate()

    date = new Date()
    m = (date.getMonth()+1)<10? "0"+(date.getMonth()+1):date.getMonth()+1;
    d = date.getDate()<10? "0"+date.getDate():date.getDate();
    today = (date.getFullYear()-18)+"-"+m+"-"+d
    $("#dob").attr("max",today)
    current = date.getFullYear()+"-"+m+"-"+d
    $("#current_date").attr("min",current)
    

    jQuery.validator.addMethod("phoneStartingWith789", function(phone_number, element) {
        phone_number = phone_number.replace(/\s+/g, ""); 
        return this.optional(element) || phone_number.match(/^9\d{8,}$/) || phone_number.match(/^8\d{8,}$/) || phone_number.match(/^7\d{8,}$/);
    }, "Phone number not valid");


    $.validator.addMethod(
        "regex",
        function(value, element, regexp) {
          var re = new RegExp(regexp);
          return this.optional(element) || re.test(value);
        },
        "Please check your input."
      );

    $("#reg_form").validate(
        {
            rules: {
                name: {
                    required: true,
                    // lettersonly: true,
                },
                address: {
                    required : true,
                },
                place: {
                    required : true,
                },
                city: {
                    required : true,
                },
                pin: {
                    required : true,
                    minlength : 6,
                    maxlength : 6,
                },
                dob:{
                    required : true,
                },
                phone : {
                    required : true,
                    maxlength : 10,
                    minlength : 10,
                    digits : true,
                    phoneStartingWith789 : true,
                },
                email : {
                    required : true,
                    email : true,
                },
                photo : {
                    required : true,
                },
                proof : {
                    required : true,
                },
                pword : {
                    required : true,
                    minlength : 6,
                },
                cpword : {
                    required : true,
                    equalTo : "#pword",
                }
            }
        }
    )
    $("#name").rules("add", { regex: "^[a-zA-Z'.\\s]{1,40}$" })

})