async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function getLyrics() {
    let lyrics = await fetch('/lyrics');
    lyrics = await lyrics.json();
    return lyrics;
}

function setLyricsInDom(lyrics) {
    if (!Array.isArray(lyrics)) lyrics = ['', lyrics.msg, ''];

    document.getElementById('previous-lyric').innerHTML = lyrics[0];
    document.getElementById('current-lyric').innerHTML = lyrics[1];
    document.getElementById('next-lyric').innerHTML = lyrics[2];
}


async function main() {
    while(true) {
        let lyrics = await getLyrics();
        setLyricsInDom(lyrics);
        await sleep(100);
    }
}


document.addEventListener('DOMContentLoaded', main);
