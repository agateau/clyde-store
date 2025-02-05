const VAULT_BASE_URL = "https://releases.hashicorp.com/vault"

const VAULT_RELEASE_URL_PATTERN = "/vault/([0-9]+\.[0-9]+\.[0-9]+)/"

function main() {
  // Fetch global release page
  const response = httpGet(VAULT_BASE_URL)
  if (response.status != 200) {
    console.log("Failed to fetch release page: status=" + response.status + "\n" + response.text)
    return null
  }
  const match = RegExp(VAULT_RELEASE_URL_PATTERN).exec(response.text)
  if (!match) {
    console.log("Failed to find a release URL in release page")
    return null
  }
  let version = match[1]
  console.log("version=" + version)

  // Fetch version release page
  const response2 = httpGet(VAULT_BASE_URL + "/" + version)
  if (response2.status != 200) {
    console.log("Failed to fetch version release page")
    return null
  }
  var text = response2.text

  const artifactRx = RegExp(
    VAULT_BASE_URL + "/" + version + "/vault_" + version + "_(linux|windows|darwin)_(arm64|amd64)\.zip",
    "g"
  )

  var urls = []
  while (true) {
    const match = artifactRx.exec(text)
    if (match == null) {
      break
    }
    urls.push(match[0])
  }

  return {
    "version": version,
    "urls": urls
  }
}

main()
