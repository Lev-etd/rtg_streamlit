import logging
import os
import sys
import platform
import streamlit as st
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import numpy as np
import rtg
import torch

import flask
from flask import Flask, request, send_from_directory, Blueprint

from rtg import TranslationExperiment as Experiment, log
from rtg.module.decoder import Decoder
from rtg.utils import max_RSS

torch.set_grad_enabled(False)
FLOAT_POINTS = 4

root = os.getcwd()
# exp = None
# app = Flask(__name__)
# app.config['JSON_AS_ASCII'] = False

sys_info = {
    'RTG Version': rtg.__version__,
    'PyTorch Version': torch.__version__,
    'Python Version': sys.version,
    'Platform': platform.platform(),
    'Platform Version': platform.version(),
    'Processor': platform.processor(),
    'CPU Memory Used': max_RSS()[1],
    'GPU': '[unavailable]',
}
if torch.cuda.is_available():
    sys_info['GPU'] = str(torch.cuda.get_device_properties(rtg.device))
    sys_info['Cuda Version'] = torch.version.cuda
else:
    log.warning("CUDA unavailable")

log.info(f"System Info: ${sys_info}")

exp, src_prep, tgt_postp = None, None, None
# global exp, src_prep, tgt_postp
exp = Experiment(f'{root}/rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05', read_only=True)
dec_args = exp.config.get("decoder") or exp.config["tester"].get("decoder", {})
decoder = Decoder.new(exp, ensemble=dec_args.pop("ensemble", 1))
src_prep = exp.get_pre_transform(side='src')
tgt_prep = exp.get_pre_transform(side='tgt')
tgt_postp = exp.get_post_transform(side='tgt')

st.set_page_config(page_title="Many to English Translation")

to_translate = st.text_input(label='Поле для перевода')

if st.button('Перевести'):
    if isinstance(to_translate, str):
        sources = [to_translate]
    if sources is None:
        st.text("Введите запрос")
    sources = [src_prep(sent) for sent in sources]
    translations = []
    for source in sources:
        translated = decoder.decode_sentence(source, **dec_args)[0][1]
        translated = tgt_postp(translated)
        translations.append(translated)

    res = dict(source=sources, translation=translations)
    st.text(translations[0])