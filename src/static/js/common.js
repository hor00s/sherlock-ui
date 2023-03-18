function sendRequest(method, header, body, uri, jsonBody = null, async = false) {
    /**
     * Send a xml request to the server. If a `jsonBody` is provided, this function
     * will move the server response to it in order to be used exterally
     * @param {string} csrf [The csrf token]
     * @param {string} header [The header (name) of the request]
     * @param {object} body [The rest of the data the request needs]
     */

    let request = new XMLHttpRequest();
    request.open(method, uri, async);
    request.setRequestHeader("Content-Type", "application/json");

    request.onload = function () {
        let dataReply = JSON.parse(this.responseText)
        if (jsonBody != null) {
            moveJson(dataReply, jsonBody)
        }
    }

    request.send(JSON.stringify(
        { header: header, body }
    ));
}