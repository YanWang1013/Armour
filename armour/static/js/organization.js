function refreshList()
{
$.ajax({type: 'GET', url: urls.employeelist})
        .done(function (data) {
           $("#employee-list").empty();
           $("#employee-list").html(data.content);
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

function loadNewEmployeeForm()
{
$.ajax({type: 'GET', url: urls.employeeadd})
        .done(function (data) {
           $("#actionModalContent").empty();
           $("#actionModalContent").html(data.content);
           $('#action-form').ajaxForm({success:ActionFormSuccess,error:ActionFormError});
        })
        .fail(function (data) {
            console.log(data.response.error);
        });
}

function loadEditEmployeeForm(item)
{
$.ajax({type: 'GET', url: urls.employeeedit.replace("0",item)})
        .done(function (data) {
           $("#actionModalContent").empty();
           $("#actionModalContent").html(data.content);
           $('#action-form').ajaxForm({success:ActionFormSuccess,error:ActionFormError});
        })
        .fail(function (data) {
            console.log(data.response.error);
        });
}

function loadDeleteEmployeeForm(item)
{
$.ajax({type: 'GET', url: urls.employeedelete.replace("0",item)})
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
});
