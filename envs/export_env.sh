#!/bin/bash
conda env export | grep -v "^prefix: "
