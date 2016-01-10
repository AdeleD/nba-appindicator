from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import AppIndicator3 as appindicator

import signal
import requests


from requests.exceptions import ConnectionError

try:
    import urllib.parse as urlrequest
except ImportError:
    import urllib as urlrequest

from datetime import datetime, timedelta

import os


APPINDICATOR_ID = 'nba_indicator'


class NBAIndicator():
    def __init__(self):
        self.indicator = appindicator.Indicator.new(
            APPINDICATOR_ID,
            os.path.join(os.path.dirname(__file__), 'nba-logo.svg'),
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_attention_icon("indicator-messages-new")

        self.create_menu()

    def run(self):
        Gtk.main()

    def quit(self):
        Gtk.main_quit()

    def open_browser(self, gameinfo_url):
        Gtk.show_uri(
            Gdk.Screen.get_default(),
            gameinfo_url,
            Gtk.get_current_event_time()
        )

    def create_menu(self):
        menu = Gtk.Menu()

        # NBA results items
        for game in self.nba_games:
            item = Gtk.MenuItem(game['score'])
            item.connect('activate', self.on_click, game['gameinfo_url'])
            menu.append(item)

        # Quit item
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.on_quit)
        menu.append(item_quit)

        menu.show_all()

        self.indicator.set_menu(menu)

    @property
    def nba_games(self):
        yesterday = datetime.now() - timedelta(days=1)
        scoreboard = Scoreboard(yesterday, '00', '00')
        return scoreboard.games

    def on_quit(self, _):
        self.quit()

    def on_click(self, source, gameinfo_url):
        self.open_browser(gameinfo_url)


class NBAStatsAPI():
    def __init__(self):
        self.api_url = 'http://stats.nba.com/stats/'

    def request(self, endpoint, params):
        params = params or {}
        encoded_params = urlrequest.urlencode(params)

        url = self.absolute_url(endpoint, encoded_params)

        try:
            result = requests.get(url)
        except ConnectionError as e:
            raise Exception('Unable to connect to stats.nba.com. %s' % e)

        if result.content:
            return result.json()

    def absolute_url(self, endpoint, encoded_params):
        return '%s%s?%s' % (self.api_url, endpoint, encoded_params)


class NBAObject():
    nba_api = NBAStatsAPI()


class Scoreboard(NBAObject):
    endpoint = 'scoreboard'

    def __init__(self, date, day_offset, league_id):
        self.date = date
        self.day_offset = day_offset
        self.league_id = league_id

        params = {
            'gameDate': self.date.strftime('%m/%d/%Y'),
            'DayOffset': day_offset,
            'LeagueID': league_id
        }

        self.result = self.nba_api.request(self.endpoint, params)

        self.results = self.parse_results()

    def parse_results(self):
        results = {}

        result_sets = self.result['resultSets']
        for result in result_sets:
            results[result['name']] = []

            for row in result['rowSet']:
                game = {}

                for key, value in enumerate(row):
                    game[result['headers'][key].lower()] = value

                results[result['name']].append(game)

        return results

    @property
    def game_header(self):
        return self.results['GameHeader']

    @property
    def line_score(self):
        return self.results['LineScore']

    @property
    def teams_scores(self):
        teams = {}
        for line in self.line_score:
            teams[line['team_id']] = {
                'name': line['team_abbreviation'],
                'pts': line['pts']
            }

        return teams

    @property
    def team_score(self, team_id):
        return self.teams_scores[team_id]

    @property
    def games(self):
        games = []
        for game in self.game_header:
            visitor_team = self.teams_scores[game['visitor_team_id']]
            home_team = self.teams_scores[game['home_team_id']]

            final_score = '%s @ %s: %s - %s' % (visitor_team['name'],
                                                home_team['name'],
                                                visitor_team['pts'] or '0',
                                                home_team['pts'] or '0')

            gameinfo_url = ('http://www.nba.com/games/%s/%s%s/'
                            'gameinfo.html?ls=iref:nba:scoreboard'
                            % (self.date.strftime('%Y%m%d'),
                               visitor_team['name'], home_team['name']))

            games.append({
                'score': final_score,
                'gameinfo_url': gameinfo_url
            })

        return games


def main():
    NBAIndicator().run()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    main()
