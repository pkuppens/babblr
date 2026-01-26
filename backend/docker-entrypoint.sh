#!/bin/sh

set -e

ensure_dir() {
  if [ ! -d "$1" ]; then
    mkdir -p "$1"
  fi
}

if [ "$(id -u)" = "0" ]; then
  ensure_dir /data
  ensure_dir /home/babblr/.cache/whisper

  chown -R babblr:babblr /data /home/babblr/.cache/whisper
  exec su -s /bin/sh babblr -c "$*"
fi

exec "$@"
