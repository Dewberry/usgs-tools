$(document).keyup(function(event) {
    if ($("#number").is(":focus") && (event.key == "Enter")) {
        $("#getInfo").click();
    }
});