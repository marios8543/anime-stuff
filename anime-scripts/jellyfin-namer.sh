#!/usr/bin/env bash

#Create flagsa and library dirs if not exist 
if [[! -d "/Anime/_flags"]]; then
	mkdir /Anime/flags;
fi
if [[! -d "/Anime/AnimeLibrary"]]; then
	mkdir /Anime/AnimeLibrary;
fi

#Gets the last part of the current directory
function get_bottom_dir() {
        IFS='/';
        read -ra ADDR <<< "$PWD";
        echo "${ADDR[-1]}";
        IFS=' ';
}

#Removes braces, parenteres along with everything in them and strips leading and trailing whitespace
function name_clean() {
        local _out=$(echo "$1" | sed -e 's/\[[^][]*\]//g');
        _out=$(echo "$_out" | sed -e 's/([^()]*)//g');
        _out=$(echo "$_out" | sed 's/_/ /g');
        echo $(echo "$_out" | xargs);
}

#Get series via seasons.py. Will fall-back to manual intervention if fail.
function get_series() {
	local sanitized_name=$(name_clean "$1");
	local output;
	output=$(python3 /scripts/seasons.py "$sanitized_name"; exit "$?";);
	if [[ "$?" -ne "0" ]]; then
		echo "seasons.py failed. Waiting for manual intevention.";
		local mi_id;
		mi_id=$(curl --fail -F "dl_path=$sanitized_name" "$MI_URL"; exit "$?";);
		if [[ "$?" -eq "0" ]]; then
			while [[ ! -f "/Anime/flags/$mi_id" ]]; do
				sleep 1;
			done
			output=$(cat "/Anime/flags/$mi_id");
			rm "/Anime/flags/$mi_id";
			if [[ "$output" -eq "delete" ]]; then
				return 1;
			fi
		else
			return 1;
		fi
	fi

	IFS="|";
	read -ra STR <<< "$output"

	TITLE_ROMAJI="${STR[0]}";
	TITLE_ENGLISH="${STR[1]}";
	SEASON="${STR[2]}";
	IFS=" ";
	return 0;
}
cd "$1";

bottom_dir=$(get_bottom_dir);
cleaned_bottom_dir=$(name_clean "$bottom_dir");
get_series "$cleaned_bottom_dir";
if [[ "$?" -eq "0" ]]; then
	if [[ -d "$JF_DIR/$TITLE_ROMAJI" ]]; then
		cleaned_dir="$TITLE_ROMAJI/Season $SEASON";
	elif [[ -d "$JF_DIR/$TITLE_ENGLISH" ]]; then
		cleaned_dir="$TITLE_ENGLISH/Season $SEASON";
	else
		cleaned_dir="$TITLE_ROMAJI/Season $SEASON";
	fi
else
	cleaned_dir="$cleaned_bottom_dir";
fi
mkdir -p "$JF_DIR/$cleaned_dir";

for i in *; do
        cleaned_name=$(name_clean "$i");
        ln "$PWD/$i" "$JF_DIR/$cleaned_dir/$cleaned_name" >/dev/null 2>/dev/null;
done;

echo "$JF_DIR/$cleaned_dir";