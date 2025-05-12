import requests
import os
from datetime import datetime
import csv
import json

def search_github_issues(token=None):
    if not token:
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            raise ValueError("GitHub token not provided")

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    queries = [
        'label:"good first issue" label:accessibility is:issue is:open',
        'label:"good first issue" label:a11y is:issue is:open'
    ]

    all_issues = []
    total_count = 0

    for query in queries:
        print(f"\nSearching query: {query}")
        url = "https://api.github.com/search/issues"
        
        params = {
            "q": query,
            "sort": "created",
            "order": "desc",
            "per_page": 100  
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 403:
                print("Error: Rate limit exceeded or authentication failed")
                return
                
            if response.status_code == 422:
                print("Error: Invalid search query")
                return
                
            response.raise_for_status()
            
            results = response.json()
            query_count = results['total_count']
            total_count += query_count
            
            print(f"Found {query_count} issues for this query")
            
            if query_count > 0:
                all_issues.extend(results['items'])
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            continue

    if not all_issues:
        print("\nNo issues found across all queries")
        return

    # Create CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"github_issues_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Title', 'Repository', 'URL', 'Created Date', 'Labels', 'State', 'Comments Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for issue in all_issues:
            repo_name = '/'.join(issue['repository_url'].split('/')[-2:])
            created_at = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            formatted_date = created_at.strftime("%Y-%m-%d")
            
            writer.writerow({
                'Title': issue['title'],
                'Repository': repo_name,
                'URL': issue['html_url'],
                'Created Date': formatted_date,
                'Labels': ', '.join(label['name'] for label in issue['labels']),
                'State': issue['state'],
                'Comments Count': issue['comments']
            })
    
    print(f"\nTotal issues found: {total_count}")
    print(f"Results saved to {csv_filename}")

if __name__ == "__main__":
    search_github_issues()