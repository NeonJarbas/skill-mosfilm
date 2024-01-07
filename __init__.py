import random
from os.path import join, dirname

import requests
from json_database import JsonStorageXDG

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class MosFilmSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.MOVIE]
        self.skill_icon = self.default_bg = join(dirname(__file__), "ui", "mosfilm_icon.jpg")
        self.archive = JsonStorageXDG("MosFilm", subfolder="OCP")
        super().__init__(*args, **kwargs)

    def initialize(self):
        self._sync_db()
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        title = []
        directors = []
        genre = ["russian"]

        for url, data in self.archive.items():
            t = data["title"].split("|")[0].split("(")[0].strip().split(",")[0].split("-")[0].lstrip("'").rstrip("'")
            if '"' in t:
                t = t.split('"')[1]
            if " by " in data["title"]:
                director = data["title"].split(" by ")[1]
                directors.append(director.strip())
                for w in director.split(" "):
                    directors.append(w)
            title.append(t.strip())

        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_name", title)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_director", directors)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "film_genre", genre)
        self.register_ocp_keyword(MediaType.MOVIE,
                                  "movie_streaming_provider",
                                  ["Mos Film",
                                   "MosFilm"])

    def _sync_db(self):
        bootstrap = "https://github.com/JarbasSkills/skill-mosfilm/raw/dev/bootstrap.json"
        data = requests.get(bootstrap).json()
        self.archive.merge(data)
        self.schedule_event(self._sync_db, random.randint(3600, 24 * 3600))

    def get_playlist(self, score=50, num_entries=25):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "bg_image": self.default_bg,
            "title": "MosFilm (Movie Playlist)",
            "author": "MosFilm"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 15 if media_type == MediaType.MOVIE else 0
        entities = self.ocp_voc_match(phrase)

        title = entities.get("movie_name")
        director = entities.get("movie_director")
        skill = "movie_streaming_provider" in entities  # skill matched

        base_score += 30 * len(entities)

        if title or director:
            base_score += 30
            if title:
                candidates = [video for video in self.archive.values()
                              if title.lower() in video["title"].lower()]
            else:
                candidates = [video for video in self.archive.values()
                              if director.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "author": video["author"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.MOVIE,
                    "uri": "youtube//" + video["url"],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["thumbnail"],
                    "bg_image": video["thumbnail"]
                }

        if skill:
            yield self.get_playlist()

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "image": video["thumbnail"],
            "match_confidence": 70,
            "media_type": MediaType.MOVIE,
            "uri": "youtube//" + video["url"],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "bg_image": video["thumbnail"],
            "skill_id": self.skill_id
        } for video in self.archive.values()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = MosFilmSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("movies by Tarkovsky", MediaType.MOVIE):
        print(r)
        # {'title': 'The Passion According to Andrei | DRAMA | By Andrei Tarkovsky', 'author': 'Mosfilm', 'match_confidence': 75, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=tiUAY6d67tQ', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/tiUAY6d67tQ/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/tiUAY6d67tQ/sddefault.jpg'}
        # {'title': 'Andrei Rublev | DRAMA | FULL MOVIE | by Andrei Tarkovsky', 'author': 'Mosfilm', 'match_confidence': 75, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=je75FDjcUP4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/je75FDjcUP4/sddefault.jpg?v=624fd8c3', 'bg_image': 'https://i.ytimg.com/vi/je75FDjcUP4/sddefault.jpg?v=624fd8c3'}
        # {'title': 'The Mirror | FULL MOVIE | Directed by Andrey Tarkovsky', 'author': 'Mosfilm', 'match_confidence': 75, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=NrMINC5xjMs', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/NrMINC5xjMs/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/NrMINC5xjMs/sddefault.jpg'}
        # {'title': "Ivan's Childhood | WAR MOVIE | directed by Andrey Tarkovsky", 'author': 'Mosfilm', 'match_confidence': 75, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=6Lnb1bI0VIk', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/6Lnb1bI0VIk/sddefault.jpg?v=624ee14e', 'bg_image': 'https://i.ytimg.com/vi/6Lnb1bI0VIk/sddefault.jpg?v=624ee14e'}
        # {'title': 'Stalker | FULL MOVIE | Directed by Andrey Tarkovsky', 'author': 'Mosfilm', 'match_confidence': 75, 'media_type': <MediaType.MOVIE: 10>, 'uri': 'youtube//https://youtube.com/watch?v=Q3hBLv-HLEc', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://i.ytimg.com/vi/Q3hBLv-HLEc/sddefault.jpg', 'bg_image': 'https://i.ytimg.com/vi/Q3hBLv-HLEc/sddefault.jpg'}
