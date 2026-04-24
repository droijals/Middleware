# -*- coding: utf-8 -*-

# ============================================
# CONEXIÓN
# ============================================

connect('weblogic','password','t3://host:7001')

# ============================================
# FUNCIONES AUXILIARES
# ============================================

def getTargets(dsBean):
    targets = []
    try:
        for t in dsBean.getTargets():
            targets.append(t.getName())
    except:
        pass
    return ",".join(targets)

def detectType(dsName):

    # 1. GRIDLINK (prioridad máxima)
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCOracleParams/' + dsName)
        return "GridLink"
    except:
        pass

    # 2. MULTI DATASOURCE
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDataSourceParams/' + dsName)
        if cmo.getDataSourceList() is not None:
            return "MultiDataSource"
    except:
        pass

    # 3. GENERIC (fallback)
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName)
        if cmo.getJDBCDataSourceParams() is not None:
            return "Generic"
    except:
        pass

    return "Unknown"

def getURL(dsName):
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName)
        return cmo.getUrl()
    except:
        return "N/A"

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

domainConfig()

print('======================================================')
print('DATASOURCES INVENTORY (CSV EXPORT)')
print('======================================================')

cd('/JDBCSystemResources')

# CSV salida
outputFile = '/tmp/datasources_report.csv'
f = open(outputFile, 'w')

# Cabecera CSV
f.write('Name,Type,URL,Targets\n')

for ds in cmo.getJDBCSystemResources():

    dsName = ds.getName()

    print('----------------------------------------')
    print('Datasource: ' + dsName)

    dsType = detectType(dsName)
    print('Tipo: ' + dsType)

    url = getURL(dsName)
    print('URL: ' + str(url))

    targets = getTargets(ds)
    print('Targets: ' + targets)

    # Escritura CSV
    f.write(dsName + ',' + dsType + ',' + str(url) + ',' + targets + '\n')

f.close()

print('======================================================')
print('CSV generado en: ' + outputFile)
print('======================================================')

disconnect()
exit()
