// for top nav
var navSize = function () {
    if ($(this).scrollTop() > 100) {
        $(".navbar").removeClass("top");
    }
    else {
        $(".navbar").addClass("top");
    }
}
$(document).ready(navSize);
$(window).scroll(navSize);


// for spyscroll
$(document).ready(function(){
    // Add scrollspy to <body>
    $('body').scrollspy({target: ".navbar", offset: 100});

    // Add smooth scrolling on all links inside the navbar
    $("a.scroll-link").on('click', function(event) {
        // Set offset
        var offset = 100;
        if ($(window).width() < 992) {
            offset = 80;
        }
        // Make sure this.hash has a value before overriding default behavior
        if (this.hash !== "") {
            // Prevent default anchor click behavior
            event.preventDefault();

            // Store hash
            var hash = this.hash;

            // Using jQuery's animate() method to add smooth page scroll
            // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
            $('html, body').animate({
                scrollTop: $(hash).offset().top - offset
            }, 500, function(){

                // Add hash (#) to URL when done scrolling (default click behavior)
                // window.location.hash = hash;
            });
        }  // End if
    });
});
