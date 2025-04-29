#!/usr/bin/env bash

# Install ffmpeg manually
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar xJ
mv ffmpeg-*-amd64-static/ffmpeg ./ffmpeg
chmod +x ./ffmpeg
