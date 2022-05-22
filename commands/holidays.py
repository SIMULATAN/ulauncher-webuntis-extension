import datetime
from datetime import datetime, timedelta

from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from webuntis.objects import HolidayList

from utils import get_one_hour_cache_result, boldify, period, sort_holidays


def holiday_command(session, query):
    query = " ".join(query)
    holidays: HolidayList = sort_holidays(get_one_hour_cache_result(session.holidays))
    results = []
    for holiday in holidays:
        if holiday.start < datetime.now():
            continue

        name = holiday.name
        if query and query != "":
            if query not in holiday.name.lower():
                continue
            else:
                name = boldify(query, holiday.name)

        results.append(ExtensionResultItem(
            icon='images/icon.png',
            name=name,
            description=holiday.start.strftime('%d.%m.%Y') + ' - ' + holiday.end.strftime('%d.%m.%Y') + " (in " + period(holiday.start - datetime.now(),
                        "{d} days, {h} hours and {m} minutes") + ", " + period((holiday.end - holiday.start) + timedelta(days=1), "{d} days long") + ")",
            highlightable=True
        ))

    return RenderResultListAction(results[:8])
