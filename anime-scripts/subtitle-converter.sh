#!/usr/bin/env bash

function convert() {
	res=$(ffprobe -v error -show_entries stream=codec_type,codec_name -of compact "$1" | grep -s "subtitle");
	if [[ "$res" == *"ass"* ]]; then
		echo "Converting $1";
		ffmpeg -n -i "$1" -c:s srt "${i%.$ext}.srt" > /dev/null
	else
		echo "$1 not ASS. Skipping";
	fi
}

if [[ -d "$1" ]]; then
	cd "$1";
	shopt -s globstar
	for i in **/*; do
		ext="${i##*.}";
		convert "$i";
	done
elif [[ -f "$1" ]]; then
	cd $(dirname "$1");
	name=$(basename "$1");
	ext="${name##*.}";
	convert "$name";
fi
