import json
import os
import sys
import uuid
import requests
import argparse
import time
from urllib.parse import quote

from project_type_groups import PROJECT_TYPE_GROUPS

# Define API version, URL base and Delay
API_VERSION = "2026-03-25"
API_BASE_URL = "https://api.snyk.io"
RATE_LIMIT_DELAY = 0.2

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--group", required=True, help="Group ID")
parser.add_argument("--project-type", choices=sorted(PROJECT_TYPE_GROUPS),
                    help="Only fetch this built-in project type group "
                         "(filters server-side, via the projects endpoint's "
                         "own types= parameter -- avoids pulling every "
                         "project in orgs that have thousands)")
parser.add_argument("--types",
                    help="Comma-separated project_type values instead of "
                         "--project-type, e.g. terraformconfig,k8sconfig")
parser.add_argument("--token", default=os.environ.get("SNYK_TOKEN"),
                    help="API token (defaults to SNYK_TOKEN env var)")
parser.add_argument("--out",
                    help="Output file (default: project_data.json, or "
                         "project_data_<project-type>.json when "
                         "--project-type is given -- so fetching two "
                         "different types doesn't overwrite each other)")
args = parser.parse_args()
if not args.token:
    parser.error("--token is required, or set the SNYK_TOKEN env var")
if args.project_type and args.types:
    parser.error("pass only one of --project-type or --types")

types = PROJECT_TYPE_GROUPS[args.project_type] if args.project_type else \
    ([t.strip() for t in args.types.split(",") if t.strip()] if args.types else None)

if args.out:
    out_path = args.out
elif args.project_type:
    out_path = f"project_data_{args.project_type}.json"
elif args.types:
    out_path = "project_data_custom.json"
else:
    out_path = "project_data.json"

def get_organizations(group_id, api_key):
    try:
        group_id = str(uuid.UUID(group_id))
    except ValueError:
        sys.exit(f"--group must be a UUID, got: {group_id!r}")
    url = f"{API_BASE_URL}/rest/groups/{quote(group_id, safe='')}/orgs?version={API_VERSION}&limit=100"
    headers = {"accept": "application/vnd.api+json", "authorization": f"token {api_key}"}
    organizations = []

    while url:
        start_time = time.time()
        response = requests.get(url, headers=headers)
        end_time = time.time()

        response.raise_for_status()  # Raise error for non-2xx status codes

        data = response.json()
        organizations.extend(data["data"])

        reponse_code = response.status_code
        
        # Print request details
        print(f"Response Code: {reponse_code} - Request URL: {url}")


        # Do not upset the API Overlords 
        time.sleep(RATE_LIMIT_DELAY)

        # Check for next page link
        links = data.get("links", {})
        url = links.get("next")

        # Add "https://api.snyk.io" if missing from next URL
        if url and not url.startswith("https://"):
            url = f"{API_BASE_URL}{url}"
        


    return organizations


def get_projects(org_id, api_key, types=None):
    url = f"{API_BASE_URL}/rest/orgs/{org_id}/projects?version={API_VERSION}&limit=100"
    if types:
        url += "&types=" + quote(",".join(types), safe="")
    headers = {"accept": "application/vnd.api+json", "authorization": f"token {api_key}"}
    projects = []

    while url:
        start_time = time.time()
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        end_time = time.time()

        data = response.json()
        projects.extend(data["data"])

        reponse_code = response.status_code

        # Print request details
        print(f"Response Code: {reponse_code} - Request URL: {url}")

        # Do not upset the API Overlords 
        time.sleep(RATE_LIMIT_DELAY)

        # Check for next page link
        links = data.get("links", {})
        url = links.get("next")

        # Add "https://api.snyk.io" if missing from next URL
        if url and not url.startswith("https://"):
            url = f"{API_BASE_URL}{url}"


    return projects


def extract_project_data(projects, org_name):
    project_data = []
    for project in projects:
        project_info = {
            "org_name": org_name,
            "org_id": project["relationships"]["organization"]["data"]["id"],
            "project_name": project["attributes"]["name"],
            "project_id": project["id"],
            "project_type": project["attributes"]["type"],
            "target_file": project["attributes"]["target_file"],
            "status": project["attributes"]["status"]
        }
        project_data.append(project_info)
    return project_data


def write_to_file(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    group_id = args.group
    api_key = args.token

    organizations = get_organizations(group_id, api_key)
    project_data = []

    for org in organizations:
        org_name = org["attributes"]["name"]
        projects = get_projects(org["id"], api_key, types)
        print(f"  {org_name}: {len(projects)} project(s)")
        org_project_data = extract_project_data(projects, org_name)
        project_data.extend(org_project_data)

    print(f"\n{len(project_data)} project(s) total across {len(organizations)} org(s)")

    # Write the project data to a file
    write_to_file(project_data, out_path)

    print(f"Project data written to {out_path}")
