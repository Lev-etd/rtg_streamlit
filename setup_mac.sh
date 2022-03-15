pip3 install wget
pip3 install flask
pip3 install rtg==0.6.1
pip3 install streamlit
pip3 install streamlit-aggrid==0.2.3.post2
pip3 install seaborn==0.11.2
wget http://rtg.isi.edu/many-eng/models/rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05.tgz
tar xvf rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05.tgz
mv conf.yml -f rtg500eng-tfm9L6L768d-bsz720k-stp200k-ens05/conf.yml