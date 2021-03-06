#!/usr/bin/env python
#
# Author: Thamme Gowda [tg (at) isi (dot) edu] 
# Created: 2019-05-25

# This tool is useful for forking an experiment

import argparse
import os
from typing import Union, List
from rtg import log, TranslationExperiment as Experiment
from pathlib import Path
from rtg.utils import IO


def fork_experiment(from_exp: Path, to_exps: Union[Path, List[Path]], conf: bool, vocab: bool, data: bool, code: bool):
    assert from_exp.exists()
    if not isinstance(to_exps, list):
        to_exps = [to_exps]
    _from_exp = None
    for to_exp in to_exps:
        log.info(f'Fork: {str(from_exp)} → {str(to_exp)}')
        if not to_exp.exists():
            log.info(f"Create dir {str(to_exp)}")
            to_exp.mkdir(parents=True)
        if conf:
            conf_file = to_exp / 'conf.yml'
            IO.maybe_backup(conf_file)
            IO.copy_file(from_exp / 'conf.yml', conf_file)
        if data:
            to_data_dir = (to_exp / 'data')
            from_data_dir = from_exp / 'data'
            if to_data_dir.is_symlink():
                log.info(f"removing the existing data link: {to_data_dir.resolve()}")
                to_data_dir.unlink()
            assert not to_data_dir.exists()
            assert from_data_dir.exists()
            # relative paths for portability; copying dirs to new machine should work
            from_data_dir_rel = os.path.relpath(from_data_dir.absolute(), to_data_dir.parent)
            log.info(f"link {to_data_dir} → {from_data_dir} [{from_data_dir_rel}]")
            to_data_dir.symlink_to(from_data_dir_rel)
            (to_exp / '_PREPARED').touch(exist_ok=True)
        if not data and vocab:  # just the vocab
            if not _from_exp:
                _from_exp = Experiment(from_exp, read_only=True)
            _from_exp.copy_vocabs(Experiment(to_exp, read_only=True))

        if code:
            for f in ['rtg.zip', 'githead']:
                src = from_exp / f
                if not src.exists():
                    log.warning(f"File Not Found: {src}")
                    continue
                IO.copy_file(src, to_exp / f)


def add_on_off_conf(parser, name:str, help, dest=None, default=True):
    dest =  dest or name.replace('-', '_')
    group = parser.add_mutually_exclusive_group()
    group.add_argument(f'--{name}', dest=dest, action='store_true', help=help, default=default)
    group.add_argument(f'--no-{name}', dest=dest, action='store_false',
                       help=f'Negation of --{name}', default=not default)


def main():
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                description="fork an experiment.")
    p.add_argument('from_exp', metavar='EXP_DIR', type=Path,
                   help="From experiment. Should be valid experiment dir")
    p.add_argument('to_exps',  metavar='TO_DIR', type=Path, nargs='+',
                   help="To experiment(s). These will be created.")
    add_on_off_conf(p, 'conf', help='Copy config: from/conf.yml → to/conf.yml', default=True)
    add_on_off_conf(p, 'data', help='Link data dir . This includes vocab.', default=True)
    add_on_off_conf(p, 'vocab', help='copy vocabularies. dont use it with --data', default=False)
    add_on_off_conf(p, 'code', help='copy source code.', default=True)
    args = vars(p.parse_args())
    clones = args['to_exps']
    fork_experiment(**args)


if __name__ == '__main__':
    main()

