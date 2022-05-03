#Utility functions

import csv
from datetime import datetime
import os
import shutil

class Game:
    def __init__(self, name, description, price, link,
                 badges=None, original_price=None):
        self.name = name
        self.description = description
        self.price = price
        self.badges = badges if badges else []
        self.original_price = original_price
        self.new_release = "NEW RELEASE" in self.badges
        self.link = link

    def __str__(self):
        return (
            f"{'+' if self.new_release else ' '}"
            f"{self.name} - {self.price}({self.original_price}) "
            f"[{','.join(self.badges)}]"
        )

def create_output_path():
    date_parts = datetime.today().strftime('%Y-%m-%d').split('-')
    date = date_parts[2]
    month = date_parts[1]
    year = date_parts[0]
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results', year, month, date)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            print(f'problem with output directory {path}')
            return
    else:
        os.makedirs(path)
        return path

def generate_csv(system, row_list, field_names):
    output_path = create_output_path()
    if output_path:
        outfile = os.path.join(output_path, f"{system}.csv")
        with open(outfile, 'w') as csvfile:
            # fieldnames = ['title', 'price', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=field_names, extrasaction='ignore')
            writer.writeheader()
            for row in row_list:
                writer.writerow({'title': row.name, 'price': row.price, 'url': row.link})

def generate_html(system, row_list):
    html_header = """
<!doctype html>
<html>
  <head>
    <title>GAME CATALOGUE</title>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.25/css/jquery.dataTables.min.css"/>
    <script src="https://code.jquery.com/jquery-3.6.0.js"></script>
    <script src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
    <script>
      $(document).ready( function () {
        $('#myTable').DataTable( {
          "paging": true,
          "ordering": true,
          "info": true,
          "searching": true,
          "responsive": true
        } );
      } );
    </script>
  </head>
  <body>
    <table id="myTable">
      <thead>
        <tr>
          <th>Title</th>
          <th>Description</th>
          <th>Price</th>
        </tr>
      </thead>
      <tbody>
"""

    html_footer = """
      </tbody>
    </table>
  </body>
</html>
"""
    output_path = create_output_path()
    if output_path:
        outfile = os.path.join(output_path, f"{system}.html")
        with open(outfile, 'w') as htmlfile:
            htmlfile.write(html_header)
            for row in row_list:
                htmlfile.write(
                    "        <tr>\n"
                    f'          <td><a href="{row.link}" target="_blank">{row.name}</a></td>\n'
                    f"          <td>{row.description}</td>\n"
                    f"         <td>{row.price}</td>\n"
                    "        </tr>\n"
                )
            htmlfile.write(html_footer)

def publish():
    source = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'results')
    destination = os.path.join(os.path.expanduser("~"), "Public", "GamePriceList")
    shutil.rmtree(destination)
    shutil.copytree(source, destination)

