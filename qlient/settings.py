class Settings:
    """
    A Settings object holds necessary settings for the library to work.
    Each setting can be changed but do this with caution.
    """

    def __init__(
            self,
            max_recursion_depth=2,
            base_response_key="data",
            base_payload_key="payload",
            return_requests_response=False,
            disable_selection_lookup=False,
            return_full_subscription_body=False
    ):
        """
        Instantiate a new Settings instance to be used by a client.

        :param max_recursion_depth: holds the max depth for looking up return fields when no selection is passed by.
        :param base_response_key: holds the base response key. This is probably "data" in most cases.
        :param base_payload_key: holds the base payload key for websockets. This is probably "payload" in most cases.
        :param return_requests_response: True if you want the requests response object. If False will try to parse json.
        :param disable_selection_lookup: Set to True if you want no automatic lookup when no selection was passed by.
        :param return_full_subscription_body: Set to True if you want the complete websocket response body
        """
        self.max_recursion_depth = max_recursion_depth
        self.default_response_key = base_response_key
        self.default_payload_key = base_payload_key
        self.return_requests_response = return_requests_response
        self.disable_selection_lookup = disable_selection_lookup
        self.return_full_subscription_body = return_full_subscription_body
