from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="GraphQL Schema Inspector CLI")

    parser.add_argument(
        "-i", "--inspect",
        type=str,
        dest="inspect",
        required=True,
        help="The url to inspect"
    )

    args = parser.parse_args()

    from qlient import loaders
    import requests
    import json
    result = loaders.request_schema(args.inspect, requests.sessions.session())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
