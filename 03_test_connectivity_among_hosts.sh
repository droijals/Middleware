#!/bin/bash

# No solo hay que ser limpio, sino tambien parecerlo :-)
clear

# Verificacion de dependencias
command -v nc >/dev/null 2>&1 || {
	    echo "ERROR: netcat (nc) no está instalado."
    exit 1
}

# Fichero CSV
OUTPUT_FILE="resultado_conectividad_$(date +%Y%m%d_%H%M%S).csv"
echo "origen,destino,puerto,resultado,tiempo_ms" > "$OUTPUT_FILE"
echo "-----------------------------------------" >> "$OUTPUT_FILE"

# Entrada de datos
read -p "Introduce hosts de ORIGEN (separados por espacio): " -a ORIGENES
read -p "Introduce hosts de DESTINO (separados por espacio): " -a DESTINOS
read -p "Introduce PUERTOS de destino (separados por espacio): " -a PUERTOS

echo ""
echo "==== INICIO DE PRUEBAS ===="
echo ""

# Funcion para ejecutar prueba desde origen
probar_conectividad() { 
	local origen=$1
	local destino=$2
	local puerto=$3

	local start end duration result

	start=$(date +%s%3N)

	if [[ "$origen" == "localhost" || "$origen" == "$(hostname)" ]]; then
		# Ejecucion local
		nc -z -w 3 "$destino" "$puerto" >/dev/null 2>&1
	else
	        # Ejecucion remota por SSH
	        ssh -o BatchMode=yes -o ConnectTimeout=5 "$origen" "nc -z -w 3 $destino $puerto" >/dev/null 2>&1
	fi

	if [ $? -eq 0 ]; then
            result="OK"
        else
	    result="KO"
	fi

	end=$(date +%s%3N)
	duration=$((end - start))

	# Salida por pantalla
	printf "%-20s -> %-20s:%-6s [%s] (%sms)\n" "$origen" "$destino" "$puerto" "$result" "$duration"

	# Salida CSV
	echo "$origen,$destino,$puerto,$result,$duration" >> "$OUTPUT_FILE"
}

# Iteraciones
for origen in "${ORIGENES[@]}"; do
	echo "---- Probando desde: $origen ----"
	for destino in "${DESTINOS[@]}"; do
		for puerto in "${PUERTOS[@]}"; do
			probar_conectividad "$origen" "$destino" "$puerto"
		done
	done
	echo ""
done

echo "==== FIN DE PRUEBAS ===="
echo "Resultados guardados en este directorio con el nombre: $OUTPUT_FILE"
