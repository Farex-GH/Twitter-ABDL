# Twitter ABDL (Automatic Bulk DownLoader)

Downloads liked images and videos or media from a user's page.

## Example usage

For downloading a user's liked images and videos
```
python downloader.py --username "your-username" --password "your-password" --page "https://twitter.com/someone/likes" --download_path "./output" 
```

For downloading a user's images and videos they've uploaded
```
python downloader.py --username "your-username" --password "your-password" --page "https://twitter.com/someone/media" --download_path "./output" 
```

For downloading a user's images and videos they've replied with
```
python downloader.py --username "your-username" --password "your-password" --page "https://twitter.com/someone/with_replies" --download_path "./output" 
```

Note that it is currently not possible to download images from someone's timeline.

## Installation

1. Install Python and Pip from https://www.python.org/downloads/

2. Install selenium https://selenium-python.readthedocs.io/installation.html (steps 1-1.4 depending on how you want to install)

3. Download the Firefox driver https://github.com/mozilla/geckodriver/releases. On my machine I put the binary in the same directory the Python script lives.

## Running

Running `python downloader.py -h` will give you a list of options, with some descriptions on how to use them.

You can use the example usage above, or specify `--finish_on_name "base-64-image-name.jpg"` or `--finish_on_url 'https://pbs.twimg.com/media/base64-name?format=jpg&name=large'` to stop downloading images when a specific link or image is found. Otherwise the script will run until it reaches the bottom of the page and infinite scrolling stops working.

## Known Issues

This is the first thing I've written in Python and it was made in less than a day, expect problems. I made this for myself so I could easily save images from my 2nd favorite furry website, so there are no tests and minimal thought.

Some things that you may run into:

1. Fails to log in. Not sure what causes this, maybe it's the script going too fast or Twitter being uncooperative. Just retry.

2. It's slow. This is so it doesn't miss images. I've found that with scrolling more or with less delay it can cause images to be skipped.

3. It may exit prematurely. I haven't actually ran into this, but it could happen in theory if Twitter takes several seconds to present new images. This is because the script thinks that there's nothing left to load.

## TODO

1. It is currently not possible from someone else's timeline.

It's probably easy, however Twitter does not sometimes make you log in right away. Because of this, the `username` prompt that the downloader looks for never shows up and it cannot proceed.

We need to either never log in, or scroll, eventually twitter tells us to log in, log in, then continue scrolling.
