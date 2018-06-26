===========================
Indexing service for Fusion
===========================

Quick start
-----------

Install the software:

.. code-block:: shell

   $ pip install fusion-index

Run the software:

.. code-block:: shell

   # Create a directory for deployment artefacts.
   $ mkdir -p ~/deployment/fusion-index
   $ cd ~/deployment/fusion-index
   
   # Start the service on port 8090.
   $ twistd --pidfile '' -n fusion-index -p tcp:8090
