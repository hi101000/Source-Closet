function filterSources() {
    let yearRange = $("#yr").val().split(" - ").map(Number);

    // Always select ALL sources, not just visible ones
    let sources = Array.from(document.querySelectorAll(".src_div"));
    sources.forEach(elem => {
        const element = elem.getElementsByClassName("src_link")[0];
        const year = parseInt(element.dataset.year);

        let show = true;

        if (!isNaN(year) && (year < yearRange[0] || year > yearRange[1])) show = false;

        if (show) {
            elem.style.removeProperty("display");
        } else {
            elem.style.display = "none";
        }
    });
}

// Attach to sliders and checkbox
$(function() {
    $("#year").slider({
        range: true,
        min: year_min,
        max: year_max,
        values: [year_min, year_max],
        slide: function(event, ui) {
            $("#yr").val(ui.values[0] + " - " + ui.values[1]);
            filterSources();
        }
    });
    $("#yr").val($("#year").slider("values", 0) +
        " - " + $("#year").slider("values", 1));
});