from collections import Counter


class CaseInsensitiveCounter(dict):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key.lower())[1]
        except KeyError:
            return 0

    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), (key, value))

    def __delitem__(self, key):
        if key in self:
            super().__delitem__(key.lower())

    def __iter__(self):
        return (super().__getitem__(x)[0] for x in super().__iter__())

    def __eq__(self, other):
        for key in other.keys():
            if self[key] != other[key]:
                return False
        return True

    def __contains__(self, key):
        return super().__contains__(key.lower())

    def items(self):
        return (x[1] for x in super().items())