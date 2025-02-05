/*
 * Helm releases are announced on GitHub, but the GitHub release contains only .asc files.
 * Link to release artifacts are in the release message, so we scrap them from there.
 */
RELEASE_URL = "https://api.github.com/repos/helm/helm/releases/latest"

function main() {
  console.log("Fetch release info")
  const response = httpGet(RELEASE_URL)
  if (response.status != 200) {
    console.log("Failed to fetch release info: " + response.text)
    return
  }
  const dct = JSON.parse(response.text)
  const tag = dct["tag_name"]
  const body = dct["body"]

  console.log("Scraping release info")
  const version = tag.substring(1)
  const artifactRx = RegExp(
    "https://get\\.helm\\.sh/helm-" + tag + "-(darwin|linux|windows)-(arm64|amd64)\\.(tar\\.gz|zip)",
    "g"
  )

  var urls = new Set()
  while (true) {
    const match = artifactRx.exec(response.text)
    if (match == null) {
      break
    }
    urls.add(match[0])
  }

  return {
    "version": version,
    "urls": [...urls]
  }
}

main()
