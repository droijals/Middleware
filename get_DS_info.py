# Script en Python que se conecta vía WLST a un weblogic y extrae en un CSV esta info:
#     Nombre del DataSource
#     Tipo (Generic, Gridlink)
#     URL (cadena de conexión)
#     Target (Cluster al que va asociado ese DataSource) 
#     Probado con éxito en DataSources globales (no particionados) y en versiones de weblogic 10.3.x (11g), 12.1.x, 12.2.x y 14.1.1


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
    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName)
        if cmo.getJDBCDataSourceParams() is not None:
            return "Generic"
    except:
        pass

    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCOracleParams/' + dsName)
        return "GridLink"
    except:
        pass

    try:
        cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDataSourceParams/' + dsName)
        return "MultiDataSource"
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

# CSV output (SIN runtime)
outputFile = '/tmp/datasources_report.csv'
f = open(outputFile, 'w')

# Encabezado SIN RuntimeTest
f.write('Name,Type,URL,Targets\n')

for ds in cmo.getJDBCSystemResources():

    dsName = ds.getName()

    print('----------------------------------------')
    print('Datasource: ' + dsName)

    dsType = detectType(dsName)
    url = getURL(dsName)
    targets = getTargets(ds)

    print('Tipo: ' + dsType)
    print('URL: ' + str(url))
    print('Targets (Clusters): ' + targets)

    # CSV SIN RuntimeTest
    f.write(dsName + ',' + dsType + ',' + str(url) + ',' + targets + '\n')

f.close()

print('======================================================')
print('CSV generado en: ' + outputFile)
print('======================================================')

disconnect()
exit()
