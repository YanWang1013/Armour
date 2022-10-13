var contactFormSuccess = function showResponse(responseText, statusText, xhr, $form)  {
    $("#contact-section").empty();
    $("#contact-section").html(responseText.content);
    $('#contact-form').ajaxForm({success:contactFormSuccess});
    alert("Message was sent");
}

function loadContact()
{
$.ajax({type: 'GET', url: urls.contact})
        .done(function (data) {
           $("#contact-section").empty();
           $("#contact-section").html(data.content);

           $('#contact-form').ajaxForm({success:contactFormSuccess});

        })
        .fail(function (data) {
            console.log(data.response.error);
        });
}