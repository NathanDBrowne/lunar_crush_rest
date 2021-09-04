import time
import urllib.request as urllib2
from typing import Optional, Dict, Any, List
import sys
import json
import pandas as pd
import webbrowser
from datetime import datetime

from requests import Request, Session, Response
import hmac
from ciso8601 import parse_datetime


class CrushClient:

    def __init__(self, api_key=None) -> None:

        _ENDPOINT = 'https://api.lunarcrush.com/v2?key='
        self._session = Session()
        self._api_key = api_key

        if self._api_key == None:
            webbrowser.open('https://lunarcrush.com/developers/docs')
            sys.exit('Please generate an API key at LunarCrush.')

        self._request_head = _ENDPOINT + self._api_key

    def _REQUEST(self, req_str):
        api_request = urllib2.Request(self._request_head + req_str)
        try:
            api_reply = urllib2.urlopen(api_request).read()
        except Exception as error:
            print("API call failed (%s)" % error)
            sys.exit(1)
        try:
            api_reply = api_reply.decode()
        except Exception as error:
            if api_method == 'RetrieveExport':
                sys.stdout.buffer.write(api_reply)
                sys.exit(0)
            print("API response invalid (%s)" % error)
            sys.exit(1)
        return json.loads(api_reply)
    
    def help(self):
        webbrowser.open('https://lunarcrush.com/developers/docs')

    def get_info(self, req_type='assets', **kwargs):
        '''
        Once you have your call response, you can use
        'response.attr_names' to see what types of info you've got.

        timeSeries are automatically turned into Pandas DataFrame

        '''
        req_str = '&data=' + req_type
        for arg_name in list(kwargs.keys()):
            req_str = req_str + '&' + arg_name + '=' + str(kwargs[arg_name])

        # print('\n\nSending Request:\n', req_str, '\n\n')

        return to_neatform(self._REQUEST(req_str))


def to_neatform(responses):

    new_data_dict = {}

    if responses['config']['data'] == 'influencers':
        new_df = pd.DataFrame(responses['data'])
        new_df.set_index('twitter_screen_name', inplace=True)
        new_df.sort_values(by='engagement_rank', ascending=False, inplace=True)
        responses['data'] = new_df
    else:
        if type(responses['data']) == dict:
            new_data_dict = ParsedResponse(responses['data'])
        else:
            for response in responses['data']:

                if 'symbol' in list(response.keys()):
                    symb_key = str(response['symbol'])
                elif 's' in list(response.keys()):
                    symb_key = str(response['acr']) + ':' + str(response['s'])

                new_data_dict[symb_key] = ParsedResponse(response)

        responses['data'] = new_data_dict

    return responses


class ParsedResponse:
    def __init__(self, response):

        self.attr_names = []
        for var_name in list(response.keys()):
            setattr(self, var_name, response[var_name])
            self.attr_names.append(var_name)

        if 'timeSeries' in self.attr_names:
            self.timeSeries = pd.DataFrame(self.timeSeries)

            if 'time' in self.timeSeries.columns:
                self.timeSeries['datetime'] = pd.to_datetime(
                    self.timeSeries['time'], unit='s')
                self.timeSeries.set_index('datetime', inplace=True)
            else:
                self.timeSeries.set_index('ts', inplace=True)

        if 'marketPairs' in self.attr_names:
            self.marketPairs = pd.DataFrame(self.marketPairs)
            self.marketPairs.set_index('unique_key', inplace=True)
            '''
            EDIT REQUIRED: Parse the 1d and 30d correctly!
            '''
            # self.marketPairs.drop(columns=['1d', '30d'], axis=1, inplace=True)

        if 'exchanges' in self.attr_names:
            self.exchanges = pd.DataFrame(self.exchanges)
            self.exchanges.set_index('lunar_id', inplace=True)

        if 'history' in self.attr_names:
            self.history = pd.DataFrame(self.history)
            self.history['last_cotd'] = pd.to_datetime(
                self.history['last_cotd'], unit='s')
            self.history.set_index('last_cotd', inplace=True)

        if 'last_changed' in self.attr_names:
            self.last_changed = datetime.fromtimestamp(self.last_changed)

        if 'verified' in self.attr_names:
            self.tweets = pd.DataFrame(self.tweets)
            self.tweets.sort_values(by='time', inplace=True)
            self.tweets['datetime'] = pd.to_datetime(
                self.tweets['time'], unit='s')
            self.tweets.set_index('id', inplace=True)

        if self.attr_names == ['profile', 'stats', 'tweets']:
            self.stats['daily_metrics'] = pd.DataFrame(
                self.stats['daily_metrics'])
            self.stats['daily_metrics'].rename(
                columns={'engagements': 'engagement'}, inplace=True)
            self.stats['daily_metrics'].sort_values(by='day', inplace=True)
            self.stats['daily_metrics']['datetime'] = pd.to_datetime(
                self.stats['daily_metrics']['day'], unit='s')
