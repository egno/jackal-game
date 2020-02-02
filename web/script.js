"use strict"

let serverdata = {}
let selectedItem = ''
let selectedPayload = ''
let api_url = '/api/'
let socket = ''

function connect() {
    if (!!(socket) && socket.readyState !== 3) {
        return socket
    }

    let ws = new WebSocket('wss://jackal.flas.ga/api/ws');
    ws.onopen = function () {
        console.log('Connected')
    };

    ws.onmessage = function (event) {
        let data = JSON.parse(event.data)
        if (data && data.field) {
            serverdata = data
            refresh()
        } else {
            console.log('Message from server ', event.data);
        }
    };

    ws.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e);
        socket = ''
        setTimeout(function () {
            socket = connect();
        }, 1000)
    };

    ws.onerror = function (err) {
        console.error('Socket encountered error: ', err.message, 'Closing socket')
        ws.close()
    };

    return ws
}


function getData() {
    socket = connect()
    fetch(api_url, {
        cache: 'no-cache',
    })
        .then(response => {
            const contentType = response.headers.get('content-type')
            if (!contentType || !contentType.includes('application/json')) {
                throw new TypeError("Oops, we haven't got JSON!")
            }
            return response.json()
        })
        .then(data => {
            serverdata = data
            refresh()
        })
}

function sendMoveData(itemId, coord, payloadIds) {
    let data = [{
        'item': itemId,
        'x': coord[1],
        'y': coord[0]
    }]
    if (payloadIds) {
        for (let p in payloadIds) {
            if (payloadIds[p] !== '') {
                data.push({
                    'item': payloadIds[p],
                    'x': coord[1],
                    'y': coord[0]
                })
            }
        }
    }
    socket = connect()
    socket.send(JSON.stringify(data))
}

function refresh() {
    let field = document.getElementById("field")
    if (!(field.getElementsByClassName('place').length)) {
        fillField(field)
    }
    refreshField(field)
    fillItems(field)
}

function fillField(field) {
    for (let y in serverdata.field) {
        let row = document.createElement("div")
        row.setAttribute("class", "row")
        field.appendChild(row)
        for (let x in serverdata.field[y]) {
            row.appendChild(newTile(y, x, serverdata.field[y][x]))
        }
    }
}

function fillItems(field) {
    for (let key in serverdata.items) {
        let item = serverdata.items[key]
        let placeID = generatePlaceID(item.y, item.x)
        let div = document.getElementById(generateItemID(key))
        if (!(div)) {
            div = document.createElement("div")
            div.setAttribute("class", `item ${item.type} hidden`)
            if (typeof item.gamer !== "undefined") {
                div.setAttribute("gamer", item.gamer)
                div.classList.add(`gamer_${item.gamer}`)
            }
            div.setAttribute("id", generateItemID(key))
            if (item.type) {
                let img = document.createElement("img")
                switch (item.type) {
                    case "Pirate":
                        img.setAttribute("src", `images/pirate${item.gamer}.png`)
                        break
                    case "Ship":
                        img.setAttribute("src", `images/ship${item.gamer}.png`)
                        div.classList.add('payload')
                        break
                    case "Coin":
                        img.setAttribute("src", `images/coin.png`)
                        div.classList.add('payload')
                        break
                    case "Chest":
                        img.setAttribute("src", `images/chest.png`)
                        div.classList.add('payload')
                        break
                }
                img.addEventListener('click', function (event) { clickItem(event) }, false)
                div.setAttribute("type", item.type)
                div.appendChild(img)
            }
            field.appendChild(div)
        }
        if (placeID) {
            let place = document.getElementById(placeID)
            placeItem(div, place)
        }
        if (item.step > -1) {
            div.setAttribute("step", item.step)
        } else {
            div.removeAttribute("step")
        }
    }
    repaintItems()
}

function selectPlace(e) {
    if (selectedItem) {
        placeItem(selectedItem, e.target.parentNode, true)
    }
}

function placeItem(item, place, send_data) {
    if (item.parentNode === place) {
        return
    }

    let payloads = []
    if (selectedPayload) {
        payloads.push(selectedPayload)
        if (selectedPayload.classList.contains('Ship')) {
            for (let payloadClass of ['Pirate', 'Coin', 'Chest']) {
                for (let p of Array.from(selectedItem.parentNode.getElementsByClassName(payloadClass))) {
                    if (p !== item) {
                        payloads.push(p)
                    }
                }
            }
        }
    }

    setTimeout(function () {
        let placeRect = place.getBoundingClientRect()
        moveItemStage1(item, placeRect)
        let itemRect = item.getBoundingClientRect()
        for (let p of payloads) {
            moveItemStage1(p, placeRect)
        }
    }, 100)

    setTimeout(function () {
        moveItemStage2(item, place)
        for (let p of payloads) {
            moveItemStage2(p, place)
        }
        if (send_data) {
            sendMoveData(item.id.split('_')[1], place.id.split(':'), payloads.map(x => x.id.split('_')[1]))
        }
        clearSelection()
    }, 500)
}

function moveItemStage1(item, placeRect) {
    let itemRect = item.getBoundingClientRect()
    item.classList.remove('hidden')
    item.style.bottom = `${itemRect.top - placeRect.top}px`
    item.style.right = `${itemRect.left - placeRect.left}px`
}

function moveItemStage2(item, place) {
    item.style.bottom = ''
    item.style.left = ''
    item.style.right = ''
    place.appendChild(item)
}

function clickItem(e) {
    let place = e.target.parentNode.parentNode
    if (selectedItem && selectedItem.parentNode !== place) {
        placeItem(selectedItem, place, true)
    } else {
        selectNextItemInPlace(place)
    }
}

function setItemSelected(item) {
    clearSelection()
    selectedItem = item
    selectedItem.classList.add('selected')
    let s = document.getElementById('selection')
    let pirateDiv = document.createElement("div")
    let img = document.createElement("img")
    img.setAttribute("src", selectedItem.firstChild.getAttribute("src"))
    pirateDiv.appendChild(img)
    s.appendChild(pirateDiv)
}

function setPayloadSelected(item) {
    clearPayloadSelection()
    selectedPayload = item
    selectedPayload.classList.add('selected')
    let s = document.getElementById('selection')
    let payloadDiv = document.createElement("div")
    let img = document.createElement("img")
    img.setAttribute("src", selectedPayload.firstChild.getAttribute("src"))
    payloadDiv.classList.add("payload")
    payloadDiv.appendChild(img)
    s.appendChild(payloadDiv)
}


function getItemGamer(item) {
    c = [...item.classList].filter(x => x.match(/gamer_*/))
    return c.length && c[0]
}

function loopItemsByAttribute(items, current, attributes) {
    if (!items.length) {
        return
    }
    let currentIndex = items.indexOf(current)
    if (currentIndex == -1) {
        return items[items.length - 1]
    }
    if (currentIndex < 1) {
        return
    }
    for (let i = currentIndex - 1; i >= 0; i--) {
        if (!(attributes
            .map(attribute => items[i].getAttribute(attribute) === current.getAttribute(attribute))
            .reduce((acc, cur) => { return acc && cur }, true)
        )) {
            return items[i]
        }
    }
}

function selectNextItemInPlace(place) {
    let pirates = Array.from(place.getElementsByClassName('Pirate'))
        .sort((a, b) => a.id > b.id ? 1 : -1)
    let payloads = Array.from(place.getElementsByClassName('payload'))
        .sort((a, b) => a.id > b.id ? 1 : -1)
    let pirate = loopItemsByAttribute(pirates, selectedItem, ["gamer", "step"])
    let payload = selectedPayload
    if (selectedItem && !pirate && payloads.length) {
        pirate = pirates[pirates.length - 1]
        payload = loopItemsByAttribute(payloads, selectedPayload, ["type"])
        if (selectedPayload && !payload) {
            payload = ''
            pirate = ''
        }
    }
    if (pirate) {
        setItemSelected(pirate)
        if (payload) {
            setPayloadSelected(payload)
        } else {
            selectedPayload = ''
        }
    } else {
        clearSelection()
    }
}

function clearSelection() {
    selectedItem = ''
    let items = Array.from(document.getElementById("field").getElementsByClassName('Pirate'))
    items.map(x => {
        x.classList.remove('selected')
    })
    let s = document.getElementById('selection')
    while (s.firstChild) {
        s.removeChild(s.firstChild);
    }
    repaintItems()
    clearPayloadSelection()
}

function clearPayloadSelection() {
    selectedPayload = ''
    let items = Array.from(document.getElementById("field").getElementsByClassName('payload'))
    items.map(x => {
        x.classList.remove('selected')
    })
}

function repaintItems(places) {
    if (!(places && places.length)) {
        places = Array.from(document.getElementById("field").getElementsByClassName("place"))
    }
    const wirlPlaces = [
        [0, 0],
        [0, 25],
        [0, 50],
        [50, 50],
        [50, 25]
    ]
    for (let place of places) {
        let pirates = Array.from(place.getElementsByClassName('Pirate'))
        if (pirates.length > 0) {
            if (place.getAttribute("type") && place.getAttribute("type").indexOf("TileWhirl") > -1) {
                for (let step = 0; step < 5; step++) {
                    let whirlStep = pirates.filter(x => x.getAttribute("step") == step)
                    for (let i in whirlStep) {
                        let p = whirlStep[i]
                        p.classList.add("whirl")
                        p.style.right = `${(wirlPlaces[step][0]) + (((whirlStep.length - i - 1) * 10) / whirlStep.length)}%`
                        p.style.bottom = `${(wirlPlaces[step][1]) + (((whirlStep.length - i - 1) * 2) / whirlStep.length)}%`
                    }
                }
            } else {
                for (let i in pirates) {
                    let p = pirates[i]
                    p.classList.remove("whirl")
                    if (pirates.length > 1) {
                        p.classList.add('multi')
                    } else {
                        p.classList.remove('multi')
                    }
                    p.style.right = `${((pirates.length - i - 1) * 40) / pirates.length}%`
                    p.style.bottom = `${((pirates.length - i - 1) * 15) / pirates.length}%`
                }
            }
        }
        let coins = Array.from(place.getElementsByClassName('Coin'))
        if (coins.length > 0) {
            coins.map((p, i) => {
                if (coins.length > 1) {
                    p.classList.add('multi')
                } else {
                    p.classList.remove('multi')
                }
                p.style.bottom = `${(i % 10) * 5}%`
                p.style.left = `${(i / 10 | 0) * 10}%`
            })
        }
    }
}


function generateItemID(key) {
    if (typeof (key) !== 'undefined') {
        return `item_${key}`
    }
    return
}

function generatePlaceID(row, col) {
    if (typeof (row) !== 'undefined' && typeof (col) !== 'undefined') {
        return `${row}:${col}`
    }
    return
}

function refreshField(field) {
    for (let y in serverdata.field) {
        for (let x in serverdata.field[y]) {
            let placeData = serverdata.field[y][x]
            let place = document.getElementById(generatePlaceID(y, x))
            let img = getImageName(placeData)
            if (img) {
                place.childNodes[0].setAttribute("src", img)
                if (placeData.orientation) {
                    place.classList.add(`rotate${placeData.orientation}`)
                }
            }
            if (placeData.tile && placeData.tile.type) {
                place.setAttribute("type", placeData.tile.type)
            } else {
                place.removeAttribute("type")
            }
        }
    }
}

function getImageName(data) {
    if (data.type !== 'EXCLUDED') {
        let img = document.createElement("img")
        switch (data.type) {
            case "SEA":
                return "images/sea.png"
                break
            case "GROUND":
                if (data.tile && data.tile.type) {
                    return `images/classic-${toKebabCase(data.tile.type)}.png`
                } else {
                    return "images/classic-cover.webp"
                }
                break
            default:
                return "images/classic-boat.png"
        }
    }

}

function newTile(row, col, data) {
    let div = document.createElement("div")
    div.setAttribute("class", "place")
    div.setAttribute("id", generatePlaceID(row, col))
    if (data.type !== 'EXCLUDED') {
        if (data.type === 'GROUND') {
            div.classList.add('tile')
        }
        let img = document.createElement("img")
        img.setAttribute("src", getImageName(data))
        img.addEventListener('click', function (event) { selectPlace(event) },
            false)
        div.appendChild(img)
    }
    return div
}

function init() {
    getData()
    setInterval(function () {
        getData()
    }, 60000);

    document.addEventListener("visibilitychange", function() {
        if (!document.hidden ) {
            getData()
        }
      });
}

function toKebabCase(s) {
    return s && s.match(/[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+/g)
        .map(x => x.toLowerCase())
        .join('-')
}

init()


