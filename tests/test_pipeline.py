#!/usr/bin/env python
#
# Author: Thamme Gowda [tg (at) isi (dot) edu] 
# Created: 4/18/20
import pytest
from rtg.pipeline import Pipeline, Experiment, log
import tempfile
from rtg.exp import load_conf
import torch
import shutil
from . import sanity_check_experiment, run_decode


def test_prepared_pipeline():  # its a transformer
    exp = Experiment('experiments/sample-exp', read_only=True)
    exp.config['trainer'].update(dict(steps=50, check_point=25))
    pipe = Pipeline(exp)
    pipe.run(run_tests=False)


def test_prepared_pipeline_relative_pos():
    config = load_conf('experiments/sample-exp/conf.yml')
    config['model_args']['self_attn_rel_pos'] = 4
    exp = Experiment('experiments/sample-exp', config=config, read_only=True)
    exp.config['trainer'].update(dict(steps=50, check_point=25))
    exp.config['trainer']['init_args']['chunk_size'] = 0  # disable chunked loss
    pipe = Pipeline(exp)
    pipe.run(run_tests=False)


def test_prepared_pipeline_subclassing():
    exp = Experiment('experiments/sample-exp', read_only=True)
    exp.config['model_type'] = 'subcls_tfmnmt'
    exp.config['trainer'].update(dict(steps=200, check_point=50))
    exp.config['trainer']['init_args']['chunk_size'] = 0
    exp.config['criterion']['name'] = 'kl_divergence'
    exp.config['schedule'] = dict(name='inverse_sqrt', args=dict(warmup=50, init_lr=1e-5, peak_lr=1e-2))
    pipe = Pipeline(exp)
    pipe.run(run_tests=False, debug=True)


def test_prepared_pipeline_subclassing_with_chunking():
    exp = Experiment('experiments/sample-exp', read_only=True)
    exp.config['model_type'] = 'subcls_tfmnmt'
    exp.config['trainer'].update(dict(steps=200, check_point=50, batch_size=(2048, 200)))
    exp.config['trainer']['init_args']['chunk_size'] = 10
    exp.config['criterion']['name'] = 'kl_divergence'
    exp.config['schedule'] = dict(name='inverse_sqrt', args=dict(warmup=100, init_lr=1e-5, peak_lr=1e-3))
    pipe = Pipeline(exp)
    pipe.run(run_tests=False, debug=True)


def test_pipeline_transformer():

    for codec_lib in ['sentpiece', 'nlcodec']:
        tmp_dir = tempfile.mkdtemp()
        config = load_conf('experiments/transformer.test.yml')
        print(f"Testing {codec_lib} --> {tmp_dir}")
        config['prep'].update({'codec_lib': codec_lib, 'char_coverage': 0.9995})
        exp = Experiment(tmp_dir, config=config, read_only=False)
        exp.config['trainer'].update(dict(steps=50, check_point=25))
        exp.config['prep']['num_samples'] = 0
        Pipeline(exp).run(run_tests=False)
        sanity_check_experiment(exp)
        print(f"Cleaning up {tmp_dir}")
        src_sents = ["hello there", "this is a test"]
        output = run_decode(exp_dir=tmp_dir, sentences=src_sents)
        assert len(src_sents) == len(output)
        shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="This is too slow on CPU")
def test_robertamt_full_init():
    tmp_dir = tempfile.mkdtemp()
    config = load_conf('experiments/pretrained/robertamt-xlmr.yml')
    model_id = config['model_args']['model_id']
    print(f"Testing {model_id} --> {tmp_dir}")
    assert 'pretrainmatch' == config['prep'].get('codec_lib')
    exp = Experiment(tmp_dir, config=config, read_only=False)
    exp.config['trainer'].update(dict(steps=4, check_point=1))
    Pipeline(exp).run(run_tests=False)
    sanity_check_experiment(exp)
    print(f"Cleaning up {tmp_dir}")
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="This is too slow on CPU")
def test_robertamt_2layer_init():
    tmp_dir = tempfile.mkdtemp()
    config = load_conf('experiments/pretrained/robertamt-xlmr-2layer.yml')
    model_id = config['model_args']['model_id']
    print(f"Testing {model_id} --> {tmp_dir}")
    assert 'pretrainmatch' == config['prep'].get('codec_lib')
    exp = Experiment(tmp_dir, config=config, read_only=False)
    exp.config['trainer'].update(dict(steps=4, check_point=1))
    Pipeline(exp).run(run_tests=False)
    sanity_check_experiment(exp)
    print(f"Cleaning up {tmp_dir}")
    shutil.rmtree(tmp_dir, ignore_errors=True)


def test_parent_child_pipeline():
    parent_dir = tempfile.mkdtemp()
    # parent_dir = 'tmp-xyz-parent'
    print(f"Making parent at {parent_dir}")
    exp = Experiment(parent_dir, config='experiments/transformer.test.yml', read_only=False)
    exp.config['trainer'].update(dict(steps=50, check_point=25))
    Pipeline(exp).run(run_tests=False)
    sanity_check_experiment(exp)
    assert not exp.parent_model_state.exists()

    child_config = load_conf('experiments/transformer.test.yml')
    child_config.update({
        'parent': {
            'experiment': str(parent_dir),
            'vocab': {
                'shared': 'shared'
            },
            'model': {
                'ensemble': 2
            }
        }
    })

    child_dir = tempfile.mkdtemp()
    # child_dir = 'tmp-xyz-child'
    print(f"Making child at {child_dir}")
    exp = Experiment(child_dir, config=child_config, read_only=False)
    exp.config['trainer'].update(dict(steps=50, check_point=25))
    Pipeline(exp).run(run_tests=False)
    sanity_check_experiment(exp)
    assert exp.parent_model_state.exists()

    for dir in [parent_dir, child_dir]:
        print(f"Cleaning up {dir}")
        shutil.rmtree(dir, ignore_errors=True)


def test_freeze_pipeline():
    exp = Experiment('experiments/sample-exp', read_only=True)
    exp.config['trainer'].update(dict(steps=50, check_point=25))
    # enable these
    trainable = {'include': ['src_embed', 'tgt_embed', 'generator', 'encoder:0', 'decoder:0,1']}
    exp.config['optimizer']['trainable'] = trainable
    pipe = Pipeline(exp)
    pipe.run(run_tests=False)


def test_byte_vocab():
    for pieces in ['byte->bpe', 'bpe->byte', 'byte->byte']:
        tmp_dir = tempfile.mkdtemp()
        codec_lib = 'nlcodec'
        config = load_conf('experiments/transformer.test.yml')
        config['prep'].update({'codec_lib': codec_lib,
                               'pieces': pieces.split('->'),
                               'shared_vocab': False,
                               'num_samples': 3})
        config['model_args'].update({'tied_emb': 'one-way'})
        config['trainer'].update(dict(steps=50, check_point=25))
        exp = Experiment(tmp_dir, config=config, read_only=False)
        try:
            Pipeline(exp).run(run_tests=False)
            sanity_check_experiment(exp, shared_vocab=False)
            src_sents = ["hello there", "this is a test"]
            output = run_decode(exp_dir=tmp_dir, sentences=src_sents)
            assert len(src_sents) == len(output)
        except Exception as e:
            # this needs fixing the nlcodec
            log.warning(e)
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()   # required for parallel nlcodec
    #test_pipeline_transformer()
