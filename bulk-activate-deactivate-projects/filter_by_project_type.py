import json
import argparse

# Snyk product -> REST API project "attributes.type" values.
# Source: https://docs.snyk.io/developer-tools/snyk-api/api-endpoints-index-and-tips/project-type-responses-from-the-api
PROJECT_TYPE_GROUPS = {
    "iac": ["k8sconfig", "helmconfig", "terraformconfig", "cloudformationconfig",
            "armconfig", "cloudconfig", "iac"],
    "container": ["dockerfile", "linux", "apk", "deb", "rpm"],
    "code": ["sast"],
    "opensource": ["npm", "pnpm", "yarn", "yarn-workspace", "maven", "gradle", "sbt",
                    "pip", "poetry", "pipenv", "rubygems", "golang", "gomodules",
                    "golangdep", "govendor", "nuget", "paket", "composer",
                    "cocoapods", "swift", "hex", "cpp", "unmanaged"],
}


def load_project_data(path):
    with open(path) as f:
        return json.load(f)


def filter_projects(project_data, types):
    type_set = {t.lower() for t in types}
    return [p for p in project_data if p.get("project_type", "").lower() in type_set]


def print_summary(matched, types):
    print(f"Matching types: {', '.join(types)}")
    print(f"{len(matched)} project(s) matched\n")
    by_org = {}
    for p in matched:
        by_org.setdefault(p["org_name"], 0)
        by_org[p["org_name"]] += 1
    for org, count in sorted(by_org.items()):
        print(f"  {org:40s} {count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filter project_data.json (from get_projects.py) down to one "
                    "product's project types, for offboarding a Snyk product.")
    parser.add_argument("input_file", help="project_data.json from get_projects.py")
    parser.add_argument("--project-type", choices=sorted(PROJECT_TYPE_GROUPS),
                        help="Built-in project type group to filter for")
    parser.add_argument("--types",
                        help="Comma-separated project_type values instead of "
                             "--project-type, e.g. terraformconfig,k8sconfig")
    parser.add_argument("--out", default="projects_to_offboard.json",
                        help="Output file (default: projects_to_offboard.json)")
    args = parser.parse_args()

    if not args.project_type and not args.types:
        parser.error("pass --project-type or --types")
    if args.project_type and args.types:
        parser.error("pass only one of --project-type or --types")

    types = PROJECT_TYPE_GROUPS[args.project_type] if args.project_type else \
        [t.strip() for t in args.types.split(",") if t.strip()]

    project_data = load_project_data(args.input_file)
    matched = filter_projects(project_data, types)
    print_summary(matched, types)

    with open(args.out, "w") as f:
        json.dump(matched, f, indent=4)
    print(f"\n{len(matched)} project(s) written to {args.out}")
