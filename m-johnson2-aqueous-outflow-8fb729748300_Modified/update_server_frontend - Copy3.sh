#!/bin/bash
HOST=aqueousoutflow.ads.northwestern.edu
ssh -t rsf895@$HOST '
sudo useradd -c "Pred S. Bundalo" -G wheel -m -s /usr/bin/bash psb996