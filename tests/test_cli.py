"""Tests for the cli calls"""
import subprocess

def test_cli_display():
    command = "python3 src/python_phycam_margin_analysis.py -o display -som PCL-066 -kit 3022210I.A0 -rev 1"
    print(command)
    result = subprocess.run(command.split(' '))
    assert result.returncode == 0
