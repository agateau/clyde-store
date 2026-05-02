// This page contains a CSV with release details, embedded in an HTML comment
const DOWNLOAD_URL = "https://www.sqlite.org/download.html"

const PRODUCT_PATTERN = "^PRODUCT,([0-9]+\.[0-9]+\.[0-9]+),(.+/sqlite-tools-[^,]+)"

function main() {
  const response = httpGet(DOWNLOAD_URL)
  if (response.status != 200) {
    console.log("Failed to fetch release page: status=" + response.status + "\n" + response.text)
    return null
  }

  const artifactRx = RegExp(PRODUCT_PATTERN)

  var urls = []
  var version = ""
  response.text.split("\n").forEach((line) => {
    const match = artifactRx.exec(line)
    if (match == null) {
      return
    }
    version = match[1]
    urls.push("https://sqlite.org/" + match[2])
  })


  return {
    "version": version,
    "urls": urls
  }
}

main()
