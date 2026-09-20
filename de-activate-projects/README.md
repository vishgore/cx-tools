# Bulk Activate / Deactivate Snyk Projects

De / activates projects across multiple Snyk Organisations in a Group.

Also used for **capability offboarding**: a customer drops a Snyk product (e.g. IaC)
from their renewal, and you need to deactivate every project of that type across
their Group. See [Capability offboarding](#capability-offboarding) below.

## Features

`get_projects.py` - gathers project information for entire Snyk Orgnisation. Uses [Snyk's REST API](https://apidocs.snyk.io/).

`filter_by_capability.py` - filters `project_data.json` down to one product's project
types (built-in: `iac`, `container`, `code`, `opensource`, or a custom `--types` list).

`change_proj_status.py` - De / activates selected projects. Uses [Snyk's V1 API](https://snyk.docs.apiary.io/).

## Configuration

Install dependencies
```sh
pip install -r requirements.txt
```

Update variables in `get_projects.py`. Get the latest API Version from [Snyk's REST API](https://apidocs.snyk.io/)
```py
API_VERSION = "2024-08-15"
RATE_LIMIT_DELAY = 0.2 (in seconds)
```

## Usage

### Gather project information 

Run the script locally

```sh
python3 get_projects.py --group YOUR_GROUP_ID --token your_api_token
```

Script will output `project_data.json` file. Edit the file as necessary. Example below

```json
[
    {
        "org_name": "Test_Org",
        "org_id": "**************",
        "project_name": "nodejs-goof/nodejs-goof(main)",
        "project_id": "**************",
        "type": "sast",
        "target_file": "",
        "status": "active"
    }
]
```

### Activate / Deactivate Projects

```sh
python3 change_proj_status.py project_data.json --action activate/deactivate --token your_api_token
```

## Capability offboarding

To deactivate every project of one Snyk product (e.g. a customer drops IaC in their
renewal) across a Group, run the three scripts as a pipeline:

```sh
# 1. Gather every org + project in the Group
python3 get_projects.py --group YOUR_GROUP_ID --token your_api_token

# 2. Narrow to the capability being dropped (prints a per-org count so you can
#    sanity-check before deactivating anything)
python3 filter_by_capability.py project_data.json --capability iac

# 3. Deactivate exactly those projects
python3 change_proj_status.py projects_to_offboard.json --action deactivate --token your_api_token
```

`--capability` supports `iac`, `container`, `code`, `opensource`. For anything else,
pass `--types` with a comma-separated list of `attributes.type` values instead, e.g.
`--types terraformconfig,k8sconfig`.

To undo, re-run step 3 with `--action activate` on the same `projects_to_offboard.json`.
