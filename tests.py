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


def test_running_with_vault(tmpdir):
    inv = tmpdir.join('inventory')
    inv.write('localhost ansible_connection=local\n')

    password_file = tmpdir.join('passwd')
    password_file.write('secret_password')

    all_vars = tmpdir.mkdir('group_vars').join('all')
    all_vars.write('dummy_var: secret_value')
    subprocess.check_call([
        'ansible-vault', 'encrypt',
        '--vault-password-file', str(password_file),
        str(all_vars)
    ])

    assert 'secret_value' not in all_vars.read()

    process = subprocess.Popen([
        ansible_shell_path, '-i', str(inv),
        '--vault-password-file', str(password_file)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    stdout, _ = process.communicate('\n'.join([
        'secret_password',
        'cd all',
        '!echo {{ dummy_var }}',
        '\n'
    ]))
    print stdout

    assert 'secret_value' in stdout
