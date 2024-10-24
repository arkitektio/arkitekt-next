# arkitekt_next

[![codecov](https://codecov.io/gh/jhnnsrs/arkitekt_next/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/arkitekt_next)
[![PyPI version](https://badge.fury.io/py/arkitekt_next.svg)](https://pypi.org/project/arkitekt_next/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/arkitekt_next/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/arkitekt_next.svg)](https://pypi.python.org/pypi/arkitekt_next/)
[![PyPI status](https://img.shields.io/pypi/status/arkitekt_next.svg)](https://pypi.python.org/pypi/arkitekt_next/)

streaming analysis for mikroscopy

## Idea

arkitekt_next is the python client for the arkitekt_next platform. It allows you to utilize the full extent of the platform from your python code.
To understand the idea behind arkitekt_next, you need to understand the idea behind the arkitekt_next platform.
(More on this in the [documentation](https://arkitekt.live))

## Features

- Host your python functions and make them to your team
- Use functions from your team in your code
- Interact with and store data in a secure and scalable way on the platform
- Use the platform as a central storage for your data

## Install

```bash
pip install arkitekt-next[all]
```

This installs all dependencies for the arkitekt_next platform, inlcuding the arkitekt_next CLI, which can be used to develop and create apps, containerize them and deploy t

arkitekt_next is relying heavily on asyncio patters and therfore supports python 3.8 and above. It also relies on the pydantic stack for serialization.

## App

You can use the cli to create python based apps for the arkitekt_next platform, profiting from a battery of features like easy GUI creation based on
type annotations, orchestration of real-time (in memoery) workflows, data hosting, easy packaging and distribution in docker containers, etc...

To get started create a directory and run

```bash
arkitekt-next init
```

Which will lead you throught an app creation process.
Apps can simply registered functions, through the register decorator

```python
from arkitekt_next import register

@register()
def rpc_function(x: int, name: str) -> str
    """
    A rpc function that we can
    simple call from anywhere

    ""

```

And then connected to a local or remote server by running

Run example:

```bash
arkitekt-next run dev
```

For more details on how to create an app follow the tutorials on https://arkitekt.live.

## Usage with complex Datastructures

ArkitektNext takes care of serialization and documentation of standard python datastructures

- str
- bool
- int
- float
- Enum
- Dict
- List

To increase performance and reduce latency it is not possible to serialize complex python objects like numpy arrays into the messages. These are best transformed into immutable objects on a centrally accessible storage and then only the reference is passed.

ArkitektNext does not impose any rules on how you handle this storage (see mikro for ideas), it provides however a simple api.

```python

class ComplexStructure:
    id: str # A reference for this structure on central storage

    async def shrink(self):
        return self.id

    @classmethod
    async def expand(cls, value):
        return cls.load_from_server(value)


```

by providing two functions:

- shrink
- expand

You can now use this Structure with simple typehints and arkitekt_next will automaticall shrink (serialize) and expand (deserialize) the structure on calling.

```python

def complex_call(x: ComplexStrucuture) -> int:
    return x.max()

```

Check out the arkitekt_next [documentation](https://arkitekt.live) for usage of this libary
