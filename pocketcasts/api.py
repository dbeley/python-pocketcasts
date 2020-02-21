# -*- coding: utf-8 -*-
"""TODO: Class description API"""
from .episode import Episode
from .podcast import Podcast
import requests
import json


class Api(object):
    def __init__(self, email, password):
        self._session = requests.Session()
        login_json = {
            "email": email,
            "password": password,
            "scope": "webplayer",
        }
        response = self._session.post(
            "https://api.pocketcasts.com/user/login",
            headers={},
            json=login_json,
        )
        response.raise_for_status()
        # TODO(Check if login was successful, code is 200 in every case)

        self._api_header = {
            "authorization": "Bearer " + str(response.json()["token"])
        }

    def my_podcasts(self):
        data = {"v": "1"}
        response = self._session.post(
            "https://api.pocketcasts.com/user/podcast/list",
            headers=self._api_header,
            json=data,
        )
        response.raise_for_status()

        podcasts = []
        for podcast_json in response.json()["podcasts"]:
            podcast = Podcast._from_json(podcast_json, self)
            podcasts.append(podcast)
        return podcasts

    def featured_podcasts(self):
        response = self._session.get(
            "https://lists.pocketcasts.com/featured.json",
            headers=self._api_header,
            json={},
        )
        response.raise_for_status()

        podcasts = []
        for podcast_json in response.json()["podcasts"]:
            podcast = Podcast._from_json(podcast_json, self)
            podcasts.append(podcast)
        return podcasts

    def episodes_for_podcast(
        self, podcast, sort_order=Podcast.SortOrder.NewestFirst
    ):
        page = 1
        pages_left = True
        episodes = []
        params = {"page": page, "sort": sort_order, "uuid": podcast.uuid}
        response = self._session.post(
            "https://api.pocketcasts.com/user/podcast/episodes", json=params
        )
        response.raise_for_status()

        for episode_json in response.json()["podcast"]["episodes"]:
            episode = Episode._from_json(episode_json, podcast)
            # episode = episode_json
            episodes.append(episode)

        return episodes

    def podcast(self, uuid):
        data = {"uuid": uuid}

        url = (
            "https://cache.pocketcasts.com/podcast/full/"
            + str(uuid)
            + "/0/3/1000"
        )
        response = self._session.get(url, headers=self._api_header, json=data)
        response.raise_for_status()
        response_json = response.json()
        podcast = Podcast._from_json(response_json["podcast"], self)

        return podcast

    def popular_podcasts(self):
        response = self._session.get(
            "https://lists.pocketcasts.com/popular.json",
            headers=self._api_header,
            json={},
        )
        response.raise_for_status()

        podcasts = []
        for podcast_json in response.json()["podcasts"]:
            podcast = Podcast._from_json(podcast_json, self)
            podcasts.append(podcast)
        return podcasts

    def trending_podcasts(self):
        response = self._session.get(
            "https://lists.pocketcasts.com/trending.json",
            headers=self._api_header,
            json={},
        )
        response.raise_for_status()
        response.raise_for_status()

        podcasts = []
        for podcast_json in response.json()["podcasts"]:
            podcast = Podcast._from_json(podcast_json, self)
            podcasts.append(podcast)
        return podcasts

    def new_episodes_released(self):
        response = self._session.post(
            "https://api.pocketcasts.com/user/new_releases",
            headers=self._api_header,
            json={},
        )
        response.raise_for_status()

        episodes = []
        podcasts = {}
        for episode_json in response.json()["episodes"]:
            podcastUuid = episode_json["podcastUuid"]
            if podcastUuid not in podcasts:
                podcasts[podcastUuid] = self.podcast(podcastUuid)
            episode = Episode._from_json(episode_json, podcasts[podcastUuid])
            episodes.append(episode)
        return episodes

    def episodes_in_progress(self):
        response = self._session.post(
            "https://api.pocketcasts.com/user/in_progress",
            headers=self._api_header,
            json={},
        )
        response.raise_for_status()

        episodes = []
        podcasts = {}
        for episode_json in response.json()["episodes"]:
            podcastUuid = episode_json["podcastUuid"]
            if podcastUuid not in podcasts:
                podcasts[podcastUuid] = self.podcast(podcastUuid)
            episode = Episode._from_json(episode_json, podcasts[podcastUuid])
            episodes.append(episode)
        return episodes

    def starred_episodes(self):
        response = self._session.post(
            "https://api.pocketcasts.com/user/starred",
            headers=self._api_header,
            json={},
        )
        response.raise_for_status()

        episodes = []
        podcasts = {}
        for episode_json in response.json()["episodes"]:
            podcastUuid = episode_json["podcastUuid"]
            if podcastUuid not in podcasts:
                podcasts[podcastUuid] = self.podcast(podcastUuid)
            episode = Episode._from_json(episode_json, podcasts[podcastUuid])
            episodes.append(episode)
        return episodes

    def mark_as_played(self, podcastUuid, episode_uuid, played):
        params = {
            "podcast": podcastUuid,
            "status": 3,  # played
            "uuid": episode_uuid,
        }
        response = self._session.post(
            "https://api.pocketcasts.com/user/starred",
            headers=self._api_header,
            json=params,
        )

        ##TODO Check to see if we need to hit https://api.pocketcasts.com/up_next/remove

        response.raise_for_status()
        # TODO(Check response for error)

    def mark_as_starred(self, podcastUuid, episode_uuid, starred):
        params = {
            "starred": starred,
            "podcastUuid": podcastUuid,
            "uuid": episode_uuid,
        }
        response = self._session.post(
            "https://play.pocketcasts.com"
            "/web/episodes/"
            "update_episode_star.json",
            json=params,
        )
        response.raise_for_status()
        # TODO(Check response for error)

    def load_notes(self, episode_uuid):
        # Why star/mark played needs podcast uuid and this only episode uuid?
        # ¯\_(ツ)_/¯
        params = {"uuid": episode_uuid}
        response = self._session.post(
            "https://play.pocketcasts.com" "/web/episodes/" "show_notes.json",
            json=params,
        )
        response.raise_for_status()
        # TODO(Check response for error)

        show_notes = response.json()["show_notes"]

        return show_notes

    def search_podcasts(self, search_string):
        params = {"term": search_string}
        response = self._session.get(
            "https://play.pocketcasts.com" "/web/podcasts/search.json",
            data=params,
        )
        response.raise_for_status()

        podcasts = []
        for podcast_json in response.json()["podcasts"]:
            podcast = Podcast._from_json(podcast_json, self)
            podcasts.append(podcast)
        return podcasts

    def subscribe_podcast(self, podcastUuid, subscribe=True):
        if not subscribe:
            return self.unsubscribe(podcastUuid)

        params = {"uuid": podcastUuid}
        response = self._session.post(
            "https://play.pocketcasts.com" "/web/podcasts/" "subscribe.json",
            json=params,
        )
        response.raise_for_status()
        # TODO(Check response for error)

    def unsubscribe_podcast(self, podcastUuid):
        params = {"uuid": podcastUuid}
        response = self._session.post(
            "https://play.pocketcasts.com" "/web/podcasts/" "unsubscribe.json",
            json=params,
        )
        response.raise_for_status()
        # TODO(Check response for error)

    def update_episode_position(
        self, podcastUuid, episode_uuid, position, episode_duration=0
    ):
        # TODO(Check position value < duration)
        params = {
            "playing_status": Episode.PlayingStatus.Unplayed,
            "podcastUuid": podcastUuid,
            "uuid": episode_uuid,
            "played_up_to": position,
            # web player sends duration so do I...
            "duration": episode_duration,
        }
        response = self._session.post(
            "https://play.pocketcasts.com"
            "/web/episodes/"
            "update_episode_position.json",
            json=params,
        )
        response.raise_for_status()
        # TODO(Check response for error)
