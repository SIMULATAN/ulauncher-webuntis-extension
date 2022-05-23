import logging
import os.path

import webuntis
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, PreferencesUpdateEvent, PreferencesEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from webuntis import Session
from webuntis.objects import KlassenList

from commands.holidays import holiday_command
from utils import save_image_hex, boldify, get_five_min_cache_result

logger = logging.getLogger(__name__)
session: Session


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
        classes: KlassenList = get_five_min_cache_result(session.klassen)

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

    def on_event(self, event: KeywordQueryEvent, extension: Extension):
        arg = (event.get_argument() or "")

        query = arg.split(" ") if (arg and arg != "") else []

        if event.get_keyword() == extension.preferences["kw_holidays"]:
            return holiday_command(session, query)

        if len(query) == 0:
            return RenderResultListAction([
                ExtensionResultItem(icon='images/icon.png',
                                    name='TimeTable',
                                    description='Access the timetable of a school or class',
                                    on_enter=HideWindowAction()),
                ExtensionResultItem(icon='images/icon.png',
                                    name='Holidays',
                                    description='Access holidays',
                                    on_enter=SetUserQueryAction(extension.preferences["kw_holidays"] + " "))
            ])

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
        logger.debug("Logged in")

        """ Save lesson code images """
        for period_code in session.statusdata().period_codes:
            save_image_hex(os.path.join(".local", period_code.name + ".png"), "#" + period_code.backcolor)
            logger.debug("Saved image for period code '" + period_code.name + "' with hex '#" + period_code.backcolor + "'")


if __name__ == '__main__':
    WebUntisExtension().run()
