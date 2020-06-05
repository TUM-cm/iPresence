# Setup light nodes
sudo -s
pip install paho-mqtt
apt-get install python-scipy
pip install jellyfish
pip install dill
pip install pycrypto
apt-get install cython
pip install cython

python -m receive_light.light_control
python -m send_light.test_light
