# iPresence
Co-Presence Reasoning using Visible Light and Sensor Data

For the PhD thesis "Edge-Driven Proximity Service Platform for the Internet of Things in Indoor Environments" of Michael Haus

This repository addresses the following question of the research problem:
How to determine the spatial proximity of users without disclosing their locations to enable user-oriented and privacy-aware services?
TODO add RQ3

We begin addressing this question by building LocalVLC, a system for VLC that we use as the building block for our further work.
We present the design and implementation of a 3D printed custom light bulb with a dedicated modulation scheme for VLC inspired
by Morse coding to eliminate the light flickering effect. The light bulb can be embedded as a regular light source into the
infrastructure and addresses the crucial challenge faced by conventional VLC designs: usability in practical deployment.

Furthermore, we present DevLoc, the design and implementation of a lighting configuration framework to integrate our
custom light bulbs into a network for communication and signaling. We can flexibly define different groups of light bulb(s)
where we adopted a master-slave principle to form semantic subnetworks to cover larger rooms or across multiple rooms.
As a result, we can control the spatial granularity of user proximity to overcome the main disadvantage of location tags:
where users have no control over the spatial granularity of proximity because the neighborhood is entirely dependent on the type of 
location tag.

TODO add services