const urls = document.querySelectorAll("#delete-site")
const addSiteBtn = document.getElementById('add')
const siteInput = document.getElementById('add-site')


function getUserName() {
    let parsedUrl = window.location.href.split('/')
    let userName = parsedUrl[parsedUrl.length-1]
    return userName
}

const user = getUserName()

urls.forEach((btn, index) => {
    btn.addEventListener('click', () => {
        sendRequest('DELETE', 'site', {site: btn.name, user: user}, '/api')
        window.location.reload()
    })
})

addSiteBtn.addEventListener('click', () => {
    sendRequest('PUT', 'site', {site: siteInput.value, user: user}, '/api')
    window.location.reload()
})

// sendRequest(method, header, body, uri, jsonBody = null, async = false)
