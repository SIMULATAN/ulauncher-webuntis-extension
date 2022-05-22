import re
from pathlib import Path

from PIL import Image
from cachetools import TTLCache, cached
from webuntis.objects import HolidayObject


def save_image_hex(name, hexcolor):
    im = Image.new("RGB", (100, 100), hexcolor)
    Path(name).parent.mkdir(parents=True, exist_ok=True)
    im.save(name)


def boldify(query, inpt):
    return re.sub(r"(" + query + ")", r"<b>\g<0></b>", inpt, flags=re.IGNORECASE)


five_minute_cache = TTLCache(maxsize=100, ttl=60 * 5)
one_hour_cache = TTLCache(maxsize=100, ttl=60 * 60)


@cached(five_minute_cache)
def get_five_min_cache_result(method):
    return method()


@cached(one_hour_cache)
def get_one_hour_cache_result(method):
    return method()


def period(delta, pattern):
    d = {'d': delta.days}
    d['h'], rem = divmod(delta.seconds, 3600)
    d['m'], d['s'] = divmod(rem, 60)
    return pattern.format(**d)


def sort_holidays(holidays):
    result = []
    for holiday in holidays:
        result.append(holiday)
    result.sort(key=holiday_start)
    return result


def holiday_start(holiday: HolidayObject):
    return holiday.start
