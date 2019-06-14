"""
SCF Custom Exceptions
"""


class SCFException(Exception):
    """custom exceptions"""
    pass


class IntegrityError(SCFException):
    """
    Violation of data integrity restriction at the application level
    (as opposed to being enfoced by a database constraint).
    """


class HasDependents(IntegrityError):
    """
    Object cannot be deleted because other objects depend on it.
    """
