===========================
Indexing service for Fusion
===========================

Quick start
-----------

Checkout a clone of the `fusion-index` repository and install it:

.. code-block:: shell

   $ cd path/to/fusion-index/checkout 
   $ pip install -r requirements.txt
   # It's recommended to install with `-e` to avoid having to constantly
   # reinstall when changing branches or making changes.
   $ pip install -e .

Run the software:

.. code-block:: shell

   # Create a directory for deployment artefacts.
   $ mkdir -p ~/deployment/fusion-index
   $ cd ~/deployment/fusion-index
   
   # Start the service on port 8090.
   $ twistd --pidfile '' -n fusion-index -p tcp:8090
