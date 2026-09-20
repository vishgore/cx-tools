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
