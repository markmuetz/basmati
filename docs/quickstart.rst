.. _quickstart:

Quickstart
==========

``basmati`` works as a command-line tool, and as a Python package. First, you will need to get some HydroBASINS data. This will get the data needed for the demonstration:

.. code-block:: bash

    export HYDROSHEDS_DIR=$HOME/HydroSHEDS
    # Download all datasets for Asia (as)
    basmati download --dataset ALL -r as

The demonstration can then be run:

.. code-block:: bash
    
    mkdir basmati_demo
    cd basmati_demo
    basmati demo

This will put some demonstration figures into a directory: ``basmati_demo_figs``.
