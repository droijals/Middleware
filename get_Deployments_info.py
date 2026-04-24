# -*- coding: utf-8 -*-

# Script en Python que se conecta vía WLST a un weblogic y extrae en un CSV un breve listado de los deployments
# Probado con éxito en versiones de weblogic 12.1.x, 12.2.x y 14.1.1

import os

connect('weblogic','password','t3://host:7001')

OUTPUT_DIR  = '/tmp/DROIJALS'
OUTPUT_FILE = OUTPUT_DIR + '/deployments_info.csv'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

f = open(OUTPUT_FILE, 'w')
f.write("NAME,SERVER,STATE,HEALTH\n")

domainRuntime()

# Obtener servidores runtime correctamente vía ls()
cd('/')
servers = ls('/ServerRuntimes', returnMap='true')

for serverName in servers:

    try:
        path = '/ServerRuntimes/' + serverName + '/ApplicationRuntimes'
        cd(path)
    except:
        continue

    apps = ls(returnMap='true')

    if apps is None:
        continue

    for appName in apps:

        # Filtro definitivo de ruido WLST
        if appName is None:
            continue
        if "No stack trace available" in str(appName):
            continue
        if appName.strip() == "":
            continue

        try:
            cd(path + '/' + appName)

            try:
                state = cmo.getState()
            except:
                state = "UNKNOWN"

            try:
                healthObj = cmo.getHealthState()
                health = healthObj.getState()
            except:
                health = "N/A"

            f.write(appName + "," + serverName + "," + str(state) + "," + str(health) + "\n")

        except:
            continue

f.close()

disconnect()
exit()

print("CSV generado en: " + OUTPUT_FILE)
