---
title: Caching Layers, From Browser to Database
date: 2026-09-15
tags: [caching, performance, distributed-systems]
cover: assets/cache-layers.svg
summary: A dummy walkthrough of where caches live, how reads fall through them, and how entries get invalidated — with images and Mermaid diagrams.
---

![Four stacked cache layers: browser, CDN, application cache, database](assets/cache-layers.svg)

## Why stack caches?

Every layer between the user and the database is a chance to answer a request
without doing the expensive work. The closer to the user a hit happens, the
cheaper and faster it is — but the harder it is to invalidate.

## Latency by layer

Rough, made-up numbers for a single read that hits each layer:

![Bar chart: browser 2 ms, CDN 6 ms, app cache 38 ms, database 180 ms](assets/latency-by-layer.png)

| Layer | Typical hit latency | Invalidation |
| --- | --- | --- |
| Browser | ~2 ms | `Cache-Control`, versioned URLs |
| CDN | ~6 ms | Purge API, surrogate keys |
| App cache (Redis) | ~38 ms | Explicit delete, TTL |
| Database | ~180 ms | — (source of truth) |

## The read path

A cache-aside read checks the cache first and only falls through to the
database on a miss:

```mermaid
flowchart TD
    R[Request] --> C{In cache?}
    C -- Hit --> H[Return cached value]
    C -- Miss --> D[Query database]
    D --> W[Write value to cache with TTL]
    W --> H
```

## The write path

Writes go to the database first, then invalidate the cache so the next read
repopulates it:

```mermaid
sequenceDiagram
    participant App
    participant DB as Database
    participant Cache

    App->>DB: UPDATE product SET price = 42
    DB-->>App: ok
    App->>Cache: DEL product:17
    Cache-->>App: ok
    Note over App,Cache: next read misses and reloads from DB
```

## Lifecycle of a cache entry

```mermaid
stateDiagram-v2
    [*] --> Missing
    Missing --> Fresh: read miss, load from DB
    Fresh --> Stale: TTL expires
    Fresh --> Missing: explicit invalidation
    Stale --> Fresh: background refresh
    Stale --> Missing: evicted under memory pressure
```

## Wrapping up

Cache as close to the user as the data's freshness requirements allow, and
decide how each layer is invalidated before you add it — not after the first
stale-price bug report.
