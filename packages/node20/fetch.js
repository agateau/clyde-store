const BASE_URL = "https://nodejs.org/dist"

const MAJOR_VERSION = 20

/**
 * Array of:
 * - element in "files" item inside index.json
 * - file suffix in the release dir
 */
const WANTED_FILES = [
  ["linux-arm64", "linux-arm64.tar.xz"],
  ["linux-x64", "linux-x64.tar.xz"],
  ["osx-arm64-tar", "darwin-arm64.tar.xz"],
  ["osx-x64-tar", "darwin-x64.tar.xz"],
  ["win-x64-zip", "win-x64.zip"],
]

/**
 * Find the first entry in index.json which starts with "v${MAJOR_VERSION}.".
 * Assumes it's the latest release of this major version.
 */
function findEntry(lst) {
  const prefix = "v" + MAJOR_VERSION + "."
  return lst.find(element => element.version.startsWith(prefix))
}

function main() {
  console.log("Fetching index.json")
  const response = httpGet(BASE_URL + "/index.json")
  console.log("Response: " + response.status)

  console.log("Parsing response")
  const lst = JSON.parse(response.text)

  console.log("Extracting info")
  const entry = findEntry(lst)
  if (entry === null) {
    console.log("Found no entry for version " + MAJOR_VERSION)
    return null
  }

  var urls = new Array()
  WANTED_FILES.forEach(element => {
    const file = element[0]
    const suffix = element[1]
    if (entry.files.find(x => x == file) === undefined) {
      console.log("Skipping " + file)
      return
    }
    console.log("Found entry for " + file)
    urls.push(BASE_URL + "/" + entry.version + "/node-" + entry.version + "-" + suffix)
  })
  return {
    "version": entry.version.substring(1),
    "urls": urls
  }
}

main()
