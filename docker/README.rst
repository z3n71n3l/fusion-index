Building the fusion-index Docker container
==========================================

There are three Docker containers defined: run.docker defines the actual
container used to run fusion-index, build.docker is used to build the wheels
required for the "run" container, and base.docker is used to define a base
container which is shared between the "build" and "run" containers as an
optimization.

Build process
-------------

1. Build the base container.

   .. code-block:: shell-session

      $ docker build --tag=fusionapp/fusion-index-base --file=docker/base.docker .

2. Build the build container.

   .. code-block:: shell-session

      $ docker build --tag=fusionapp/fusion-index-build --file=docker/build.docker .

3. Run the build container to build the necessary wheels.

   .. code-block:: shell-session

      $ docker run --rm --interactive --volume=${PWD}:/application --volume=${PWD}/wheelhouse:/wheelhouse fusionapp/fusion-index-build

   The built wheels will be placed in the "wheelhouse" directory at the root
   of the repository. This is necessary for building the final container.

4. Build the run container.

   .. code-block:: shell-session

      $ docker build --tag=fusionapp/fusion-index --file=docker/run.docker .

You only need to rerun steps 3 and 4 to build a container from modified source.
