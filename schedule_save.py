'''
Test with Postgres 9.4 & Postgres 12.6
Read the doc for schedule job : https://schedule.readthedocs.io/en/stable/
Author : Pierre SICALLAC
Mail : pierre.sicallac@protonmail.com
Date : 04/02/2022
Job : Save all the databases

Special thanks to @Jaymon for is job on is project "dump", i use some part of your code particularly in https://github.com/Jaymon/dump/blob/master/dump/postgres.py
Profil : https://github.com/Jaymon
Project : https://github.com/Jaymon/dump


Comment : This is my first functional script for my professional activity
'''
import logging
import os
from logging import basicConfig, info
from re import sub
from tempfile import NamedTemporaryFile
from psycopg2 import connect
from subprocess import Popen
from schedule import every, run_pending
from datetime import date
from time import sleep

ascii_art = '''
╔═══╗╔═══╗╔╗ ╔╗╔═══╗╔═══╗╔╗ ╔╗╔╗   ╔═══╗╔═══╗    ╔═══╗╔═══╗╔╗  ╔╗╔═══╗    ╔═══╗╔═══╗╔═══╗╔════╗╔═══╗╔═══╗╔═══╗╔═══╗
║╔═╗║║╔═╗║║║ ║║║╔══╝╚╗╔╗║║║ ║║║║   ║╔══╝║╔═╗║    ║╔═╗║║╔═╗║║╚╗╔╝║║╔══╝    ║╔═╗║║╔═╗║║╔═╗║║╔╗╔╗║║╔═╗║║╔═╗║║╔══╝║╔═╗║
║╚══╗║║ ╚╝║╚═╝║║╚══╗ ║║║║║║ ║║║║   ║╚══╗║╚═╝║    ║╚══╗║║ ║║╚╗║║╔╝║╚══╗    ║╚═╝║║║ ║║║╚══╗╚╝║║╚╝║║ ╚╝║╚═╝║║╚══╗║╚══╗
╚══╗║║║ ╔╗║╔═╗║║╔══╝ ║║║║║║ ║║║║ ╔╗║╔══╝║╔╗╔╝    ╚══╗║║╚═╝║ ║╚╝║ ║╔══╝    ║╔══╝║║ ║║╚══╗║  ║║  ║║╔═╗║╔╗╔╝║╔══╝╚══╗║
║╚═╝║║╚═╝║║║ ║║║╚══╗╔╝╚╝║║╚═╝║║╚═╝║║╚══╗║║║╚╗    ║╚═╝║║╔═╗║ ╚╗╔╝ ║╚══╗    ║║   ║╚═╝║║╚═╝║ ╔╝╚╗ ║╚╩═║║║║╚╗║╚══╗║╚═╝║
╚═══╝╚═══╝╚╝ ╚╝╚═══╝╚═══╝╚═══╝╚═══╝╚═══╝╚╝╚═╝    ╚═══╝╚╝ ╚╝  ╚╝  ╚═══╝    ╚╝   ╚═══╝╚═══╝ ╚══╝ ╚═══╝╚╝╚═╝╚═══╝╚═══╝
                                                                                                                   
                                                                                                                   
                                                                                                                                                                    
    '''
while True:
    print(ascii_art)

    print('''
Que voulez-vous faire ? 

    - 1 : Lancer la sauvegarde automatique
    - 2 : Sauvegarder toutes les bases du serveur
    - 3 : Aide
    
> ''', end='')

    try:
        choice = int(input())
        if 0 < choice < 4:
            break
        else:
            x = 1 / 0
    except BadChoice as bad:
        os.system('cls' if os.name == 'nt' else 'clear')
        pass


def set_connexion() -> connect:
    try:
        connex = connect(database=db, user=user, password=pwd, host=host, port=port0)
        print('Connexion au serveur réussi')
        return connex
    except:
        print('Connexion au serveur impossible')
        exit()


def close_connection():
    cursor.close()
    connexion.close()


def get_all_db():
    query = 'SELECT datname FROM pg_database;'
    cursor.execute(query)
    return list(map(str, (sub("['(,)']", "", str(row)) for row in cursor.fetchall())))


def _get_new_name_save(db_name):
    return 'DBSAVE_{}_{}.backup'.format(db_name, date.today())


def _get_path(db_name):
    path = os.path.join(backup_path, db_name)
    if os.path.isdir(path):
        return path
    os.mkdir(path)
    return path


def save_all_db(scheduler=True):
    list_db = get_all_db()
    for db_name in list_db:
        if db_name not in exclude_DB:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f'Sauvegarde en cours de {db_name}')
            path = _get_path(db_name)
            outfile = os.path.join(path, _get_new_name_save(db_name))
            command = ['pg_dump'
                        , '-i'
                        , '-h {}'.format(host)
                        , '-p {}'.format(port0)
                        , '-U {}'.format(user)
                        , '-F c'
                        , '-b'
                        , '-v'
                        , r'-f "{}"'.format(outfile)
                        , '{}'.format(db_name)]

            _run_cmd(' '.join(command))
            info('Sauvegarde de {} : OK'.format(db_name))

    if scheduler:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(ascii_art)
        print('Sauvegarde automatique en place')
        print('Attention : ne pas fermer cette fenêtre.')


def _get_env():
    """this returns an environment dictionary we want to use to run the command
    this will also create a fake pgpass file in order to make it possible for
    the script to be passwordless"""

    # create a temporary pgpass file
    pgpass = _get_file()
    # format: http://www.postgresql.org/docs/9.2/static/libpq-pgpass.html
    pgpass.write('*:*:*:{}:{}\n'.format(user, pwd).encode("utf-8"))
    pgpass.close()
    env = dict(os.environ)
    env['PGPASSFILE'] = pgpass.name

    # we want to assure a consistent environment
    if 'PGOPTIONS' in env:
        del env['PGOPTIONS']
    return env


def _get_file():
    '''
    return an opened tempfile pointer that can be used
    http://docs.python.org/2/library/tempfile.html
    '''
    f = NamedTemporaryFile(delete=False)
    return f


def _run_cmd(cmd, ignore_ret_code=False):
    env = _get_env()
    kwargs = {
        'shell': True,
        'env': env
    }

    pipe = Popen(
        cmd,
        **kwargs
        , cwd=postgres_path
    )
    ret_code = pipe.wait()
    if not ignore_ret_code and ret_code > 0:
        info('Échec de la sauvegarde : [{}]'.format(cmd))

    return pipe

cur_path = os.path.dirname(os.path.abspath(__file__))

# SETUP LOG FILE
log = "save.log"
basicConfig(filename=log, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

try:
    with open(cur_path + r"\conf\save_conf.txt", "r") as con_file:
        host = con_file.readline().strip().split(':')[1]
        user = con_file.readline().strip().split(':')[1]
        db = con_file.readline().strip().split(':')[1]
        pwd = con_file.readline().strip().split(':')[1]
        port0 = con_file.readline().strip().split(':')[1]
        hour_save = list(map(str, con_file.readline().strip().split(':')[1].split('|')))
        exclude_DB = list(map(str, con_file.readline().strip().split(':')[1].split('|')))
        backup_path = con_file.readline().strip().split(':')[1]
        postgres_path = con_file.readline().strip().split('|')[1]
    if backup_path == 'cur_path':
        backup_path = os.path.dirname(os.path.abspath(__file__))

except ErrorFoundFile as error:
    print('Erreur fichier de configuration introuvable')
    exit()

connexion = set_connexion()
cursor = connexion.cursor()

if choice == 1:
    info('Mise en place de la sauvegarde automatique.')
    info("Chemin d'accès des fichiers de sauvegarde : {}".format(backup_path))
    for hour in hour_save:
        every().day.at(hour + ':00').do(save_all_db)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(ascii_art)
    print('Sauvegarde automatique en place')
    print('Attention : ne pas fermer cette fenêtre.')

    while True:
        run_pending()
        sleep(1)

elif choice == 2:
    save_all_db()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(ascii_art)
    print('Sauvegarde de toutes les bases : OK')
elif choice == 3:
    print('''Pour modifier les options de connexion au serveur veuillez éditer le fichier de configuration ce trouvant 
dans le fichier de configuration du script de sauvegarde''')