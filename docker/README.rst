Building the fusion-index Docker container
==========================================

fusion-index is built off of the standard fusionapp/base container.

Build process
-------------

1. Pull the base container.

   .. code-block:: shell-session

      $ docker pull fusionapp/base

2. Run the base container to build the necessary wheels.

   .. code-block:: shell-session

      $ docker run --rm --interactive --volume=${PWD}:/application --volume=${PWD}/wheelhouse:/wheelhouse fusionapp/base

   The built wheels will be placed in the "wheelhouse" directory at the root
   of the repository.

3. Build the fusion-index container.

   .. code-block:: shell-session

      $ docker build --tag=fusionapp/fusion-index --file=docker/fusion-index.docker .
