/**
 * This function is used to sleep for a given amount of time.
 * @param {Number} ms The amount of time to sleep in milliseconds. 
 * @returns {Promise} A promise that resolves after the given amount of time. 
 */
async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


/**
 * This function is used to get the lyrics from the server.
 * @returns {Promise<Array<String> | {msg: String}>} The lyrics from the server.
 */
async function getLyrics() {
    let lyrics = await fetch('/lyrics');
    lyrics = await lyrics.json();
    return lyrics;
}

/**
 * This function is used to set the lyrics in the DOM.
 * @param {Array<String> | {msg: String}} lyrics The lyrics to set in the DOM.
 */
function setLyricsInDom(lyrics) {
    if (!Array.isArray(lyrics)) lyrics = ['', lyrics.msg, ''];

    document.getElementById('previous-lyric').innerHTML = lyrics[0];
    document.getElementById('current-lyric').innerHTML = lyrics[1];
    document.getElementById('next-lyric').innerHTML = lyrics[2];
}


/**
 * This function is used to get the lyrics from the server and set them in the DOM.
 * It will repeat this process forever.
 */
async function main() {
    while(true) {
        let lyrics = await getLyrics();
        setLyricsInDom(lyrics);
        await sleep(100);
    }
}


document.addEventListener('DOMContentLoaded', main);
