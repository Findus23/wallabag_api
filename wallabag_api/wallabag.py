# coding: utf-8
import requests
from requests import HTTPError
import logging

__author__ = 'foxmask'


logging.basicConfig(format='%(message)s', level=logging.INFO)

__all__ = ['Wallabag']


class Wallabag(object):
    """
        Python Class 'Wallabag' to deal with Wallabag REST API
        This class is able to handle any data from your Wallabag account
    """

    host = ''
    token = ''
    client_id = ''
    client_secret = ''
    user_agent = ''
    format = ''
    username = ''
    password = ''

    def __init__(self,
                 host='',
                 token='',
                 client_id='',
                 client_secret='',
                 extension='json',
                 user_agent="WallabagPython/1.0 "
                            "+https://github.com/foxmask/wallabag-api"):
        """
            init variable
            :param host: string url to the official API Wallabag
            :param token: string of the key provided by Wallabag
            :param client_id client id
            :param client_secret client secret
            :param extension: json/xml/html
            :param user_agent
        """
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = token
        self.format = extension
        self.user_agent = user_agent

    def get_host(self):
        """
            get the host from which to get API
            :return host
        """
        return self.host

    def query(self, path, method='get', **params):
        """
            Do a query to the System API
            :param path: url to the API
            :param method: the kind of query to do
            :param params: a dict with all the
            necessary things to query the API
            :return json data
        """
        if method in ('get', 'post', 'patch', 'delete', 'put'):
            full_path = self.get_host() + path
            if method == 'get':
                r = requests.get(full_path, params=params)
            elif method == 'post':
                r = requests.post(full_path, data=params)
            elif method == 'patch':
                r = requests.patch(full_path, data=params)
            elif method == 'delete':
                r = requests.delete(full_path, headers=params)
            elif method == 'put':
                r = requests.put(full_path, params=params)
            return self.handle_json_response(r)
        else:
            raise ValueError('method expected: get, post, patch, delete, put')

    @staticmethod
    def handle_json_response(responses):
        """
            get the json data response
            :param responses: the json response
            :return the json data without 'root' node
        """
        if responses.status_code != 200:
            raise HTTPError(responses.status_code, responses.json())
        json_data = {}
        try:
            json_data = responses.json()
        except:
            for error in json_data['errors']:
                error_json = json_data['errors'][error]['content']
                logging.error("Wallabag: {error}".format(error=error_json))
        return json_data

    def __get_attr(self, what, type_attr, value_attr, **kwargs):
        value = int(kwargs[what]) if type_attr == 'int' else kwargs[what]
        if what in kwargs and value in value_attr:
            return value

    def get_entries(self, **kwargs):
        """

            GET /api/entries.{_format}

            Retrieve all entries. It could be filtered by many options.

            :param kwargs: can contain one of the following filters
                archive:  '0' or '1', default '0' filter by archived status.
                star: '0' or '1', default '0' filter by starred status.
                delete: '0' or '1', default '0' filter by deleted status.
                sort: 'created' or 'updated', default 'created'
                order: 'asc' or 'desc', default 'desc'
                page: int default 1 what page you want
                perPage: int default 30 result per page
                tags: list of tags url encoded.
                Will returns entries that matches ALL tags
            :return data related to the ext
        """
        # default values
        params = dict({'access_token': self.token,
                       'archive': 0,
                       'star': 0,
                       'delete': 0,
                       'sort': 'created',
                       'order': 'desc',
                       'page': 1,
                       'perPage': 30,
                       'tags': []})

        params['archive'] = self.__get_attr(what='archive',
                                            type_attr=int,
                                            value_attr=(0, 1),
                                            **kwargs)
        params['star'] = self.__get_attr(what='star',
                                         type_attr=int,
                                         value_attr=(0, 1),
                                         **kwargs)
        params['delete'] = self.__get_attr(what='delete',
                                           type_attr=int,
                                           value_attr=(0, 1),
                                           **kwargs)
        params['order'] = self.__get_attr(what='order',
                                          type_attr=str,
                                          value_attr=('asc', 'desc'),
                                          **kwargs)

        if 'page' in kwargs and isinstance(kwargs['page'], int):
            params['page'] = kwargs['page']
        if 'perPage' in kwargs and isinstance(kwargs['perPage'], int):
            params['perPage'] = kwargs['perPage']
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            params['tags'] = kwargs['tags']

        path = '/api/entries.{ext}'.format(ext=self.format)

        return self.query(path, "get", **params)

    def post_entries(self, url, title='', tags='', starred=0, archive=0):
        """

            POST /api/entries.{_format}

            Create an entry

            :param url: the url of the note to store
            :param title: Optional, we'll get the title from the page.
            :param tags: tag1,tag2,tag3 a comma-separated list of tags.
            :param starred entry already starred
            :param archive entry already archived
            :return result
        """
        params = {'access_token': self.token, 'url': url, 'title': title,
                  'tags': tags, 'starred': starred, 'archive': archive}
        if len(tags) > 0 and isinstance(tags, list):
            params['tags'] = ', '.join(tags)
        path = '/api/entries.{ext}'.format(ext=self.format)
        return self.query(path, "post", **params)

    def get_entry(self, entry):
        """

            GET /api/entries/{entry}.{_format}

            Retrieve a single entry

            :param entry: \w+ an integer The Entry ID
            :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}.{ext}'.format(entry=entry,
                                                  ext=self.format)
        return self.query(url, "get", **params)

    def patch_entries(self, entry, **kwargs):
        """

            PATCH /api/entries/{entry}.{_format}

            Change several properties of an entry

            :param entry: the entry to 'patch' / update
            :param kwargs: can contain one of the following
                title: string
                tags: a list of tags tag1,tag2,tag3
                archive:  '0' or '1', default '0' archived the entry.
                star: '0' or '1', default '0' starred the entry
                delete: '0' or '1', default '0' flag as deleted.
                In case that you don't want to *really* remove it..
            :return data related to the ext
        """
        # default values
        params = {'access_token': self.token,
                  'title': '',
                  'archive': 0,
                  'tags': [],
                  'star': 0,
                  'delete': 0}

        if 'title' in kwargs:
            params['title'] = kwargs['title']
        if 'tags' in kwargs and isinstance(kwargs['tags'], list):
            params['tags'] = ', '.join(kwargs['tags'])

        params['archive'] = self.__get_attr(what='archive',
                                            type_attr=int,
                                            value_attr=(0, 1),
                                            **kwargs)
        params['star'] = self.__get_attr(what='star',
                                         type_attr=int,
                                         value_attr=(0, 1),
                                         **kwargs)
        params['delete'] = self.__get_attr(what='delete',
                                           type_attr=int,
                                           value_attr=(0, 1),
                                           **kwargs)
        params['order'] = self.__get_attr(what='order',
                                          type_attr=str,
                                          value_attr=('asc', 'desc'),
                                          **kwargs)

        path = '/api/entries/{entry}.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(path, "patch", **params)

    def delete_entries(self, entry):
        """

            DELETE /api/entries/{entry}.{_format}

            Delete permanently an entry

            :param entry: \w+ an integer The Entry ID
            :return result
        """

        params = {'Authorization': 'Bearer {}'.format(self.token)}
        path = '/api/entries/{entry}.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(path, "delete", **params)

    def get_entry_tags(self, entry):
        """

            GET /api/entries/{entry}/tags.{_format}

            Retrieve all tags for an entry

            :param entry: \w+ an integer The Entry ID
            :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/tags.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(url, "get", **params)

    def post_entry_tags(self, entry, tags):
        """

            POST /api/entries/{entry}/tags.{_format}

            Add one or more tags to an entry

            :param entry: \w+ an integer The Entry ID
            :param tags: string
            :return result
        """
        params = {'access_token': self.token, 'tags': []}
        if isinstance(tags, list):
            params['tags'] = tags
        path = '/api/entries/{entry}/tags.{ext}'.format(
            entry=entry, ext=self.format)
        return self.query(path, "post", **params)

    def delete_entry_tag(self, entry, tag):
        """

            DELETE /api/entries/{entry}/tags/{tag}.{_format}

            Permanently remove one tag for an entry

            :param entry: \w+ an integer The Entry ID
            :param tag: string The Tag
            :return data related to the ext
        """
        params = {'access_token': self.token}
        url = '/api/entries/{entry}/tags/{tag}.{ext}'.format(
            entry=entry, tag=tag, ext=self.format)
        return self.query(url, "delete", **params)

    def get_tags(self):
        """

            GET /api/tags.{_format}

            Retrieve all tags

            :return data related to the ext
        """
        params = {'access_token': self.token}
        path = '/api/tags.{ext}'.format(ext=self.format)
        return self.query(path, "get", **params)

    def delete_tag(self, tag):
        """

            DELETE /api/tags/{tag}.{_format}

            Permanently remove one tag from every entry

            :param tag: string The Tag
            :return data related to the ext
        """
        path = '/api/tags/{tag}.{ext}'.format(tag=tag, ext=self.format)
        params = {'access_token': self.token}
        return self.query(path, "delete", **params)

    @classmethod
    def get_token(cls, host, **params):
        """
        :param host: host of the service
        :param params: will contain :

        params = {"grant_type": "password",
                  "client_id": "a string",
                  "client_secret": "a string",
                  "username": "a login",
                  "password": "a password"}

        :return: access token
        """
        params['grant_type'] = ["password"]
        path = "/oauth/v2/token"
        r = requests.post(host + path, data=params)
        return cls.handle_json_response(r)['access_token']
