#!/bin/bash
HOST=aqueousoutflow.ads.northwestern.edu
scp ./aq-ui-dist/backend/"$1" $HOST:/home/njf390/backend
ssh -t $HOST "
sudo scl enable rh-python36 bash
pip uninstall aq-backend
pip install /home/njf390/backend/$1
systemctl restart httpd24-httpd
exit
exit"