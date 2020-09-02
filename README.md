# Graphy: Python GraphQL Client

A fast and modern graphql client library designed with simplicity in mind.

[![pypi][pypi-image]][pypi-url]
[![GitHub license][github-license-image]][github-license-url]
[![Wheel][pypi-wheel-image]][pypi-wheel-url]
[![Language][language-image]][language-url]


[pypi-image]: https://img.shields.io/pypi/v/python-graphy.svg?style=flat
[pypi-url]: https://pypi.python.org/pypi/python-graphy

[github-license-image]: https://img.shields.io/github/license/Lab9/python-graphy.svg
[github-license-url]: https://github.com/Lab9/python-graphy/blob/master/LICENSE

[pypi-wheel-image]: https://img.shields.io/pypi/wheel/python-graphy.svg
[pypi-wheel-url]: https://pypi.python.org/pypi/python-graphy

[language-image]: https://img.shields.io/badge/lang-python-green
[language-url]: https://www.python.org/

NOTE: THIS PACKAGE IS STILL UNDER DEVELOPMENT.

## Getting Started

### Installing

```shell script
pip install python-graphy
```

### Usage
This example shows a simple query
```python
from graphy import Client

client = Client("https://graphql-pokemon.now.sh/")

response = client.query.pokemon(select=["id", "name"], where={"name": "Pikachu"})
```

## Documentation
The Documentation covers the following points:
* [Query](#query)
* [Mutation](#mutation)
* [Subscription](#subscription)
* [Transporter](#transporter)
    * [PromiseTransporter](#promisetransporter)
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
from graphy import Client

client = Client("https://graphql-pokemon.now.sh/")

response = client.query.pokemons(select=["id", "name"], where={"first": 10})
```
Which will make a request to the server and return the id and name of the first 10 pokemons found in the pokedex.

But what if you want to make a more complex query with fields within fields?
Don't need to worry, we got you covered:
```python
from graphy import Client, fields

client = Client("https://graphql-pokemon.now.sh/")

response = client.query.pokemons(
    select=fields("id", "name", evolutions=fields("id", "name")), 
    where={"first": 10}
)
```
Using the fields method from `graphy` you can simply use `*args` and `**kwargs` for making deeper selections.
By the way, you could stack this like forever.

Last but not least, what if you don't know the fields you could select?
Yup, we got you somewhat covered as well. The thing is, that due to performance issues,
this package is not able to completely create a query that retrieves all fields for a Query.
I have set the max depth to **2** (Can be changed via [Settings](#settings)). This allows to still send a query without selecting any fields
but you won't get them all. If you want all, use the `fields` function defined above.

```python
from graphy import Client

client = Client("https://graphql-pokemon.now.sh/")

response = client.query.pokemons(where={"first": 10})

# this gives you a good amount of data back.
```

### Mutation
I haven't found a real world example for making mutations without being authenticated,
so here's a hypothetical one.
```python
from graphy import Client

client = Client("https://some-host.com/authentication")

response = client.mutation.register(data={"email": "foo@bar.com", "password": "987654321"})
```

### Subscription
Sometimes you want to execute things when something - an action - happened on the server.
In those cases, you can subscribe to an event.
For subscribing to an endpoint, I am using the asyncio `websockets` library.
So have a look at their [documentation](https://pypi.org/project/websockets/) for clarification.

Here is a basic example
```python
import asyncio
from graphy import Client

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
from graphy import Client

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

from graphy import Client, Transporter

my_session = requests.sessions.session()

my_session.headers["Authorization"] = "Bearer some-api-token"

client = Client("https://foo.bar/", transporter=Transporter(session=my_session))
```

#### PromiseTransporter

So why not create asynchronous transporters as well?
Making a request with the promise transporter returns a `Promise[Response]` with the response as a value.
Have a look at their [documentation](https://pypi.org/project/promise/).

```python
from graphy import Client, PromiseTransporter

client = Client("https://graphql-pokemon.now.sh/", transporter=PromiseTransporter())

client.query.pokemons(where={"first": 10}).done(lambda j: print(j), None)  # None represents the did_reject callback.
```

#### AsyncTransporter

And an AsyncTransporter:
```python
import asyncio

from graphy import Client, AsyncTransporter

client = Client("https://graphql-pokemon.now.sh/", transporter=AsyncTransporter())

async def request_data():
    return await client.query.pokemons(where={"first": 10})

asyncio.run(request_data())
```

### Settings
Most things can be adjusted using the settings.
When no settings are passed by to a client, the default values will be used instead

#### max_recursion_depth
The max_recursion_depth can be used for changing the max depth for deeper automatic selection lookup.
Default is 2.
```python
from graphy import Client, Settings

settings = Settings(max_recursion_depth=5)  # Due to performance reasons I do not recommend to go any higher than that.

client = Client("https://graphql-pokemon.now.sh/", settings=settings)
```

#### base_response_key
The base_response_key can be changed for setting the base key that is being used to get the data from the server.
Default is "data".
```python
from graphy import Client, Settings

settings = Settings(base_response_key="my_custom_data_key")

client = Client("https://graphql-pokemon.now.sh/", settings=settings)
```

#### base_payload_key
The base_payload_key can be changed for setting the base key that is being used to read the data from the websocket response.
Default is "payload".
```python
from graphy import Client, Settings

settings = Settings(base_payload_key="my_custom_payload_key")

client = Client("https://graphql-pokemon.now.sh/", settings=settings)
```

#### return_requests_response
The return_requests_response can be set to True if you want the whole request back instead of just the json.
Default is False.
```python
from graphy import Client, Settings

settings = Settings(return_requests_response=True)

client = Client("https://graphql-pokemon.now.sh/", settings=settings)
```

#### disable_selection_lookup
The disable_selection_lookup can be set to True if you want to disable the automatic selection lookup.
Default is False.
```python
from graphy import Client, Settings

settings = Settings(disable_selection_lookup=True)

client = Client("https://graphql-pokemon.now.sh/", settings=settings)
```

#### return_full_subscription_body
The return_full_subscription_body can be set to True if you want to get the full websocket response instead of only
the data.
```python
from graphy import Client, Settings

settings = Settings(return_full_subscription_body=True)

client = Client("https://graphql-pokemon.now.sh/", settings=settings)
```

### CLI
Graphy also provides a CLI for inspecting a schema.
```shell script
graphy --inspect "https://graphql-pokemon.now.sh/"

# or short:
# graphy -i "https://graphql-pokemon.now.sh/"
```

## Authors
* **Daniel Seifert** - *Initial work* - [Lab9](https://github.com/Lab9)

## Acknowledgments
* Heavily inspired by [Zeep](https://github.com/mvantellingen/python-zeep)
