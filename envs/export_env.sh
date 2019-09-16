#!/bin/bash
conda env export | grep -v "^prefix: " > basmti_env.yml
