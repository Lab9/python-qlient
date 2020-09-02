from typing import Union


def get_version() -> str:
    """
    Get the version from qlient
    :return: the version of qlient
    """
    from qlient import __version__
    return __version__


def remove_duplicate_spaces(string: str) -> str:
    """
    Remove duplicate spaces from a string
    :param string: the string to remove the duplicate spaces from
    :return: a string with no double spaces.
    """
    return " ".join(string.split())


def adapt_websocket_endpoint(endpoint: str) -> Union[str, None]:
    """
    Adapt the given http[s] endpoint to a websocket endpoint.
    :param endpoint: holds the endpoints host address with protocol
    :return: the websocket url
    """
    if endpoint.startswith("https://"):
        return "wss://" + endpoint.replace("https://", "")
    elif endpoint.startswith("http://"):
        return "ws://" + endpoint.replace("http://", "")
    else:
        return None
