(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });


    // Progress Bar
    $('.pg-bar').waypoint(function () {
        $('.progress .progress-bar').each(function () {
            $(this).css("width", $(this).attr("aria-valuenow") + '%');
        });
    }, {offset: '80%'});


    // Calender
    $('#calender').datetimepicker({
        inline: true,
        format: 'L'
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        items: 1,
        dots: true,
        loop: true,
        nav : false
    });


    // Chart Global Color
    Chart.defaults.color = "#6C7293";
    Chart.defaults.borderColor = "#000000";

    //charts    
    $(document).ready(function() {
        // Function to fetch and process data from CSV
        function fetchDataAndProcess(url, columnIndex, chartOptions) {
            $.get(url, function(data) {
                var lines = data.split("\n");
                var dates = [];
                var values = [];
                for (var i = 1; i < lines.length; i++) {
                    var parts = lines[i].split(",");
                    if (parts.length >= columnIndex + 1) {
                        dates.push(parts[0]);
                        values.push(parseFloat(parts[columnIndex]));
                    }
                }
                var last30Dates = dates.slice(-30);
                var last30Values = values.slice(-30);
                createChart(last30Dates, last30Values, chartOptions);
            });
        }
    
        // Function to create Chart.js chart
        function createChart(labels, data, options) {
            var ctx = options.ctx;
            var chartType = options.chartType;
            var chartData = {
                labels: labels,
                datasets: [{
                    label: options.label,
                    backgroundColor: options.backgroundColor,
                    borderColor: options.borderColor,
                    borderWidth: 1,
                    data: data
                }]
            };
            var chartOptions = {
                scales: {
                    y: {
                        beginAtZero: options.beginAtZero || false,
                        suggestedMin: options.suggestedMin || null,
                        suggestedMax: options.suggestedMax || null
                    }
                }
            };
            var myChart = new Chart(ctx, {
                type: chartType,
                data: chartData,
                options: chartOptions
            });
        }
    
        // Define chart options
        var chartOptions = [{
                ctx: document.getElementById('bar-chart').getContext('2d'),
                chartType: 'bar',
                label: 'Water Usage',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                columnIndex: 1
            },
            {
                ctx: document.getElementById('line-chart-1').getContext('2d'),
                chartType: 'line',
                label: 'Temperature',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                columnIndex: 2,
                beginAtZero: false,
                suggestedMin: 23.5,
                suggestedMax: 27
            },
            {
                ctx: document.getElementById('line-chart-2').getContext('2d'),
                chartType: 'line',
                label: 'pH Value',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                columnIndex: 3,
                beginAtZero: false,
                suggestedMin: 14,
                suggestedMax: 0
            },
            {
                ctx: document.getElementById('line-chart-3').getContext('2d'),
                chartType: 'line',
                label: 'TDS',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                columnIndex: 4
            }
        ];
    
        // Fetch and process data for each chart
        chartOptions.forEach(function(options) {
            fetchDataAndProcess("data/dataset.csv", options.columnIndex, options);
        });
    });

    
})(jQuery);

