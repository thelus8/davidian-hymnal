# The Davidian Hymnal

All 51 Davidian songs as a web app you can install on your phone and use offline.

**Open it:** https://thelus8.github.io/davidian-hymnal/

- **iPhone:** open the link in Safari, tap Share, then **Add to Home Screen**.
- **Android:** open the link in Chrome, tap ⋮, then **Install app**.

Open it once while online. After that it works without internet.

## Updating the hymnal

The site at the top of this repository (`index.html`, `sw.js`, `manifest.webmanifest`) is generated. Don't edit those by hand; edit the files in `src/` and rebuild.

| File | What it is |
| --- | --- |
| `src/songs.json` | Every song: number, title, scripture, tune and verses. Edit this to fix a word or add a song. |
| `src/template.html` | The app's layout, colors and behavior. |
| `src/cover.jpg` | The banner image at the top of the home screen. |
| `src/sw.js`, `src/manifest.webmanifest` | Offline support and install settings. |
| `src/build.py` | Builds the site from the files above. |
| `src/parse.py` | Re-reads the songs from the original PDF. **This overwrites `songs.json`**, including any hand edits. |
| `src/make_icons.py` | Remakes the home-screen icons from the PDF cover. |

### Fix a typo or add a song

1. Edit `src/songs.json`. Each song looks like this:

   ```json
   {
    "n": 52,
    "title": "New Song Title",
    "caps": "NEW SONG TITLE",
    "ref": "Rev. 14:1",
    "tune": "Tune name",
    "sections": [
     { "label": "1", "lines": ["First line", "Second line"] },
     { "label": "Chorus", "lines": ["Chorus line"] },
     { "label": "2", "lines": ["..."] }
    ]
   }
   ```

   Keep songs in number order. `caps` is extra search text and can match the title.

2. Rebuild (needs only Python 3, which comes with macOS):

   ```bash
   python3 src/build.py
   ```

3. Commit and push. GitHub Pages republishes in about a minute, and installed copies update the next time they're opened online.

You can also do step 1 straight on github.com: open `src/songs.json`, click the pencil icon, and commit. Then rebuild on a computer before the change shows up in the app.
