#!/usr/bin/env bash

# Download and unpack ffmpeg static binary
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar xJ
mv ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
chmod +x ./ffmpeg
