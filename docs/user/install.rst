.. _install:

Installation
============

Install from PyPI
-----------------

python-libweb can be installed using pip3:

::

    pip3 install libweb

Or, if you're feeling adventurous, can be installed directly from
github:

::

    pip3 install git+https://github.com/HurricaneLabs/python-libweb.git


Source Code
-----------

libweb `lives on GitHub <https://github.com/hurricanelabs/python-libweb>`_, making the
code easy to browse, download, fork, etc. Pull requests are always welcome! Also,
please remember to star the project if it makes you happy.

Once you have cloned the repo or downloaded a tarball from GitHub, you
can install libweb like this:

.. code:: bash

    $ cd python-libweb
    $ pip3 install .

Or, if you want to edit the code, first fork the main repo, clone the fork
to your desktop, and then run the following to install it using symbolic
linking, so that when you change your code, the changes will be automagically
available to your app without having to reinstall the package:

.. code:: bash

    $ cd python-libweb
    $ pip install -e .

Did we mention we love pull requests? :)
