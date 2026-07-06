#!/usr/bin/env python3
"""Compatibilità: il builder ora è tools/sad.py.

    python3 tools/sad.py build clienti/<slug>.json      (equivalente di questo script)
    python3 tools/sad.py build-base                     (ricostruisce stanza.html)
"""
import subprocess, sys, os
sys.exit(subprocess.call([sys.executable,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'sad.py'),
    'build', *sys.argv[1:]]))
