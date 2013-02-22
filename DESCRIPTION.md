Ambient Intelligence Laboratory
===============================

Ambient Intelligence Laboratory (AmI-Lab) is the first Ambient Intelligence lab
in Romania, generously hosted by the Politehnica University of Bucharest,
in the Faculty of Automatic Control and Computer Science (http://acs.pub.ro).
Development is also backed by ARIA (Asociatia Romana pt. Inteligenta Artificiala,
http://aria-romania.org).

Our purpose is to create a distributed, multi-modal tracking system that will
automatically detect whether an elder has fallen down, be it day or night.
In order to achieve this, we are using a number of sensors and equipment:
  * 9 Microsoft Kinects, from which we are pulling data using OpenNI/Nite
      under Linux
  * 20 Arduinos equipped with distance, humidity, temperature, light sensors and
      microphone, from which we will be pulling data over an HTTP connection
      over WiFi (they also have WiFly shields)
  * 14 computers for crunching this data in real-time
      * 7 data crunching machines (face recognition, face cropping, distributed
            queue system, MongoDB database)
      * 5 data acquisition machines (temporarily only pulling data from 5
              Kinects)
      * 1 admin machine for monitoring the status of the cluster (running
              Nagios for monitoring) and provisioning it with the required
              software (we''re using Chef)
      * 1 public IP machine, in Amazon''s EC2 cloud, for managing the DNS, VPN
              and other services of the cluster

The software platform for operating this cluster is right in this github
repository. The flow of processing the data is currently the following:
  * data is fetched using an OpenNI/Nite program written in C++, on the
      data acquisition machines (the data acquisition process can be scaled
      horizontally)
  * data is enqueued to the ''measurements'' queue, backed by Kestrel. Kestrel
      is a distributed queue system we''re using for communication between the
      modules of our system. This allows us to write modules in any language that
      can do network programming (e.g. interact with Kestrel via sockets)
  * data is then fetched from the measurements queue by the Router module,
      which is the first PDU (Processing Data Unit). Data is then forwarded
      to a graph of PDUs which communicate using Kestrel queues. These PDUs
      can only be scaled vertically (in order to ensure strict ordering
      constraints) and they perform head cropping, face recognition, room
      management, air conditioning management, etc.
  * data is also saved to a MongoDB database, which only keeps the latest 1 day
       of data (by using Mongo''s TTL collections). This will allow us to
       perform statistical queries on the data when we need to. This MongoDB
       database is also polled by a client-side Javascript dashboard which
       displays the latest data from each sensor.

What are our future plans?
==========================
   * integrate the Arduinos and perform multi-modal localization of the person(s)
           inside
   * integrate a posture recognition algorithm, that in conjunction with the
           skeleton data from the Kinects can tell us more about the posture of
           the tracked person(S)
   * integrate a sound recognition algorithm, especially for fall/glass break
           detection

Team (in the order of coming on-board):
=======================================
    * Andrei Ismail (iandrei _at_ gmail.com) - PhD student - project leader
    * Liviu Vladutu (liviu.vladutu _at_ gmail.com) - PostDoc student - posture recognition
    * Diana Tatu (diana.tatu _at_ gmail.com) - MSc student - processing pipeline
    * Alin Lacea (alin.lacea _at_ aza.ro) - MSc student - infrastructure
    * Cosmin Marian (cosmin1611 _at_ gmail.com) - PhD student - person localization
