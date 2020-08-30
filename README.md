# Gooify

Gooify is a simple program that finds all of the music in your Google Play Music library and adds it to your Spotify library
- It can import your playlists
- Albums
- Followed Artists

It can use the google music api or a google music takeout file.

This version modified from the [original](https://github.com/gzinck/Gooify). 

## Guide

- pip install -r requirements.txt
- cp .env.dist .env
- Add your [spotify client info](https://developer.spotify.com/) to .env and set your usernames
- python main.py
- Boom!
- Otherwise check out the code, there is a bit of a mess, but should easy to modify and do what you want with.
