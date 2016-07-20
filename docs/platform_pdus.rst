.. How to setup a PDU (Processing Data Unit) within AmI-Platform

How to Create a PDU from Scratch
================================

Purpose of This Document
------------------------

The purpose is two-fold:
* to describe how the existing Python PDU system works
* to give tips and tricks on how to create PDUs in a new language that
interacts with the existing queue system

Definition of a PDU
-------------------

A PDU is a **processing data unit**, a part of a distributed system that
processes data in real-time from the existing laboratory sensors. These PDUs
form a directed graph through which messages flow. A message is basically an
event of the system, and can represent anything:
* a new measurement has been produced by a sensor
* a new event has appeared (e.g. door has been opened)

Why do you Need to Create PDUs?
-------------------------------

One wants to create PDUs in order to add new functionality to the existing
platform. Examples of PDUs:
* PDU that detects the faces in a given image (by using an API)
* PDU that detects the posture of a skeleton by running a classifier

Format of the Messages Between PDUs
-----------------------------------

It's nothing more than free-style JSON, serialized to a string.
In Python, we do that by the `json.dumps` command::

    import json

    msg = {'a': {'deeply': 'nested'}, 'dictionary': 'message'}
    serialized_msg = json.dumps(msg)


Other than that, the formats of the messages should be traced back to the
initial chain of PDUs that process them. Because the PDUs form a directed
graph, a message or piece of information is usually processed through a chain
of PDUs. The initial message might not be preserved, but it triggers a multitude
of other messages to be processed by other PDUs. For example:
* a picture gets produced by the PDU which polls the Kinects for images
* the picture gets picked up by Router and forwarded to other types of PDUs
* `mongo_writer` writes the image in MongoDB
* `head_crop` tries to detect faces in that image
and so on.

It's pretty clear that the message forwarded from Router to HeadCrop differs in
format from the message that was initially received by Router, but that is the
spirit of the graph computation.

Skeleton of a PDU
-----------------

A PDU has basically the following responsibilities:
* connect to `Kestrel <https://github.com/twitter/kestrel>`_ to the queue where it 
expects to receive its messages
* read the message from Kestrel and decode it to a dictionary
* process the message and put some other messages on other queues if needed

In pseudocode-Python, the skeleton would look something like this::

    kestrel_connection = connect_to_kestrel(hostname, port)

    # Basically a PDU runs forever. You can kill the process and restart it
    # if you want to update the code.
    while True
        # The reading of a message from Kestrel is provided by the Kestrel lient
        # library. Depending on your chosen message, google for a Kestrel client
        # library. If no good library is available, feel free to choose a Memcache
        # client library instead (read below for details)
        serialized_msg = read_message_from_kestrel(kestrel_connection)

        # In Python this is equivalent to json.loads
        msg = deserialize_msg(serialized_msg)

        # This is the actual processing of the message.
        # Do whatever you need to do in here: detect images, classify postures, etc.
        # One key point of this will be to put messages on other queues, if needed.
        process_message(msg)


Duality of Kestrel and Memcache
-------------------------------

Kestrel is a queue system with the following basic operations (well, not only
these, but these are the ones useful to us): put a message on a queue, retrieve
a message from that queue.

As a TCP-level communication protocol, it uses the same protocol as memcached,
for several reasons:
* it's rich enough semantically-wise
* there are a bunch of libraries already available to interact with memcached

For example, in our C++ Kinect acquisition code, we use the "libmemcached"
library, in order to write the images pulled from the Kinect to the Router
PDU which is written in Java.

Sample code we use to write to the queue from C++::

    #include <libmemcached/memcached.h>
    memcached_st* g_MemCache;
    memcached_return rc;

    g_MemCache = memcached_create(NULL);
    memcached_server_st* servers = NULL;
    memcached_return rc;

    servers = memcached_server_list_append(servers, getKestrelServerIP(), getKestrelServerPort(), &rc);
    memcached_server_push(g_MemCache, servers);

    // buffer is a string containing a serialized JSON
    // In this case, we write to the "measurements queue"
    size_t len = strlen(buffer);
    rc = memcached_set(g_MemCache,
            "measurements", strlen("measurements"),
            buffer, len,
            (time_t)0, (uint32_t)0);


The beauty of this approach is that we can have any process from any language
communicate with another process from another language. In our case, we used
that to our benefit because Python support for Kinect was very poor, while C++
support was very strong.

Properties of a PDU
-------------------

1. A PDU runs forever
2. A PDU reads from a Kestrel queue serialized messages (serialized JSON)
   My recommendation here would be to insert a small sleep between two attempts
   to read the message in order not to bring the CPU usage to 100%.
3. A PDU processes the message received and possibly writes messages to other
   queues
4. A PDU uses either a Kestrel client library or a Memcache client library in
   order to communicate with the Kestrel server

Conclusions
-----------

Writing a PDU is very easy once you understand the basic skeleton available in
the Python pseudo-code above. It should be less than 50 lines of code in any
language to prototype one.

In fact, it's very similar to any program that you've ever written that
connects to a socket and receives messages from that socket. Only that in this
case, it does not use the low-level socket API, but a library that speaks the
proper protocol.
