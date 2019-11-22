#Utility functions

import csv
from datetime import datetime

def generate_csv(system, row_list, field_names):
    outfile = f"{system}-{datetime.today().strftime('%Y-%m-%d')}.csv"
    with open(outfile, 'w') as csvfile:
        # fieldnames = ['title', 'price', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=field_names, extrasaction='ignore')
        writer.writeheader()
        for row in row_list:
            writer.writerow(row)

def generate_html(system, row_list):
    html_header = """
<!doctype html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <style>
            body { max-width:60rem; margin: auto; }
            table { width: 100%; }
        </style>
        <script>
        </script>
    </head>
    <body>
        <table>
            <tr>
                <th>Name</th>
                <th>
                    Price 
                    <select>
                        <option value="-2.0">Pre Order</option>
                        <option value="-1.0">Unavailable</option>
                        <option value="0.0">Free</option>
                        <option value="100-199">100-199</option>
                        <option value="200-299">200-299</option>
                        <option value="300-399">300-399</option>
                        <option value="400-499">400-499</option>
                        <option value="500-599">500-599</option>
                        <option value="600-699">600-699</option>
                        <option value="700-799">700-799</option>
                        <option value="800-899">800-899</option>
                        <option value="900-999">900-999</option>
                        <option value="1000-1499">1000-1499</option>
                        <option value="1500-1999">1500-1999</option>
                        <option value="2000-2499">2000-2499</option>
                        <option value="2500-99999">2500+</option>
                    </select>
                </th>
            </tr>
"""

    html_footer = """
        </table>
    </body>
    <script>
        function get_min_max() {
            elems = document.querySelectorAll('option')
            for (var i=0; i<elems.length; i++) {
                e=elems[i];
                if (e.selected) {
                    // console.log(e);
                    range = e.value;
                    if (["0.0", "-1.0", "-2.0"].includes(range)) {
                        if (range === "0.0") {
                            min = -0.1;
                            max = 0.0;
                        } else if (range === "-1.0") {
                            min = -1.1;
                            max = -1.0;
                        } else if (range === "-2.0") {
                            min = -2.1;
                            max = -2.0;
                        }
                    } else {
                        values = range.split("-")
                        min = parseFloat(values[0]);
                        max = parseFloat(values[1]);
                    }
                    return [min, max]
                }
            }
        }

        function filter(event) {
            // console.log(event.target);
            range = get_min_max();
            min = range[0];
            max = range[1];
            price_elems = document.querySelectorAll('td[data-price]');
            printed=false;
            price_elems.forEach(function(element) {
                game_price = parseFloat(element.innerHTML);
                // console.log(game_price > min, game_price < max);
                if (game_price > min && game_price < max+1) {
                    // console.log(element.innerHTML);
                    element.parentElement.style.display = "";
                } else {
                    element.parentElement.style.display = "none";
                }
            });
        }
        var price_selector = document.querySelectorAll('select')
        for (var i=0; i < price_selector.length; i++) {
            e = price_selector[i];
            e.addEventListener("change", filter);
        }
    </script>
</html>
"""
    outfile = f"{system}-{datetime.today().strftime('%Y-%m-%d')}.html"
    with open(outfile, 'w') as htmlfile:
        htmlfile.write(html_header)
        for row in row_list:
            htmlfile.write(
                f"""
            <tr>
                <td>
                    <a href="{row["url"]}" target="_blank">{row["title"]}</a>
                </td>
                <td data-price>{row["price"]}</td>
            </tr>""")
        htmlfile.write(html_footer)
