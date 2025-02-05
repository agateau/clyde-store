const RELEASE_RSS_URL = "https://git.sr.ht/~gpanders/ijq/refs/rss.xml"

const RELEASE_URL_PATTERN = "https://git\.sr\.ht/~gpanders/ijq/refs/v([0-9]+\.[0-9]+\.[0-9]+)"

const ARTIFACT_URL_PATTERN_TEMPLATE = "/~gpanders/ijq/refs/download/v@VERSION@/ijq-@VERSION@-(linux|darwin)-(arm64|amd64).tar.gz"

function main() {
  // Fetch global release page
  const response = httpGet(RELEASE_RSS_URL)
  if (response.status != 200) {
    console.log("Failed to fetch release page: status=" + response.status + "\n" + response.text)
    return null
  }
  const match = RegExp(RELEASE_URL_PATTERN).exec(response.text)
  if (!match) {
    console.log("Failed to find a release URL in release page")
    return null
  }
  const releaseURL = match[0]
  const version = match[1]
  console.log("version=" + version)

  // Fetch version release page
  const response2 = httpGet(releaseURL)
  if (response2.status != 200) {
    console.log("Failed to fetch version release page")
    return null
  }
  var text = response2.text

  const artifactPattern = ARTIFACT_URL_PATTERN_TEMPLATE.replaceAll("@VERSION@", version)
  const artifactRx = RegExp(artifactPattern, "g")

  var urls = []
  while (true) {
    const match = artifactRx.exec(text)
    if (match == null) {
      break
    }
    urls.push("https://git.sr.ht" + match[0])
  }

  return {
    "version": version,
    "urls": urls
  }
}

main()
