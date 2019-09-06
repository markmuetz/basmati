import argparse

try:
    import argcomplete
    use_argcomplete = True
except ImportError:
    use_argcomplete = False


def parse_commands(name, top_level_args, module, cmdline_args):
    # create the top-level parser.
    parser = argparse.ArgumentParser(prog=name)
    subparsers = parser.add_subparsers(dest='cmd_name')
    subparsers.required = True

    for top_level_pos_args, top_level_kwargs in top_level_args:
        parser.add_argument(*top_level_pos_args, **top_level_kwargs)

    cmds = module.modules
    for cmd_name, cmd_module in cmds.items():
        # create the subparser for each command.
        subparser = subparsers.add_parser(cmd_name,
                                          help=cmd_module.__doc__)
        for cmd_pos_args, cmd_kwargs in cmd_module.ARGS:
            subparser.add_argument(*cmd_pos_args, **cmd_kwargs)

    if use_argcomplete:
        argcomplete.autocomplete(parser)
    args = parser.parse_args(cmdline_args)

    return cmds, args
