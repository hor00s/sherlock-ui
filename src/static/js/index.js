function moveJson(from, to) {
    for (const key in from) {
        to[key] = from[key]
    }
}





function checkError(response) {
    const errorMsg = response.error
    if (errorMsg) {
        const msg = errorMsg
        alert(msg)
    }
}


const username = document.getElementById('username-input')
const verboseCb = document.getElementById('verbose-cb')
const nsfwCb = document.getElementById('nsfw-cb')
const xlsxCb = document.getElementById('xlsx-cb')
const csvCb = document.getElementById('csv-cb')
const timeoutSetter = document.getElementById('timeout-step')
const stdOutCb = document.getElementById('get-stdout')
const localCb = document.getElementById('local-cb')


const submitBtn = document.getElementById('submit-btn')
const deleteUserBtn = document.querySelectorAll('.delete-user')
const deleteCommandBtn = document.querySelectorAll('.delete-command')

submitBtn.addEventListener('click', () => {
    let command = {}
    const args = [
        [verboseCb, "--verbose"],
        [nsfwCb, "--nsfw"],
        [xlsxCb, "--xlsx"],
        [csvCb, "--csv"],
        [localCb, "--local"],
        [stdOutCb, "get_stdout"],
    ]

    const timeout = timeoutSetter.value
    const getUsername = username.value

    command.timeout = timeout

    for (let i=0; i<args.length; i++) {
        const checkbox = args[i][0]
        if (checkbox.checked) {
            command[args[i][1]] = true
        } else if (!checkbox.checked) {
            command[args[i][1]] = false
        }
    }

    command.username = getUsername

    let dataReply = {}
    sendRequest('POST', 'run', command, '/api', dataReply)
    checkError(dataReply)
    window.location.reload()
})




deleteUserBtn.forEach((item, _) => {
    console.log(item.name === item.id)
    item.addEventListener('click', () => {
        
        sendRequest('DELETE', 'user', {'file': item.name}, '/api')
        window.location.reload()
    })
})


deleteCommandBtn.forEach((item, index) => {
    item.addEventListener('click', () => {
        console.log(index)
        sendRequest('DELETE', 'command', {'content': index}, '/api')
        window.location.reload()
    })
})
