# tzatzikiweeb's Anime Stack

### Where autism meets subpar coding skills

## Prologue

Anime is undoubtedly a patrician hobby that is only enjoyed by those at the top of the consoomer pyramid.
Those that have freed themselves from the shackles of mindless capeshit movies and mediocre to downright
disgusting TV comedies. And standing on top, the upper echelon of Weeeabo Inc., the Rothschild of the otaku
society, is torrenters. Why, you may ask? Well, truth is, sure you could pay for crunchyroll, but then you'd
have to deal with their horrible outdated player (and even more atrocious app), their blatant lack of good shows,
especially older ones and with your own concience for funding [this](https://twitter.com/GuardianSpice). Or you
could use sites like kissanime, but then you'd have to constantly put up with all the horny milfs in your area,
and as a weeb you just can't have that. So torrenting it is. But how do you go about managing your vast library
of east asian moving drawings, automating as much as possible and making your life easier ?

## Goals and requirements

I downloaded all of my anime from Animebytes. It's a private torrent tracker so I won't focus too much on it. Anything could replace it.
For watching, sorting and organising my library I use Jellyfin, while watching is done mostly on a 3rd Generation Google Cast.
Now Jellyfin is rather anal about how these shows are named, so if you want to have metadata fetched properly and your library to look nice,
you should probably be mindful to have the folders named as cleanly as possible. This means no random information (like sub group, resolution, etc)
in the folder name. The chromecast now has its fair share of quirks as well. It can't play HEVC, it can't play 10-bit content but most importantly it
can't render SSA/ASS subtitles which is what almost all anime uses. ASS subs pack visual effects (like karaoke stuff for the OP) besides just subtitles, so Jellyfin will not attempt to convert it to a more primitive format like SRT. Instead it will fire up ffmpeg and burn the subtitles into
the video, sending the quality into the ground and violating my electricity bill. What ? You have a NAS with a crappy ARM processor instead of a meme
server with double xeons ? Tough luck pal. But fear not. While converting to SRT will indeed not preserve all the information, it will certainly keep the important bits. So if Jellyfin will not do it, then we will. But first things first...

## Animebyter

It's a daemon and web app that keeps track of the shows I watch and automatically downloads new episode off Animebytes. It takes advantage of the RSS
feeds provided by the tracker. I won't focus too much on the inner workings of this because it's not really important but if you want to modify it to
work with another RSS source take a look at Animebyter.py inside the animebyter folder. Modify the `get_airing` function as you wish. It should return a list of `Anime` objects. Oh and don't forget to use aiohttp for the requests or else it can mess something else up.

## seasons.py

Now we get to the interesting stuff. You may have noticed this little script called `seasons.py` inside the anime-scripts folder. Well I can't deny that it looks a bit out of place in there. So what is it ? Why it's a script that figures out the title and season from an anime name. Its principle of operation is roughly as follows:

- Search for the name provided on anilist.
- If the search returns an ID, fetch the series.
- Recursively fetch all of the prequels (the prequels of the prequels of the prequels...etc).
- Sort them by release date
- Narrow down these results to shows that are of type TV. This is done to counter edge cases like Kaminomi where there the first item in the above list is a prequel OVA. In the eyes of the script that would be our season 1 but this is obviously not the case.
- If our show doesn't exist in there (ex in the case of an OVA-only series like Hellsing Ultimate), expand the search to all types.
- Finally find the index of our show in the list of prequels. Add 1 and there's your season!

You can test this component out [here](https://tzatzikiweeb.moe/season-finder)
Now obviously this isn't foolproof and sometimes I have to manually define the title and season of shows. Keep reading to find that out...

## jellyfin-namer.sh

This script implements `seasons.py` and creates the appropriately named folders, which jellyfin can then scan and identify. It also symlinks the actual videos from the downloadeds folder into the new ones essentially decoupling my downloads from the library, allowing me to manipulate the structure as I see fit, while keeping the originals intact and seedable (I have to maintain a ratio on my cool kids only tracker). Again the steps this script follows are more or less the following:

- Do some initial sanization on the name: Remove braces and parentheses and everything inbetween and strip leading and trailing whitespace.
- Run `seasons.py` with the sanitized name. If successful this will yield a `|`-separated string containing the determined series name in romaji and english as well as the season number. If not successful it will get the user to provide said data. Keep reading to find out how this is done...
- Check if either romaji or english named folders exist already. If not, pick romaji. Create a folder like `"$TITLE_ROMAJI/Season $SEASON"` in the library directory.
- Sanitize and symlink all of the videos inside the original folder to the new folder created above.
  
## anime-namer

Above, I've mentioned that the user will manually provide the title and season of shows that cannot be determined automatically by `seasons.py`. This is done by this little utility. It's a web-app written in Python. Let's see how it works:

- When `jellyfin-namer.sh` gets a non-zero exit code from `seasons.py` it will initiate manual intervention. This is done with an `/addPending` request to the anime-namer server. cURL is used. Said request will return an id which will be stored in a variable on jellyfin-namer while a notification will be sent through gotify.
- `jellyfin-namer.sh` will then start listening to the flags directory (which is shared between itself and namer) for a file with the same name as the id fetched above.
- When the user goes to the anime-namer page he will be asked to provide the title and season. Then a file with the same name as the above id will be created containing the same `|`-separated string that `seasons.py` would normally return. From that point on the script continues normally with the output of that flag file instead. If the user opts to click delete instead, a flag file is also created containing the word `delete`. This is detected by `jellyfin-namer.sh` and the sanitized name is used for the folder name.

## subtitle-converter.sh

Not much to say here. This script will extract the ASS subtitles from videos, convert to SRT and save with the same name as the videos so they're picked up by Jellyfin.
