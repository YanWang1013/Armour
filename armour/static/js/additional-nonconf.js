var currForm;
var currTab;
var $pills = $('#v-pills-tab');
const $status = $('#id_status');
const $priority = $('#id_priority');
var dataStatus = '';
var dataPriority = '';

$(document).ready(function() {
    currTab = $('#curr-tab').val();
    currForm = $('#form-' + currTab).serialize();
});

var ActionFormSuccess = function showResponse(responseText, statusText, xhr, $form)  {
    var id = responseText.id;
    var verify = responseText.verify;
    var priority = $form.find('select[name="priority"]').val();
    var nctype = responseText.nctype;
    var index = $form.find('input[name="form-tab"]').val();
    var $thisPill = $("#v-pills-" + nctype + "-" + index + "-tab");

    if (verify == 1) {
        $thisPill.attr('data-status' , 'completed');
    } else {
        $thisPill.attr('data-status' , 'open');
    }

    $thisPill.attr('data-priority' , priority);

    if (responseText.content != '') {
        $("#tabs-content").empty();
        $("#tabs-content").html(responseText.content);
        $pills = $('#v-pills-tab');
    }

    addAlert("success", "Success", "Data has been saved");
}

var ActionFormError = function showResponse(responseText, statusText, xhr, $form)  {

}

function submitForm() {
    $form = $("#form-" + currTab);
    $form.submit();
}

function setView(next) {
    saveForm = $("#form-" + currTab).serialize();
    if (saveForm !== currForm) {
        $('#form-' + currTab).ajaxForm({success: ActionFormSuccess, error: ActionFormError});
        submitForm();
    }
    $('#curr-tab').val(next);
    $('#curr-page').text(next);
    currTab = $('#curr-tab').val();
    currForm = $('#form-' + next).serialize();
}

function nextView() {
    var $next = $pills.find('a.active').nextAll('a:not(.d-none):first');
    $next.click();
    $(window).scrollTop(0);
}

function prevView(e) {
    var $prev = $pills.find('a.active').prevAll('a:not(.d-none):first');
    $prev.click();
    $(window).scrollTop(0);
}

function AddView() {
    $('#add-new-' + currTab).val(1);
    submitForm();
}

function filterStatus() {
    var status = $status.val();

    if (status == 'open') {
        $priority.parents('.form-group').removeClass('d-none');
    } else {
        $priority.parents('.form-group').addClass('d-none');
        $priority.val('any').change();
    }

    if (status == 'all') {
        dataStatus = '';
    } else {
        dataStatus = '[data-status="' + status + '"]';
    }

    filterData(dataStatus, dataPriority);
}

function filterPriority() {
    var status = $status.val();
    var priority = $priority.val();

    if (priority == 'any') {
        dataPriority = '';
    } else {
        dataPriority = '[data-priority="' + priority + '"]';
    }

    if (status == 'open') {
        filterData(dataStatus, dataPriority);
    }
}

function filterData(dataStatus, dataPriority) {
    $pills.find('a').each(function() {
        if ($(this).is('a' + dataStatus + dataPriority)) {
            $(this).removeClass("d-none");
        } else {
            $(this).addClass("d-none");
        }
    }).promise().done(function() {
        $pills.find('a:not(.d-none):first').click();
    })
}
