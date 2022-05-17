import logging
import os.path

import webuntis
from cachetools import TTLCache, cached
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesUpdateEvent, PreferencesEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from webuntis import Session
from webuntis.objects import KlassenList

from utils import save_image_hex, boldify

logger = logging.getLogger(__name__)
session: Session

five_minute_cache = TTLCache(maxsize=100, ttl=60 * 5)
one_hour_cache = TTLCache(maxsize=100, ttl=60 * 60)


@cached(five_minute_cache)
def get_cached_result(method):
    return method()


class WebUntisExtension(Extension):
    """
    Syntax:

    (wu timetable)|(wt) [class name] [date]

    wu holidays
    """

    def __init__(self):
        super(WebUntisExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())
        self.subscribe(PreferencesEvent, PreferencesUpdateEventListener())

    @staticmethod
    def class_list(query):
        """ List classes """

        if query:
            query = query.lower()
        # with open(self.class_cache_file) as cache_file:
        # classes = json.load(cache_file)
        classes: KlassenList = get_cached_result(session.klassen)

        items = []
        for clazz in classes:
            if query and query != "" and query not in clazz.name.lower():
                continue

            name = clazz.name
            if query:
                name = boldify(query, name)

            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=name,
                description=clazz.long_name,
                highlightable=True
            ))

        return RenderResultListAction(items[:8])


class KeywordQueryEventListener(EventListener):

    def on_event(self, event: KeywordQueryEvent, extension):
        query = (event.get_argument() or "").split(" ")

        return extension.class_list(query[0])


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        return RenderResultListAction([ExtensionResultItem(icon='images/icon.png',
                                                           name=data['new_name'],
                                                           on_enter=HideWindowAction())])


class PreferencesUpdateEventListener(EventListener):

    def on_event(self, event, extension):
        global session
        # use `event` instead of `extension` because the event is getting called before the extension preferences get updated
        session = webuntis.Session(
            server=event.preferences['url'],
            username=event.preferences['username'],
            password=event.preferences['password'],
            school=event.preferences['school'],
            useragent=event.preferences['useragent'],
        )
        session.login()

        """ Save lesson code images """
        for period_code in session.statusdata().period_codes:
            save_image_hex(os.path.join(".local", period_code.name + ".png"), "#" + period_code.backcolor)


if __name__ == '__main__':
    WebUntisExtension().run()
