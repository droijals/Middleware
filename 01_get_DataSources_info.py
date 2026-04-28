# -*- coding: utf-8 -*-

# Script en Python que se conecta vía WLST a un weblogic y extrae en un CSV esta info:
#     Nombre del DataSource
#     Tipo (Generic, Gridlink)
#     URL (cadena de conexión)
#     Target (Cluster al que va asociado ese DataSource) 
#     Probado con éxito en DataSources globales (no particionados) y en versiones de weblogic 10.3.x (11g), 12.1.x, 12.2.x y 14.1.1

# ============================================
# CONEXION
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

    # 1. GRIDLINK (detección real)
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCOracleParams/' + dsName)
        
        # Solo es GridLink si FAN está habilitado
        if cmo.isFanEnabled():
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

    # 3. GENERIC (fallback real)
    return "Generic"

def getURL(dsName):
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName)
        return cmo.getUrl()
    except:
        return "N/A"

# ============================================
# EJECUCION PRINCIPAL
# ============================================

domainConfig()

print('======================================================')
print('DATASOURCES INVENTORY (CSV EXPORT)')
print('======================================================')

cd('/JDBCSystemResources')

# CSV salida
outputFile = '/tmp/DROIJALS/datasources_report.csv'
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
