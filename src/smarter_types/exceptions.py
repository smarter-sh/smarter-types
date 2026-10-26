"""The exceptions that smarter-types raises."""


class SmarterTypesError(Exception):
    """The base class of every exception that smarter-types raises."""


class SmarterTypesValueError(SmarterTypesError, ValueError):
    """A value that is not one of an enumeration's, e.g. a string that is not a SAM kind."""


__all__ = ["SmarterTypesError", "SmarterTypesValueError"]
