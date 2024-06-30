---
sidebar_label: default
title: apps.default
---

## ArkitektNext Objects

```python
class ArkitektNext(ConnectedApp)
```

ArkitektNext

An app that connected to the services of the arkitekt_next Api,
it comes included with the following services:

- Rekuest: A service for that handles requests to the arkitekt_next Api as well as provides an interface to provide functionality on the arkitekt_next Api.
- Herre: A service for that handles the authentication and authorization of the user
- Fakts: A service for that handles the discovery and retrieval of the configuration of the arkitekt_next Api
- Mikro: A service for that handles the storage and data of microscopy data

Apps have to be always used within a context manager, this is to ensure that the services are properly closed when the app is no longer needed.

**Example**:

  &gt;&gt;&gt; from arkitekt_next import ArkitektNext
  &gt;&gt;&gt; app = ArkitektNext()
  &gt;&gt;&gt; with app:
  &gt;&gt;&gt;     # Do stuff
  &gt;&gt;&gt; # App is closed

