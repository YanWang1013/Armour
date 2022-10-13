function selectQuestion(question,reply)
{
  var postdata={};
  postdata['question']=question;
  postdata['reply']=reply;

  $.ajax({
    type: 'POST',
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    url: urls.setquestion,
    data: JSON.stringify(postdata),
    /*
    beforeSend: function (xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
  }
},
*/
success: function (data) {
  handleProgress();
},

error: function (data) {
}
});
}

function showHideQuestions()
{
  $('.questionboxes').hide();
  var location = $('#id_location').val();
  var topic = $('#id_topic').val();
  var idx = "#product"+"-"+location+"-"+topic;
  $(idx).show();
}

var oVal = 0;
var cVal = 0;

function handleProgress() {
  // o = overall
  var $oProgress = $('#progress-overall');
  var oTotal = 0;
  var oDone = 0;
  // c = current
  var cProduct = 'product-' + $('#id_location').val() + '-' + $('#id_topic').val();
  var $cProgress = $('#progress-product');
  var cTotal = 0;
  var cDone = 0;

  $('.question-wrapper').each(function() {
    oTotal += 1;
    var $question = $(this);
    if ($(this).find('.form-radio-input:checked').length > 0) {
      oDone += 1;
      $question.removeClass('error');
    }
    if ($(this).parent('.card').prop('id') == cProduct) {
      cTotal += 1;
      if ($(this).find('.form-radio-input:checked').length > 0) {
        cDone += 1;
      };
    }
  });

  oVal = Math.round(oDone/oTotal*100);
  setProgress(oVal,$oProgress);
  cVal = Math.round(cDone/cTotal*100);
  setProgress(cVal,$cProgress);
}

function handleErrors() {
  $('.question-wrapper').each(function() {
    var $question = $(this);
    if ($(this).find('.form-radio-input:checked').length == 0) {
      $question.addClass('error');
    }
  });
}

$(document).ready(function() {
  showHideQuestions();
  handleProgress();
  $('.action-btns').find('.btn-primary').on('click', function(e) {
    if (oVal == 100) {
      e.preventDefault();
      $('#loadingModal').modal('show');
      var href = $(this).attr('href')
      setTimeout(function () {
        window.location.href = href;
      }, 3000);
    }
  });
  $('[data-toggle="tooltip"]').tooltip({
    container: 'body',
    placement: 'top',
    boundary: 'viewport',
  })
});
