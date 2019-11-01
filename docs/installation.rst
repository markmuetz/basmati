.. _installation:

Installation
============

The recommended way to intall ``basmati`` is using `Anaconda <https://www.anaconda.com/distribution/>`_. ``basmati`` only works with ``python3.6`` or higher.

Clone basmati repository
------------------------

.. code-block:: bash

    git clone https://github.com/markmuetz/basmati.git
    cd basmati

Create conda env and install basmati
------------------------------------

Install all the dependencies into a new conda environment. Activate the environment, then install ``basmati`` into the environment.

.. code-block:: bash

    conda env create -f envs/basmati_env.yml
    conda activate basmati_env
    pip install -e .

Check it has worked
-------------------

.. code-block:: bash

    basmati version

::

    >>> import basmati
    >>> print(basmati.__version__)

See the :ref:`quickstart` guide for what to try next.
