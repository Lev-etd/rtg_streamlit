apt install wget
pip install flask
pip install rtg==0.6.1
pip install streamlit
pip install streamlit-aggrid==0.2.3.post2
pip install seaborn==0.11.2
wget http://rtg.isi.edu/many-eng/models/rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05.tgz
tar xvf rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05.tgz
cp conf.yml -fr rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05/conf.yml
