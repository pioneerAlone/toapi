from toapi.selector import Selector


def with_metaclass(meta):
    return meta("toapi", (object,), {})


class ItemType(type):
    def __new__(cls, what, bases=None, dict=None):
        selectors = {}
        for name, selector in dict.items():
            if isinstance(selector, Selector):
                selectors[name] = selector
        dict['selectors'] = selectors
        dict['__base_url__'] = dict.get('__base_url__', None)
        dict['name'] = what.lower()
        for name in selectors:
            del dict[name]
        return type.__new__(cls, what, bases, dict)


class Item(with_metaclass(ItemType)):
    """Parse item from html"""

    @classmethod
    def parse(cls, html):
        """Parse html to json"""
        if cls.Meta.source is None:
            return cls._parse_item(html)
        else:
            sections = cls.Meta.source.parse(html)
            results = []
            for section in sections:
                results.append(cls._parse_item(section))
            return results

    @classmethod
    def _parse_item(cls, html):
        item = {}
        for name in cls.selectors:
            try:
                item[name] = getattr(cls, name)
            except IndexError:
                item[name] = ''
            except Exception:
                item[name] = ''
        item = cls._clean_item(item)
        return item

    @classmethod
    def _clean_item(cls, item):
        for index, field_name in enumerate(item):
            clean_method = getattr(cls, 'clean_%s' % field_name, None)
            if clean_method:
                item[field_name] = clean_method(cls, item[field_name])
            return item

    class Meta:
        source = None
        route = '\.+'
