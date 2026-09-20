# Bulk Activate / Deactivate Snyk Projects

De / activates projects across multiple Snyk Organisations in a Group.

Also used for **capability offboarding**: a customer drops a Snyk product (e.g. IaC)
from their renewal, and you need to deactivate every project of that type across
their Group. See [Capability offboarding](#capability-offboarding) below.

## Features

`get_projects.py` - gathers project information for entire Snyk Orgnisation. Uses [Snyk's REST API](https://apidocs.snyk.io/).
Accepts an optional `--project-type` / `--types` filter, applied server-side via the
projects endpoint's own `types=` query parameter -- pass it whenever you already know
what you're after, so orgs with thousands of projects aren't fetched in full just to
throw most of them away. Built-in `--project-type` groups: `iac`, `container`, `code`,
`secrets`, `opensource` (see `project_type_groups.py`), or pass `--types` with a
comma-separated list of the API's own `attributes.type` values instead, e.g.
`--types terraformconfig,k8sconfig`. Writes to `project_data.json` by default, or
`project_data_<project-type>.json` when `--project-type` is given (so fetching two
different types in a row doesn't overwrite each other) -- override with `--out`.

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

Both scripts take `--token`, or default to the `SNYK_TOKEN` env var if `--token` is
omitted:

```sh
export SNYK_TOKEN=your_api_token
```

### Gather project information 

Run the script locally

```sh
python3 get_projects.py --group YOUR_GROUP_ID
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
python3 change_proj_status.py project_data.json --action activate/deactivate
```

## Capability offboarding

To deactivate every project of one Snyk product (e.g. a customer drops IaC in their
renewal) across a Group:

```sh
export SNYK_TOKEN=your_api_token

# 1. Gather only the relevant projects -- filtered server-side, so orgs with
#    thousands of projects aren't fetched in full. Prints a per-org count so
#    you can sanity-check before deactivating anything. Writes to
#    project_data_iac.json here specifically.
python3 get_projects.py --group YOUR_GROUP_ID --project-type iac

# 2. Deactivate exactly those projects
python3 change_proj_status.py project_data_iac.json --action deactivate
```

To undo, re-run step 2 with `--action activate` on the same output file.
