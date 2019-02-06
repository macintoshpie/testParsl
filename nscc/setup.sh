#!/usr/bin/env bash
module load anaconda/3
conda create --name parsl_py36 python=3.6
source activate parsl_py36

# NOTE: on ASPIRE 1, it is necessary to force compilation of the zmq bindings.
# First, make sure that all versions of pyzmq are removed from the path.
pip install --no-binary pyzmq pyzmq

# install parsl
# python3 -m pip install parsl
# FIX: using my branch of parsl b/c default timeouts for commands are too short
cd ~
git clone -b refactor/torque https://github.com/macintoshpie/parsl.git
pip install -e parsl/
