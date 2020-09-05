# Qlient: Python GraphQL Client

A fast and modern graphql client library designed with simplicity in mind.

[![pypi][pypi-image]][pypi-url]
[![GitHub license][github-license-image]][github-license-url]
[![Wheel][pypi-wheel-image]][pypi-wheel-url]
[![Language][language-image]][language-url]


[pypi-image]: https://img.shields.io/pypi/v/python-qlient.svg?style=flat
[pypi-url]: https://pypi.python.org/pypi/python-qlient

[github-license-image]: https://img.shields.io/github/license/Lab9/python-qlient.svg
[github-license-url]: https://github.com/Lab9/python-qlient/blob/master/LICENSE

[pypi-wheel-image]: https://img.shields.io/pypi/wheel/python-qlient.svg
[pypi-wheel-url]: https://pypi.python.org/pypi/python-qlient

[language-image]: https://img.shields.io/badge/lang-python-green
[language-url]: https://www.python.org/

## Getting Started

### Installing

```shell script
pip install python-qlient
```

### Usage
This example shows a simple query
```python
from qlient import Client

client = Client("https://countries.trevorblades.com/")

response = client.query.countries(select=["name"])
```

## Documentation
The Documentation covers the following points:
* [Query](#query)
* [Mutation](#mutation)
* [Subscription](#subscription)
* [Transporter](#transporter)
    * [AsyncTransporter](#asynctransporter)
* [Settings](#settings)
    * [max_recursion_depth](#max_recursion_depth)
    * [base_response_key](#base_response_key)
    * [base_payload_key](#base_payload_key)
    * [return_requests_response](#return_requests_response)
    * [disable_selection_lookup](#disable_selection_lookup)
    * [return_full_subscription_body](#return_full_subscription_body)
* [CLI](#cli)

### Query
Queries are the A and O of graphql and are as easy as:
```python
from qlient import Client

client = Client("https://countries.trevorblades.com/")

response = client.query.country(select=["name", "capital"], where={"code": "CH"})
```
Which will make a request to the server and return the name and capital of the country switzerland.

But what if you want to make a more complex query with fields within fields?
Don't need to worry, we got you covered:
```python
from qlient import Client, fields

client = Client("https://countries.trevorblades.com/")

response = client.query.country(select=fields("name", "capital", languages=fields("name")), where={"code": "CH"})
```
Using the fields method from `qlient` you can simply use `*args` and `**kwargs` for making deeper selections.
By the way, you could stack this like forever.

Last but not least, what if you don't know the fields you could select?
Yup, we got you somewhat covered as well. The thing is, that due to performance issues,
this package is not able to completely create a query that retrieves all fields for a Query.
I have set the max depth to **2** (Can be changed via [Settings](#settings)). This allows to still send a query without selecting any fields
but you won't get them all. If you want all, use the `fields` function defined above.

```python
from qlient import Client

client = Client("https://countries.trevorblades.com/")

response = client.query.country(where={"code": "CH"})
```

### Mutation
I haven't found a real world example for making mutations without being authenticated,
so here's a hypothetical one.
```python
from qlient import Client

client = Client("https://some-host.com/authentication")

response = client.mutation.register(data={"email": "foo@bar.com", "password": "987654321"}, select=["userId"])
```

### Subscription
Sometimes you want to execute things when something - an action - happened on the server.
In those cases, you can subscribe to an event.
For subscribing to an endpoint, I am using the asyncio `websockets` library.
So have a look at their [documentation](https://pypi.org/project/websockets/) for clarification.

Here is a basic example
```python
import asyncio
from qlient import Client

client = Client("http://your-host:8080")  # remains the same

def on_event(data: dict):
    # ... do something with the data
    print(data)

asyncio.run(client.subscription.my_subscription(handle=on_event))  # the asyncio.run() function is important!
```

#### Different Websocket endpoint
If no websocket endpoint was specified, it gets adapted based on the given request host.
for example `http://localhost:3000` becomes `ws://localhost:3000`.
Same goes for secured connections: `https` becomes `wss`.
But it may be, that you have different endpoints. Therefor you can specify the websocket endpoint
manually.
```python
from qlient import Client

client = Client("http://your-host:8080", ws_endpoint="wss://your-other-host:3000")
```

### Transporter
For making requests, we use a transporter. (Irrelevant for Websockets.)

If none is given, a new one will be created.

Sometimes you want your own custom session to be used for making requests.
For example if you need to authenticate yourself with some sort of an api key.
Therefor, you can pass it directly to the transporter.

```python
import requests

from qlient import Client, Transporter

my_session = requests.sessions.session()

my_session.headers["Authorization"] = "Bearer some-api-token"

client = Client("https://foo.bar/", transporter=Transporter(session=my_session))
```

#### AsyncTransporter

And an AsyncTransporter:
```python
import asyncio

from qlient import Client, AsyncTransporter

client = Client("https://countries.trevorblades.com/", transporter=AsyncTransporter())

async def request_data():
    return await client.query.country(select=["name", "capital"], where={"code": "CH"})

asyncio.run(request_data())
```

### Settings
Most things can be adjusted using the settings.
When no settings are passed by to a client, the default values will be used instead

#### max_recursion_depth
The max_recursion_depth can be used for changing the max depth for deeper automatic selection lookup.
Default is 2.
```python
from qlient import Client, Settings

settings = Settings(max_recursion_depth=5)  # Due to performance reasons I do not recommend to go any higher than that.

client = Client("https://countries.trevorblades.com/", settings=settings)
```

#### base_response_key
The base_response_key can be changed for setting the base key that is being used to get the data from the server.
Default is "data".
```python
from qlient import Client, Settings

settings = Settings(base_response_key="my_custom_data_key")

client = Client("https://countries.trevorblades.com/", settings=settings)
```

#### base_payload_key
The base_payload_key can be changed for setting the base key that is being used to read the data from the websocket response.
Default is "payload".
```python
from qlient import Client, Settings

settings = Settings(base_payload_key="my_custom_payload_key")

client = Client("https://countries.trevorblades.com/", settings=settings)
```

#### return_requests_response
The return_requests_response can be set to True if you want the whole request back instead of just the json.
Default is False.
```python
from qlient import Client, Settings

settings = Settings(return_requests_response=True)

client = Client("https://countries.trevorblades.com/", settings=settings)
```

#### disable_selection_lookup
The disable_selection_lookup can be set to True if you want to disable the automatic selection lookup.
Default is False.
```python
from qlient import Client, Settings

settings = Settings(disable_selection_lookup=True)

client = Client("https://countries.trevorblades.com/", settings=settings)
```

#### return_full_subscription_body
The return_full_subscription_body can be set to True if you want to get the full websocket response instead of only
the data.
```python
from qlient import Client, Settings

settings = Settings(return_full_subscription_body=True)

client = Client("https://countries.trevorblades.com/", settings=settings)
```

### CLI
Qlient also provides a CLI for inspecting a schema.
```shell script
qlient --inspect "https://countries.trevorblades.com/"

# or short:
# qlient -i "https://countries.trevorblades.com/"
```

## Authors
* **Daniel Seifert** - *Initial work* - [Lab9](https://github.com/Lab9)

## Acknowledgments
* Heavily inspired by [Zeep](https://github.com/mvantellingen/python-zeep)
