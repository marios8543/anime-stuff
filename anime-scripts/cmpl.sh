#!/usr/bin/env bash

name="$1";
category="$2";
content_path="$3";
root_path="$4";
save_path="$5";
file_number="$6";
size="$7";
current_tracker="$8";
hash="$9";

export JF_DIR=/Anime/Jellyfin-Anime
export MI_URL=http://anime-namer:9010/addPending
cd /scripts

if [[ "$category" == "Anime" ]]; then
	echo "Running jellyfin namer";
	if [[ -d "$root_path" ]]; then
		res=$(bash jellyfin-namer-new.sh "$root_path");
	else
		res=$(bash jellyfin-namer-new.sh "$save_path");
	fi
	bash subtitle-converter.sh "$res";
fi
