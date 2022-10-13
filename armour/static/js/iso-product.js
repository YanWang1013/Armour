function selectResponse(keypoint) {
    let postdata = {};
    let tab = $('#curr-tab').val();
    let reply = '';
    let nc_desc = '';

    $.each($("input[name='repl-" + keypoint + "']:checked"), function () {
        reply = $(this).val();
    });
    let nc = $('#nc-' + keypoint);
    if (reply === '0') {
        nc.show();
        nc_desc = nc.val();
    } else {
        nc.hide();
        nc.val('');
    }

    postdata['keypoint'] = keypoint;
    postdata['keypoint_note'] = $('#note-' + keypoint).val();

    postdata['nc_desc'] = nc_desc;
    postdata['reply'] = reply;
    // postdata['topic'] = $('#id_topic').val();
    // postdata['location'] = $('#id_location').val();
    postdata['position'] = tab;

    $.ajax({
        type: 'POST',
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        url: urls.dataset,
        data: JSON.stringify(postdata),

        success: function (data) {
            setProgress(data.product_progress, $('#progress-product'));
            setProgress(data.all_progress, $('#progress-overall'));
            handleNav();
            burger(tab);
        },

        error: function (data) {
        }
    });

}

function refreshData() {
    // let location = $('#id_location').val();
    // let topic = $('#id_topic').val();

    $.ajax({
        type: 'GET',
        url: urls.datacontent,
        data: {
            // location: location,
            // topic: topic,
        },
    })
        .done(function (data) {
            let iss_content = $("#leg-content");
            iss_content.empty();
            iss_content.html(data.content);
            $(".isostandards").hide();
            $("#tab-1").show();
            $('.curr-tab').val(1);
            setProgress(data.product_progress, $('#progress-product'));
            setProgress(data.all_progress, $('#progress-overall'));
            $(".lg-counter").text("/ " + data.counter)
            setTimeout(function () {
                handleNav();
                burger(1);
            }, 1);
        })
        .fail(function (data) {

        });
}

function nextView() {
    let tab = $('.curr-tab').val();
    let next = parseInt(tab) + 1;
    setView(next);
}

function prevView() {
    let tab = $('.curr-tab').val();
    let next = parseInt(tab) - 1;
    setView(next);
}

function setView(next) {

    if ($(next).is('#curr-tab')) {
        next = $('.curr-tab').val();
    }

    if (next < 1 || $("#tab-" + next).length === 0) {
        return false;
    } else {
        $(".isostandards").hide();
        $("#tab-" + next).show();
        $('.curr-tab').val(next);
        $(window).scrollTop(0);
        handleNav();
        burger(next);
    }
}

function selectQuestion(question, reply) {
    var postdata = {};
    postdata['question'] = question;
    postdata['reply'] = reply;

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
        },

        error: function (data) {
        }
    });
}

function handleErrors() {
    $('.keyp-wrapper').each(function () {
        let $row = $(this);
        let index = $row.index();
        if ($(this).find('.form-radio-input:checked').length === 0) {
            $row.addClass('error');
            $row.find('.form-radio-input').on('change', function () {
                $row.removeClass('error');
            });
        }
        $('.page-nav').find('.btn-nav').each(function () {
            if ($(this).hasClass('open')) {
                $(this).removeClass('open').addClass('error');
            }
        });
    });
}

function handleNav() {
    let tab = $('.curr-tab').val();
    let index = 0;
    $('.page-nav').empty();
    $('#tab-' + tab).find('#Detail_more .keyp-wrapper').each(function () {
        let $row = $(this);
        let status;
        index += 1;
        // check status
        if ($row.find('.form-radio-input:checked').length === 0) {
            if ($row.hasClass('error')) {
                status = 'error';
            } else {
                status = 'open';
            }
        } else {
            status = 'completed';
        }
        // handle button creation
        let btn = "<button class='btn-nav " + status + "' data-index='" + index + "'></button>";
        $('.page-nav').append(btn);
        // handle complete
        $row.find('.form-radio-input').on('change', function () {
            $('.btn-nav[data-index=' + index + ']').removeClass('error').removeClass('open').addClass('completed');
        });
    });
    // handle scrollTo
    $('.btn-nav').on('click', function () {
        let index = $(this).attr('data-index')
        let $scrollTo = $('#tab-' + tab).find(".keyp-wrapper:nth-of-type(" + index + ")");
        $('html, body').animate({
            scrollTop: $scrollTo.offset().top - 110 - 66
        }, 300);
    })
}

// Clark: Add burger function

function burger(tab_number){
    let btn_detail = $('#tab-' + tab_number + ' #btn_detail');
    let btn_burger = $('#tab-' + tab_number + ' #btn_burger');
    let div_burger_more = $('#tab-' + tab_number + ' #Burger_more');
    let div_detail_more = $('#tab-' + tab_number + ' #Detail_more');
    btn_detail.hide();
    div_burger_more.hide();

    btn_burger.on('click', function (){
        $(this).hide();
        btn_detail.show();
        div_detail_more.hide();
        div_burger_more.show();
    })
    btn_detail.on('click', function (){
        $(this).hide();
        btn_burger.show();
        div_burger_more.hide();
        div_detail_more.show();
    })
}

$(document).ready(function () {
    refreshData();
    // handle nav affix
    $(window).scroll(function () {
        let $nav = $('#page-nav-wrapper');
        let scroll = $(window).scrollTop();
        if (scroll >= 284) {
            $nav.addClass('fixed');
        } else {
            $nav.removeClass('fixed');
        }
    });
});
