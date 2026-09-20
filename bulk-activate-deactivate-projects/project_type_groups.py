# Snyk product -> REST API project "attributes.type" values.
# Source: https://docs.snyk.io/developer-tools/snyk-api/api-endpoints-index-and-tips/project-type-responses-from-the-api
# plus "secrets", confirmed against real fetched data -- not in that
# reference doc, which is known to be stale. Secrets scanning is its
# own Snyk product, separate from Code/SAST.
PROJECT_TYPE_GROUPS = {
    "iac": ["k8sconfig", "helmconfig", "terraformconfig", "terraformplan",
            "cloudformationconfig", "armconfig"],
    "container": ["dockerfile", "linux", "apk", "deb", "rpm"],
    "code": ["sast"],
    "secrets": ["secrets"],
    "opensource": ["npm", "pnpm", "yarn", "yarn-workspace", "maven", "gradle", "sbt",
                    "pip", "poetry", "pipenv", "rubygems", "golang", "gomodules",
                    "golangdep", "govendor", "nuget", "paket", "composer",
                    "cocoapods", "swift", "hex", "cpp", "unmanaged"],
}
