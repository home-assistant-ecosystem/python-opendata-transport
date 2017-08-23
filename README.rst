python-opendata-transport
=========================

Python API for interacting with `transport.opendata.ch <http://transport.opendata.ch/>`_.

Installation
------------
The module is available from the `Python Package Index <https://pypi.python.org/pypi>`_.

.. code:: bash

    $ pip3 install python_opendata_transport

Usage
-----

The file ``example.py`` contains a similar example.

.. code:: bash

    >>> from opendata_transport import OpendataTransport
    >>> data = OpendataTransport('Bern', 'Biel')
    >>> data.get_data()
    >>> print(data.connections)

Development
-----------
For development is recommanded to use a ``venv``.

.. code:: bash

    $ python3.6 -m venv
    $ source bin/activate
    $ python3 setup.py develop

License
-------
``python-opendata-transport`` is licensed under MIT, for more details check LICENSE.
