import os
import requests
import json
import argparse


def deactivate_or_activate_project(org_id, project_id, action, token, org_name, project_name):
    """
    Deactivates or activates a project based on the specified action.
    """
    url = f"https://api.snyk.io/v1/org/{org_id}/project/{project_id}/{action}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"token {token}",
        "Content-Type": "application/vnd.api+json"
    }

    response = requests.post(url, headers=headers)
    response.raise_for_status()  # Raise exception for non-2xx status codes

    print(f"{action}d: {org_name} / {project_name} ({project_id})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deactivate or activate Snyk projects based on a JSON file")
    parser.add_argument("input_file", help="The JSON file containing project information")
    parser.add_argument("--action", choices=["activate", "deactivate"], required=True,
                        help="The action to perform (activate or deactivate)")
    parser.add_argument("--token", default=os.environ.get("SNYK_TOKEN"),
                        help="Your Snyk API token (defaults to SNYK_TOKEN env var)")
    args = parser.parse_args()
    if not args.token:
        parser.error("--token is required, or set the SNYK_TOKEN env var")

    with open(args.input_file, "r") as f:
        data = json.load(f)

    for i, project in enumerate(data, 1):
        org_id = project["org_id"]
        project_id = project["project_id"]
        org_name = project.get("org_name", "")
        project_name = project.get("project_name", "")
        print(f"[{i}/{len(data)}] ", end="")
        deactivate_or_activate_project(org_id, project_id, args.action, args.token,
                                        org_name, project_name)

    print(f"\nAll {len(data)} project(s) successfully {args.action}d.")
