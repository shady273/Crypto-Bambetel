$(document).ready(function() {
    $('#search-input').on('input', function() {
        var searchQuery = $(this).val();
        if (searchQuery.length >= 3) { // виконуємо запит на сервер, якщо довжина запиту >= 3 символів
            $.ajax({
                url: '/search_coins?q=' + searchQuery,
                type: 'GET',
                success: function(response) {
                    // очистити вікно результатів від попередніх результатів
                    $('#search-results').empty();

                    // створити нові блоки для кожної знайденої монети
                    $.each(response, function(index, coin) {
                        var coinBlock = '<div class="coin-block">' +
                                            '<a href="/' + coin.id_coin + '">' + coin.name + ' (' + coin.symbol + ')' + '</a>' +
                                        '</div>';

                        $('#search-results').append(coinBlock);
                    });

                    // показати вікно результатів
                    $('#search-results').show();
                },
                error: function() {
                    // припустимо, що сталась помилка і показати повідомлення про це
                    $('#search-results').html('<div class="error">An error occurred while processing the search request.</div>');
                    $('#search-results').show();
                }
            });
        } else {
            // очистити вікно результатів і приховати його
            $('#search-results').empty();
            $('#search-results').hide();
        }
    });
});

$(document).ready(function() {
    $(document).on('click', function(event) {
        if (!$(event.target).closest('#search-results').length && !$(event.target).is('#search-results')) {
            $('#search-results').hide();
        }
    });
});

 function buildPlot(data) {
        const layout = {
            title: data[0].name,
            xaxis: {
                tickangle: 25,
                tickfont: {
                    size: 10
                },
                tickvals: data[0].x.filter((_, i) => i % 40 === 0),
                ticktext: data[0].x.filter((_, i) => i % 40 === 0),
            },
            yaxis: {
                title: 'Price'
            }
        };
        Plotly.newPlot('myPlot', data, layout);
    }