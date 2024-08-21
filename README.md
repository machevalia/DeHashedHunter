# DeHashedHunter
DeHashedHunter is a Python utility to interact with the DeHashed API. The tool can be used to query single targets such as domain, name, email, and phone numbers or you can provide a list of targets and the utility will query all of them. Users have the option to output results to CSV or HTML reports for easy storage and parsing. 

# User Guide
## Arguments:
    --query      : Single query (e.g., email address or phone number)
    --list       : Path to a file containing a list of queries
    --field      : Field to search in (default: email). Options: 'email', 'name', 'phone'
    --csv        : Path to save the CSV report
    --html       : Path to save the HTML report
    --silent     : Run without terminal output (for report-only mode)
## Examples:
Search a single email and output results:
```python dehashedhunter.py --query "example@example.com" --field email --csv results.csv --html results.html```
Search a list of phone numbers and save results:
```python dehashedhunter.py --list phones.txt --field phone --csv results.csv --html results.html```
Run in silent mode with HTML and CSV reports:
```python dehashedhunter.py --list queries.txt --field name --csv results.csv --html results.html --silent```
