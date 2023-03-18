const clearLogsBtn = document.getElementById('clear-logs')

// sendRequest(method, header, body, uri, jsonBody = null, async = false)
clearLogsBtn.addEventListener('click', () => {
    sendRequest('DELETE', 'logs', {}, '/api')
    window.location.reload()
})
