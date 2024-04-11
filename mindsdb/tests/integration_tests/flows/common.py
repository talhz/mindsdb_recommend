import time
import os
import json
import subprocess
import atexit
import asyncio
import re
import sys
from pathlib import Path
import signal

import psutil
import requests
from pandas import DataFrame

from ps import wait_port, is_port_in_use, net_connections


HTTP_API_ROOT = 'http://localhost:47334/api'

DATASETS_PATH = os.getenv('DATASETS_PATH')

USE_EXTERNAL_DB_SERVER = bool(int(os.getenv('USE_EXTERNAL_DB_SERVER') or "0"))

USE_PERSISTENT_STORAGE = bool(int(os.getenv('USE_PERSISTENT_STORAGE') or "0"))

EXTERNAL_DB_CREDENTIALS = str(Path.home().joinpath('.mindsdb_credentials.json'))

MINDSDB_DATABASE = 'mindsdb'

TEST_CONFIG = os.path.dirname(os.path.realpath(__file__)) + '/config/config.json'

TESTS_ROOT = Path(__file__).parent.absolute().joinpath('../../').resolve()

START_TIMEOUT = 15

OUTPUT = None  # [None|subprocess.DEVNULL]

TEMP_DIR = Path(__file__).parent.absolute().joinpath('../../').joinpath(
    f'temp/test_storage_{int(time.time()*1000)}/' if not USE_PERSISTENT_STORAGE else 'temp/test_storage/'
).resolve()
TEMP_DIR.mkdir(parents=True, exist_ok=True)

DATASETS_COLUMN_TYPES = {
    'us_health_insurance': [
        ('age', int),
        ('sex', str),
        ('bmi', float),
        ('children', int),
        ('smoker', str),
        ('region', str),
        ('charges', float)
    ],
    'hdi': [
        ('Population', int),
        ('Area', int),
        ('Pop_Density', int),
        ('GDP_per_capita_USD', int),
        ('Literacy', float),
        ('Infant_mortality', int),
        ('Development_Index', float)
    ],
    'used_car_price': [
        ('model', str),
        ('year', int),
        ('price', int),
        ('transmission', str),
        ('mileage', int),
        ('fueltype', str),
        ('tax', int),
        ('mpg', float),
        ('enginesize', float)
    ],
    'home_rentals': [
        ('number_of_rooms', int),
        ('number_of_bathrooms', int),
        ('sqft', int),
        ('location', str),
        ('days_on_market', int),
        ('initial_price', int),
        ('neighborhood', str),
        ('rental_price', int)
    ],
    'concrete_strength': [
        ('id', int),
        ('cement', float),
        ('slag', float),
        ('flyAsh', float),
        ('water', float),
        ('superPlasticizer', float),
        ('coarseAggregate', float),
        ('fineAggregate', float),
        ('age', int),
        ('concrete_strength', float)
    ]
}

CONFIG_PATH = TEMP_DIR.joinpath('config.json')

with open(TEST_CONFIG, 'rt') as f:
    config_json = json.loads(f.read())
    config_json['storage_dir'] = f'{TEMP_DIR}'
    config_json['storage_db'] = f'sqlite:///{TEMP_DIR}/mindsdb.sqlite3.db?check_same_thread=False&timeout=30'


def close_all_ssh_tunnels():
    RE_PORT_CONTROL = re.compile(r'^\.mindsdb-ssh-ctrl-\d+$')
    for p in Path('/tmp/mindsdb').iterdir():
        if p.is_socket() and p.name != '.mindsdb-ssh-ctrl-5005' and RE_PORT_CONTROL.match(p.name):
            sp = subprocess.Popen(f'ssh -S /tmp/mindsdb/{p.name} -O exit ubuntu@3.220.66.106', shell=True)
            sp.wait()


def close_ssh_tunnel(port, sp=None):
    if sp is not None:
        sp.kill()
    # NOTE line below will close connection in ALL test instances.
    # sp = subprocess.Popen(f'for pid in $(lsof -i :{port} -t); do kill -9 $pid; done', shell=True)
    if port is not None:
        print(f'Closing ssh tunnel at port {port}')
        sp = subprocess.Popen(f'ssh -S /tmp/mindsdb/.mindsdb-ssh-ctrl-{port} -O exit ubuntu@3.220.66.106', shell=True)
        sp.wait()


def open_ssh_tunnel(port, direction='R'):
    path = Path('/tmp/mindsdb')
    if not path.is_dir():
        path.mkdir(mode=0o777, exist_ok=True, parents=True)

    if port == 5005 and os.path.exists('/tmp/mindsdb/.mindsdb-ssh-ctrl-5005'):
        return 0

    if is_mssql_test() and port != 5005:
        cmd = f'ssh -i ~/.ssh/db_machine_ms -S /tmp/mindsdb/.mindsdb-ssh-ctrl-{port} -o TCPKeepAlive=yes -o ServerAliveCountMax=5 -o ServerAliveInterval=15 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -fMN{direction} 127.0.0.1:{port}:127.0.0.1:{port} Administrator@107.21.140.172'
    else:
        cmd = f'ssh -i ~/.ssh/db_machine -S /tmp/mindsdb/.mindsdb-ssh-ctrl-{port} -o TCPKeepAlive=yes -o ServerAliveCountMax=5 -o ServerAliveInterval=15 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -fMN{direction} 127.0.0.1:{port}:127.0.0.1:{port} ubuntu@3.220.66.106'
    sp = subprocess.Popen(
        cmd.split(' '),
        stdout=OUTPUT,
        stderr=OUTPUT
    )
    try:
        status = sp.wait(20)
    except subprocess.TimeoutExpired:
        status = 1
        sp.kill()

    return status


def stop_mindsdb(ports=None):
    mdb_ports = [47334, 47335, 47336]
    if isinstance(ports, list):
        mdb_ports = mdb_ports + ports
    procs = [x for x in net_connections() if x.pid is not None and x.laddr[1] in mdb_ports]
    print(f'Found {len(procs)} MindsDB processes')

    if len(procs) == 0:
        print('Nothing to close')
        return

    for proc in procs:
        print(f' -- {proc.pid} / {proc.laddr[1]} / {proc.status}')

    pid_port = set((x.pid, x.laddr[1]) for x in procs)

    interrupted_pids = []
    for pid, port in pid_port:
        if pid is None:
            print(f'Can not release {port} because it occupied by OS')
        elif pid not in interrupted_pids:
            try:
                p = psutil.Process(pid)
                print(f'Send SIGINT to {pid}/{[port]}')
                p.send_signal(signal.SIGINT)
                interrupted_pids.append(pid)
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                print(f'Can not interrupt process {pid}: {e}')

    waited_for = 0
    waited_ports = [x for x in net_connections() if x.laddr[1] in mdb_ports]
    while len(waited_ports) > 0 and waited_for < 30:
        print(f'\nSome mindsdb ports are yet to die, waiting for them to do so: {[(x.pid, x.laddr[1], x.status) for x in waited_ports]}. Waited for a total of: {waited_for} seconds\n')
        time.sleep(2)
        waited_for += 2
        waited_ports = [x for x in net_connections() if x.laddr[1] in mdb_ports]
    if waited_for >= 30:
        raise Exception('Some mindsdb ports can`t die.')


def is_mssql_test():
    for x in sys.argv:
        if 'test_mssql.py' in x:
            return True
    return False


mindsdb_port = None

if USE_EXTERNAL_DB_SERVER:
    open_ssh_tunnel(5005, 'L')
    wait_port(5005, timeout=10)

    close_all_ssh_tunnels()
    stop_mindsdb()

    for _ in range(10):
        r = requests.get('http://127.0.0.1:5005/port')
        if r.status_code != 200:
            raise Exception('Cant get port to run mindsdb')
        mindsdb_port = r.content.decode()
        print(f'Trying port forwarding on {mindsdb_port}')
        status = open_ssh_tunnel(mindsdb_port, 'R')
        if status == 0:
            break
    else:
        raise Exception('Cant get empty port to run mindsdb')

    print(f'use mindsdb port={mindsdb_port}')
    wait_port(mindsdb_port, timeout=10)
    config_json['api']['mysql']['port'] = mindsdb_port
    config_json['api']['mongodb']['port'] = mindsdb_port

    MINDSDB_DATABASE = f'mindsdb_{mindsdb_port}'
    config_json['api']['mysql']['database'] = MINDSDB_DATABASE
    config_json['api']['mongodb']['database'] = MINDSDB_DATABASE

    with open(EXTERNAL_DB_CREDENTIALS, 'rt') as f:
        credentials = json.loads(f.read())
    override = {}
    for key, value in credentials.items():
        value['publish'] = False
        value['type'] = key
        config_json['integrations'][f'default_{key}'] = value

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', None)
    if AWS_SECRET_ACCESS_KEY is not None and AWS_ACCESS_KEY_ID is not None:
        if 'permanent_storage' not in config_json:
            config_json['permanent_storage'] = {}
        config_json['permanent_storage']['s3_credentials'] = {
            'aws_access_key_id': AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': AWS_SECRET_ACCESS_KEY
        }

    config_json['permanent_storage'] = {
        'bucket': 'mindsdb-cloud-storage-v1'
    }


def make_test_csv(name, data):
    test_csv_path = TEMP_DIR.joinpath(f'{name}.csv').resolve()
    df = DataFrame(data)
    df.to_csv(test_csv_path, index=False)
    return str(test_csv_path)


def override_recursive(a, b):
    for key in b:
        if isinstance(b[key], dict) is False:
            a[key] = b[key]
        elif key not in a or isinstance(a[key], dict) is False:
            a[key] = b[key]
        # make config section empty by demand
        elif isinstance(b[key], dict) is True and b[key] == {}:
            a[key] = b[key]
        else:
            override_recursive(a[key], b[key])


def run_environment(apis, override_config={}):
    api_str = ','.join(apis)

    override_recursive(config_json, override_config)

    with open(CONFIG_PATH, 'wt') as f:
        f.write(json.dumps(config_json))

    os.environ['CHECK_FOR_UPDATES'] = '0'
    print('Starting mindsdb process!')
    subprocess.Popen(
        ['python3', '-m', 'mindsdb', f'--api={api_str}', f'--config={CONFIG_PATH}', '--verbose'],
        close_fds=True,
        stdout=OUTPUT,
        stderr=OUTPUT
    )
    atexit.register(close_ssh_tunnel, port=mindsdb_port)
    atexit.register(stop_mindsdb, ports=[mindsdb_port])

    print('Waiting on ports!')

    async def wait_port_async(port, timeout):
        start_time = time.time()
        started = is_port_in_use(port)
        while (time.time() - start_time) < timeout and started is False:
            await asyncio.sleep(1)
            started = is_port_in_use(port)
        return started

    async def wait_apis_start(ports):
        futures = [wait_port_async(port, 200) for port in ports]
        success = True
        for i, future in enumerate(asyncio.as_completed(futures)):
            success = success and await future
        return success

    ports_to_wait = [config_json['api'][api]['port'] for api in apis]

    ioloop = asyncio.get_event_loop()
    if ioloop.is_closed():
        ioloop = asyncio.new_event_loop()
    success = ioloop.run_until_complete(wait_apis_start(ports_to_wait))
    ioloop.close()
    if not success:
        raise Exception('Cant start mindsdb apis')
    print('Done waiting, mindsdb has started!')


def condition_dict_to_str(condition):
    ''' convert dict to sql WHERE conditions

        :param condition: dict
        :return: str
    '''
    s = []
    for name, value in condition.items():
        if isinstance(value, str):
            s.append(f"{name}='{value}'")
        elif value is None:
            s.append(f'{name} is null')
        else:
            s.append(f'{name}={value}')

    return ' AND '.join(s)


def get_all_pridict_fields(fields):
    ''' make list off all prediciton fields
    '''
    fieldes = list(fields.keys())
    for field_name, field_type in fields.items():
        fieldes.append(f'{field_name}_confidence')
        fieldes.append(f'{field_name}_explain')
        if field_type in [int, float]:
            fieldes.append(f'{field_name}_min')
            fieldes.append(f'{field_name}_max')
    return fieldes


def check_prediction_values(row, to_predict):
    try:
        for field_name, field_type in to_predict.items():
            if field_type in [int, float]:
                print(f'checking {field_name} is int or float')
                print(row[field_name], type(row[field_name]))
                assert isinstance(row[field_name], (int, float))
                print('checking min bound')
                assert isinstance(row[f'{field_name}_min'], (int, float))
                print('checking max bound')
                assert isinstance(row[f'{field_name}_max'], (int, float))
                print('comparing the two')
                assert row[f'{field_name}_max'] > row[f'{field_name}_min']
            elif field_type is str:
                print(f'checking {field_name} is str')
                assert isinstance(row[field_name], str)
            else:
                assert False

            print(f'checking confidence for {field_name}')
            assert isinstance(row[f'{field_name}_confidence'], (int, float))
            print(f'checking explain for {field_name}')
            assert isinstance(row[f'{field_name}_explain'], (str, dict))
    except Exception as e:
        print(f'Error "{e}" | Wrong values in row:')
        print(row)
        return False
    return True
