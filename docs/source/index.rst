.. My API documentation master file, created by
   sphinx-quickstart on Fri Jun 27 22:12:41 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

My API documentation
====================

Add your content using ``reStructuredText`` syntax. See the
`reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
documentation for details.


.. toctree::
   :maxdepth: 2
   :caption: Contents:


REST API Main
=============

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:

REST API Authorization
======================

.. automodule:: src.auth.auth
   :members:
   :undoc-members:
   :show-inheritance:

REST API Database
=================

.. automodule:: src.databases.connect
   :members:
   :undoc-members:
   :show-inheritance:

REST API Repository
===================

.. automodule:: src.repository.crud
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

REST API Routes
===============

.. automodule:: src.routes.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.routes.contacts
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.routes.users
   :members:
   :undoc-members:
   :show-inheritance:

REST API Services
=================

.. automodule:: src.services.email_token
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.services.email
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: src.services.update_avatar
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
