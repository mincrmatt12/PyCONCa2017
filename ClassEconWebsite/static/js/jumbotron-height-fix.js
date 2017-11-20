$( window ).resize(function() {
    $(".navbar").data("bs.affix").options.offset = $("#jumbotron-height-wrapper").height();
});
$(".navbar").data("offset-top",$("#jumbotron-height-wrapper").height());;