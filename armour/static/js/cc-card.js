function stripeResponseHandler(status, response) {

  if (response.error) {
    addAlert("danger", "Credit Card Verification", response.error.message);

  } else {
    var token = response.id;
    $('#id_card_token').val(token);
    $('#cc-card').submit();
  }
}

function beforeSubmit()
{
    $('#id_card_token').val('');
    Stripe.card.createToken({
        number: $('#id_card_num').val(),
        cvc: $('#id_card_code').val(),
        exp_month: $('#id_month_expires').val(),
        exp_year: $('#id_year_expires').val(),
        }, stripeResponseHandler);
}

$(document).ready(function(){
    s_continute = false;
    Stripe.setPublishableKey(STRIPE_KEY);
});
