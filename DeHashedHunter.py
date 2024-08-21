import requests
import argparse
import re
import csv
from requests.auth import HTTPBasicAuth
from jinja2 import Template

# Replace these with your actual DeHashed API credentials
EMAIL = 'your_email@example.com'
API_KEY = 'your_api_key'

# ASCII Art Logo
def print_logo():
    print(r"""
    ____       __  __           __             ____  __            __           
   / __ \___  / / / /___ ______/ /_  ___  ____/ / / / /_  ______  / /____  _____
  / / / / _ \/ /_/ / __ `/ ___/ __ \/ _ \/ __  / /_/ / / / / __ \/ __/ _ \/ ___/
 / /_/ /  __/ __  / /_/ (__  ) / / /  __/ /_/ / __  / /_/ / / / / /_/  __/ /    
/_____/\___/_/ /_/\__,_/____/_/ /_/\___/\__,_/_/ /_/\__,_/_/ /_/\__/\___/_/     
""")

# Function to normalize phone numbers to a plain string format
def normalize_phone_number(phone):
    normalized_phone = re.sub(r'\D', '', phone)
    return normalized_phone

# Function to perform a search using the DeHashed API
def search_dehashed(query, field='email', size=1000, page=1):
    url = f'https://api.dehashed.com/search?query={field}:{query}&size={size}&page={page}'
    
    try:
        response = requests.get(url, auth=HTTPBasicAuth(EMAIL, API_KEY), headers={'Accept': 'application/json'})
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# Function to store results in CSV format
def store_results_csv(query, results, csv_writer):
    if results['success']:
        for entry in results['entries']:
            csv_writer.writerow({
                'query': query,
                'id': entry.get('id'),
                'email': entry.get('email'),
                'username': entry.get('username'),
                'password': entry.get('password'),
                'phone': entry.get('phone'),
                'name': entry.get('name'),
                'database': entry.get('database_name')
            })

# Function to store results in HTML format
def store_results_html(query, results, html_entries):
    if results['success']:
        for entry in results['entries']:
            html_entries.append({
                'query': query,
                'id': entry.get('id'),
                'email': entry.get('email'),
                'username': entry.get('username'),
                'password': entry.get('password'),
                'phone': entry.get('phone'),
                'name': entry.get('name'),
                'database': entry.get('database_name')
            })

# Function to search through all pages for a single query and store results
def search_all_pages(query, field='email', size=1000, csv_writer=None, html_entries=None, silent=False):
    page = 1
    while True:
        results = search_dehashed(query, field, size, page)
        if results and results['entries']:
            if csv_writer:
                store_results_csv(query, results, csv_writer)
            if html_entries is not None:
                store_results_html(query, results, html_entries)
            if not silent:
                for entry in results['entries']:
                    print(entry)
            page += 1
        else:
            break

# Function to handle searching a list of queries
def search_multiple_queries(queries, field='email', size=1000, csv_path=None, html_path=None, silent=False):
    csv_writer = None
    html_entries = []
    
    if csv_path:
        csv_file = open(csv_path, 'w', newline='')
        csv_writer = csv.DictWriter(csv_file, fieldnames=['query', 'id', 'email', 'username', 'password', 'phone', 'name', 'database'])
        csv_writer.writeheader()
    
    for query in queries:
        if not silent:
            print(f"\nSearching for {query} in {field} field...\n")
        if field == 'phone':
            query = normalize_phone_number(query)
        search_all_pages(query, field, size, csv_writer, html_entries, silent)
    
    if csv_path:
        csv_file.close()
    
    if html_path:
        generate_html_report(html_entries, html_path)

# Function to generate an HTML report with scrolling and consistent formatting
def generate_html_report(entries, html_path):
    template = Template('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DeHashedHunter Search Results</title>
        <style>
            body { font-family: Arial, sans-serif; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .container { max-width: 1000px; margin: 0 auto; overflow-x: auto; }
            h2 { margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>DeHashedHunter Search Results</h1>
            {% for entry in entries %}
            <h2>Query: {{ entry.query }}</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Phone</th>
                    <th>Name</th>
                    <th>Database</th>
                </tr>
                <tr>
                    <td>{{ entry.id }}</td>
                    <td>{{ entry.email }}</td>
                    <td>{{ entry.username }}</td>
                    <td>{{ entry.password }}</td>
                    <td>{{ entry.phone }}</td>
                    <td>{{ entry.name }}</td>
                    <td>{{ entry.database }}</td>
                </tr>
            </table>
            {% endfor %}
        </div>
    </body>
    </html>
    ''')
    
    html_content = template.render(entries=entries)
    
    with open(html_path, 'w') as html_file:
        html_file.write(html_content)

# Main function to handle command-line arguments and execute searches
def main():
    print_logo()  # Display the ASCII art logo

    parser = argparse.ArgumentParser(
        description="DeHashedHunter: A tool to search DeHashed data using the API.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--query', type=str, help="Single query (e.g., email address or phone number)")
    parser.add_argument('--list', type=str, help="Path to a file containing a list of queries")
    parser.add_argument('--field', type=str, choices=['email', 'name', 'phone'], default='email',
                        help="Field to search in (default: email)")
    parser.add_argument('--csv', type=str, help="Path to save the CSV report")
    parser.add_argument('--html', type=str, help="Path to save the HTML report")
    parser.add_argument('--silent', action='store_true', help="Run without terminal output (for report-only mode)")

    args = parser.parse_args()

    # Display table of arguments and descriptions
    print("""
    Arguments:
    -------------------------------------------------------------------------
    --query      : Single query (e.g., email address or phone number)
    --list       : Path to a file containing a list of queries
    --field      : Field to search in (default: email). Options: 'email', 'name', 'phone'
    --csv        : Path to save the CSV report
    --html       : Path to save the HTML report
    --silent     : Run without terminal output (for report-only mode)
    -------------------------------------------------------------------------

    Examples:
    -------------------------------------------------------------------------
    Search a single email and output results:
        python dehashedhunter.py --query "example@example.com" --field email --csv results.csv --html results.html
    
    Search a list of phone numbers and save results:
        python dehashedhunter.py --list phones.txt --field phone --csv results.csv --html results.html
    
    Run in silent mode with HTML and CSV reports:
        python dehashedhunter.py --list queries.txt --field name --csv results.csv --html results.html --silent
    -------------------------------------------------------------------------
    """)

    # Handle single query
    if args.query:
        queries = [args.query]
    
    # Handle list of queries
    elif args.list:
        with open(args.list, 'r') as file:
            queries = file.read().splitlines()
    
    else:
        print("Please provide either a single query using --query or a list of queries using --list.")
        return
    
    search_multiple_queries(queries, args.field, csv_path=args.csv, html_path=args.html, silent=args.silent)

if __name__ == "__main__":
    main()                                                                               
