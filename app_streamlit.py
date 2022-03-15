import os
import sys
import platform
import streamlit as st

import pandas as pd
import rtg
import torch

from io import BytesIO

import seaborn as sns
import matplotlib
from matplotlib.figure import Figure

from rtg import TranslationExperiment as Experiment, log
from rtg.module.decoder import Decoder
from rtg.utils import max_RSS
from st_aggrid import AgGrid

torch.set_grad_enabled(False)
FLOAT_POINTS = 4

root = os.getcwd()

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
# exp = Experiment(f'{root}/rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05', read_only=True)
# dec_args = exp.config.get("decoder") or exp.config["tester"].get("decoder", {})
# decoder = Decoder.new(exp, ensemble=dec_args.pop("ensemble", 1))
# src_prep = exp.get_pre_transform(side='src')
# tgt_prep = exp.get_pre_transform(side='tgt')
# tgt_postp = exp.get_post_transform(side='tgt')
list_of_languages = pd.read_csv('list_of_available_languages')
metrics = pd.read_csv('metrics', index_col='Unnamed: 0')

st.set_page_config(page_title="Many to English Translation")

to_translate = st.text_input(label='Поле для перевода',
                             help='Введите текст на любом языке, чтобы получить перевод на английский')

if st.button('Перевести'):
    if isinstance(to_translate, str):
        sources = [to_translate]
    if sources is None:
        st.text("Введите запрос")
    sources = [src_prep(sent) for sent in sources]
    translations = []
    # for source in sources:
    #     translated = decoder.decode_sentence(source, **dec_args)[0][1]
    #     translated = tgt_postp(translated)
    #     translations.append(translated)
    #
    # res = dict(source=sources, translation=translations)
    # st.write(translations[0])

# with st.expander("Статистика по набору данных, использованному в обучении модели"):
AgGrid(list_of_languages)

col1, col2 = st.columns(2)
with col1:
    fig = Figure(figsize=(6, 4.5))
    ax = fig.subplots()
    sns.barplot(x=metrics.index, y=metrics['BRE-ENG'], ax=ax)
    ax.set_title('Качество обучения на паре языков Breton-English')
    ax.set_ylabel('BLEU score')
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    st.image(buf)
with col2:
    fig = Figure(figsize=(6, 4.5))
    ax = fig.subplots()
    sns.barplot(x=metrics.index, y=metrics['SME-ENG'], ax=ax)
    ax.set_title('Качество обучения на паре языков  Northern Sami-English ')
    # ax.set_xlabel()
    ax.set_ylabel('BLEU score')
    fig.tight_layout()
    buf_1 = BytesIO()
    fig.savefig(buf_1, format="png")
    st.image(buf_1)
# st.write(fig)
