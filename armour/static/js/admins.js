function refreshList()
{
$.ajax({type: 'GET', url: urls.objlist})
        .done(function (data) {
           $("#objects-list").empty();
           $("#objects-list").html(data.content);

        })
        .fail(function (data) {
        });
}

var ActionFormSuccess = function showResponse(responseText, statusText, xhr, $form)  {
    $("#action-close").click();
    $("#actionModalContent").empty();
    refreshList();
}

var ActionFormError = function showResponse(responseText, statusText, xhr, $form)  {
    $("#actionModalContent").empty();
    $("#actionModalContent").html(responseText.responseJSON.content);
    $('#action-form').ajaxForm({success:ActionFormSuccess,error:ActionFormError});
}

function loadNewForm()
{
$.ajax({type: 'GET', url: urls.objadd})
        .done(function (data) {
           $("#actionModalContent").empty();
           $("#actionModalContent").html(data.content);
           $('#action-form').ajaxForm({success:ActionFormSuccess,error:ActionFormError});
           handlePasswordField();
        })
        .fail(function (data) {
            console.log(data.response.error);
        });
}

function loadEditForm(item)
{
$.ajax({type: 'GET', url: urls.objedit.replace("0",item)})
        .done(function (data) {
           $("#actionModalContent").empty();
           $("#actionModalContent").html(data.content);
           $('#action-form').ajaxForm({success:ActionFormSuccess,error:ActionFormError});
           handlePasswordField();
        })
        .fail(function (data) {
            console.log(data.response.error);
        });
}

function loadDeleteForm(item)
{
$.ajax({type: 'GET', url: urls.objdelete.replace("0",item)})
        .done(function (data) {
           $("#actionModalContent").empty();
           $("#actionModalContent").html(data.content);
           $('#action-form').ajaxForm({success:ActionFormSuccess,error:ActionFormError});
        })
        .fail(function (data) {
            console.log(data.response.error);
        });
}

$(document).ready(function(){
    refreshList();
});
