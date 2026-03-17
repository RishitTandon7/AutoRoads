#!/bin/bash
export DISPLAY=:0
cd "/mnt/d/The Open Road/designs/gcd"
openroad -no_init -exit mpw_shuttle.tcl

openroad -gui load_gui_mpw.tcl
