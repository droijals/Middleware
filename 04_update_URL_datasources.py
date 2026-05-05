# -*- coding: utf-8 -*-

##############################################################
# Ejecutar desde el server dónde corre el AdminServer del WL #
##############################################################

# No solo hay que ser limpio sino tambien parecerlo :-)
import os
os.system('cls' if os.name == 'nt' else 'clear')

# Al tema:

import csv
import sys
import traceback

def log(msg):
        print('[INFO] ' + msg)

def log_error(msg):
        print('[ERROR] ' + msg)

def connect_to_wls(admin_url, username, password):
        log('Conectando a: ' + admin_url)
        try:
            connect(username, password, admin_url)
            log('Conexión OK')
        except:
            log_error('Fallo de conexión')
            raise

def detect_ds_type(ds_name):
        try:
            base_path = '/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name

            # Intento detectar Multi DS
            try:
                cd(base_path + '/JDBCDataSourceParams/' + ds_name)
                ds_list = cmo.getDataSourceList()
                if ds_list is not None:
                    return 'MULTI'
            except:
                pass

            # Intento detectar GridLink
            try:
                cd(base_path + '/JDBCOracleParams/' + ds_name)
                return 'GRIDLINK'
            except:
                pass

            # Intento detectar Generic
            try:
                cd(base_path + '/JDBCDriverParams/' + ds_name)
                return 'GENERIC'
            except:
                pass

            return 'UNKNOWN'

        except:
            return 'UNKNOWN'


def update_datasource(ds_name, new_url):
    log('--------------------------------------------------')
    log('Procesando datasource: ' + ds_name)

    base_path = '/JDBCSystemResources/' + ds_name + '/JDBCResource/' + ds_name

    ds_type = detect_ds_type(ds_name)
    log('Tipo detectado: ' + ds_type)

    if ds_type == 'MULTI':
        log('Multi DataSource detectado → NO se modifica directamente')
        return

    try:
        edit()
        startEdit()
        log('Entrando en modo edición')

        if ds_type == 'GENERIC':
            path = base_path + '/JDBCDriverParams/' + ds_name
        elif ds_type == 'GRIDLINK':
            path = base_path + '/JDBCDriverParams/' + ds_name
        else:
            log_error('Tipo desconocido, se omite')
            stopEdit('y')
            return

        log('Accediendo a MBean: ' + path)
        cd(path)

        current_url = cmo.getUrl()

        log('URL actual: ' + str(current_url))
        log('Nueva URL: ' + str(new_url))

        if current_url == new_url:
            log('No hay cambios necesarios')
            cancelEdit('y')
            return

        log('Aplicando cambio...')
        cmo.setUrl(new_url)

        log('Guardando cambios...')
        save()

        log('Activando cambios...')
        activate()

        log('Cambio aplicado correctamente')

    except:
        log_error('Error actualizando datasource: ' + ds_name)
        traceback.print_exc()
        try:
            undo('true', 'y')
            stopEdit('y')
        except:
            pass


def process_csv(file_path):
    log('Leyendo fichero: ' + file_path)

    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)

        current_connection = None

        for row in reader:
            admin_url = row['admin_url']
            username = row['username']
            password = row['password']
            ds_name = row['datasource_name']
            new_url = row['new_url']

            log('==================================================')
            log('Nueva entrada CSV')
            log('Admin URL: ' + admin_url)
            log('Datasource: ' + ds_name)

            if current_connection != admin_url:
                if current_connection is not None:
                    log('Cerrando conexión previa')
                    disconnect()

                connect_to_wls(admin_url, username, password)
                current_connection = admin_url

            update_datasource(ds_name, new_url)

        if current_connection is not None:
            log('Desconectando...')
            disconnect()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Uso: wlst.sh 04_update_URL_datasources.py datasources.csv')
        exit(1)

    file_path = sys.argv[1]
    process_csv(file_path)
