import pytest
import imp
import subprocess
import os

ansible_shell_path = os.path.dirname(__file__) + '/ansible-shell'
with open(ansible_shell_path) as f:
    ansible_shell = imp.load_module(
        'ansible_shell', f, ansible_shell_path, ('', 'U', 1))


@pytest.mark.parametrize(('hosts', 'serial', 'result'), [
    (['a', 'b'], 1, [['a'], ['b']]),
    (['a', 'b', 'c'], 2, [['a', 'b'], ['c']]),
    ([], 1, []),
    ([], 0, []),
    (['a', 'b'], 0, [['a', 'b']]),
])
def test_generating_batches(hosts, serial, result):
    assert result == ansible_shell.get_hosts_batches(hosts, serial)


def test_running_ansible_shell(tmpdir):
    inv = tmpdir.join('inventory')
    inv.write('localhost ansible_connection=local\n')
    process = subprocess.Popen([ansible_shell_path, '-i', str(inv)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    stdout, _ = process.communicate('cd all\nsetup\n')
    print stdout

    assert '"ansible_hostname"' in stdout
