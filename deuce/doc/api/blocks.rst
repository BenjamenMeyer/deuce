================
Deuce Blocks API
================

----
v1.0
----

The Deuce Blocks API is split into two groups: Blocks Collection, and Blocks Item.


Blocks Collections
==================

Blocks Collection URL: ``/vaults/{vault id}/blocks``

The Blocks Collection group supports the HTTP POST and GET verbs.

POST
----

The POST verb provides support to upload multiple blocks at the same-time using the MSG Pack format.
The MSG Pack data contains information encoded in a key-value pair consisting of the Block ID as the
key and the Block Data as the value.

Moreover, the POST verb supports streaming data so that an large data set can be quickly provided in
a memory efficient manner.

On success, the POST verb will return 201 on success. Any information regarding the uploaded blocks
will have to be determined via a HEAD on the specific Block ID.

GET
---

The GET verb provides a listing of all the blocks in the Deuce Vault and supports Marker/Limit
semantics. If there are more blocks in the listing than were returned, then the X-Next-Batch header
will be provided with a full URL to the next set of listing data.

Blocks Items
============

Blocks Item URL: ``/vaults/{vault id}/blocks/{block id}``

HEAD
----

PUT
---

GET
---

DELETE
-------
