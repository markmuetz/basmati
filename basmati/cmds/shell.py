"""Launches IPython shell"""
ARGS = [(['--failsafe'], {'action': 'store_true'})]
RUN_OUTSIDE_PROJECT = True


def main(cmd_ctx, args):
    import IPython
    import os
    import datetime as dt

    if not args.failsafe:
        # Load up useful modules
        import numpy as np

        import iris

        import basmati
        from basmati.basmati_errors import BasmatiError
        from basmati.hydrobasins import load_hydrobasins_geodataframe

        project = cmd_ctx.project

        modules = [os, dt, np, iris]
        try:
            import matplotlib.pyplot as plt
            modules.append(plt)
        except ImportError:
            pass
        for module in modules:
            print('Loaded module: {}'.format(module.__name__))
        print('Loaded module: basmati')

        for cls in [BasmatiError]:
            print('Loaded class: {}'.format(cls.__name__))

    # IPython.start_ipython(argv=[])
    # This is better because it allows you to access e.g. args, config.
    IPython.embed()
