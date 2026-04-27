# -*- coding: utf-8 -*-

import os

connect('weblogic','password','t3://host:7001')

OUTPUT_DIR  = '/tmp/DROIJALS'
OUTPUT_FILE = OUTPUT_DIR + '/deployments.csv'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def csv_escape(value):
    if value is None:
        return ""
    v = str(value)
    if ',' in v or '"' in v:
        v = '"' + v.replace('"', '""') + '"'
    return v

f = open(OUTPUT_FILE, 'w')
f.write("NAME,STATE,HEALTH,TARGET,TARGET_TYPE,TYPE,CONTEXT_ROOT\n")

# =========================
# 1. INVENTARIO
# =========================
domainConfig()

deployments = {}

apps = cmo.getAppDeployments()

for app in apps:
    name = app.getName()

    # TARGETS
    targets = []
    for t in app.getTargets():
        try:
            tType = t.getType()
        except:
            # fallback 12.1
            if "Cluster" in str(t):
                tType = "Cluster"
            else:
                tType = "Server"

        targets.append({
            "name": t.getName(),
            "type": tType.upper()
        })

    if not targets:
        targets = [{"name": "NO_TARGET", "type": "UNKNOWN"}]

    # TYPE (EAR/WAR/JAR)
    try:
        src = app.getSourcePath()
        if src:
            src = src.lower()
            if src.endswith(".ear"):
                appType = "EAR"
            elif src.endswith(".war"):
                appType = "WAR"
            elif src.endswith(".jar"):
                appType = "JAR"
            else:
                appType = "UNKNOWN"
        else:
            appType = "UNKNOWN"
    except:
        appType = "UNKNOWN"

    # CONTEXT ROOT (config)
    context_root = ""
    try:
        modules = app.getModules()
        if modules:
            for m in modules:
                try:
                    cr = m.getContextRoot()
                    if cr:
                        context_root = cr
                        break
                except:
                    continue
    except:
        pass

    deployments[name] = {
        "targets": targets,
        "type": appType,
        "context_root": context_root
    }

# =========================
# 2. MAPEO SERVER → CLUSTER
# =========================
server_to_cluster = {}

servers = cmo.getServers()
for s in servers:
    sName = s.getName()
    try:
        cluster = s.getCluster()
        if cluster:
            server_to_cluster[sName] = cluster.getName()
        else:
            server_to_cluster[sName] = None
    except:
        server_to_cluster[sName] = None

# =========================
# 3. RUNTIME
# =========================
domainRuntime()

cd('/ServerRuntimes')
servers_rt = ls(returnMap='true')

runtime_data = {}

for serverName in servers_rt:

    try:
        path = '/ServerRuntimes/' + serverName + '/ApplicationRuntimes'
        cd(path)
    except:
        continue

    apps_runtime = ls(returnMap='true')
    if apps_runtime is None:
        continue

    for appName in apps_runtime:

        if appName is None:
            continue
        if "No stack trace available" in str(appName):
            continue
        if appName not in deployments:
            continue

        try:
            cd(path + '/' + appName)

            try:
                state = str(cmo.getState())
            except:
                state = "UNKNOWN"

            try:
                healthObj = cmo.getHealthState()
                health = str(healthObj.getState())
            except:
                health = "N/A"

            # fallback context-root runtime (12.1 útil)
            if deployments[appName]["context_root"] == "":
                try:
                    cr = cmo.getContextRoot()
                    if cr:
                        deployments[appName]["context_root"] = cr
                except:
                    pass

            cluster = server_to_cluster.get(serverName)

            if cluster:
                key = (appName, cluster)
            else:
                key = (appName, serverName)

            if key not in runtime_data:
                runtime_data[key] = []

            runtime_data[key].append({
                "state": state,
                "health": health
            })

        except:
            continue

# =========================
# 4. CONSOLIDACIÓN
# =========================
def consolidate_state(states):
    if "STATE_FAILED" in states:
        return "STATE_FAILED"
    if "STATE_ADMIN" in states:
        return "STATE_ADMIN"
    if all(s == "STATE_ACTIVE" for s in states):
        return "STATE_ACTIVE"
    return "STATE_PARTIAL"

def consolidate_health(healths):
    priority = {
        "HEALTH_OK": 0,
        "HEALTH_WARN": 1,
        "HEALTH_CRITICAL": 2,
        "N/A": 3
    }
    worst = "HEALTH_OK"
    for h in healths:
        if h in priority and priority[h] > priority[worst]:
            worst = h
    return worst

# =========================
# 5. OUTPUT
# =========================
for appName in deployments:

    appInfo = deployments[appName]

    for t in appInfo["targets"]:

        targetName = t["name"]
        targetType = t["type"]

        key = (appName, targetName)

        if key in runtime_data:
            states  = [x["state"] for x in runtime_data[key]]
            healths = [x["health"] for x in runtime_data[key]]

            final_state  = consolidate_state(states)
            final_health = consolidate_health(healths)
        else:
            final_state  = "STATE_NEW"
            final_health = "N/A"

        line = [
            csv_escape(appName),
            csv_escape(final_state),
            csv_escape(final_health),
            csv_escape(targetName),
            csv_escape(targetType),
            csv_escape(appInfo["type"]),
            csv_escape(appInfo["context_root"])
        ]

        f.write(",".join(line) + "\n")

f.close()

disconnect()
exit()

print("CSV generado en: " + OUTPUT_FILE)
