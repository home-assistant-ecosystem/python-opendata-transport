python-opendata-transport
=========================

A Python client for interacting with `transport.opendata.ch <http://transport.opendata.ch/>`_.

This module is the base for the integration into `Home Assistant <https://home-assistant.io>`_
and is simply retrieving the details about a given connection between two stations.

This module is not official, developed, supported or endorsed by opendata.ch.

Installation
------------

The module is available from the `Python Package Index <https://pypi.python.org/pypi>`_.

.. code:: bash

    $ pip3 install python_opendata_transport

On a Fedora-based system or on a CentOS/RHEL 8 machine with has EPEL enabled.

.. code:: bash

    $ sudo dnf -y install python3-opendata-transport

For Nix or NixOS users is a package available. Keep in mind that the lastest releases might only
be present in the ``unstable`` channel.

.. code:: bash

    $ nix-env -iA nixos.python39Packages.python-opendata-transport

Usage
-----

The file ``example.py`` contains an example about how to use this module.

Development
-----------

For development is recommended to use a ``venv``.

.. code:: bash

    $ python3 -m venv .
    $ source bin/activate
    $ python3 setup.py develop

License
-------

``python-opendata-transport`` is licensed under MIT, for more details check LICENSE.
