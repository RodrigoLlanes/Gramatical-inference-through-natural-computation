# Inferencia gramatical de lenguajes incontextuales mediante computación natural y evolutiva

Este repositorio contiene la implementación del simulador de un modelo de inferencia gramatical, basado en sistemas
P en tejido combinados con algoritmos genéticos. Es parte de mi trabajo final de grado (TFG), a continuación se 
encuentran las instrucciones sobre su instalación, uso y las utilidades presentes en el simulador.

# Instalación

Para realizar la instalación, asumiremos que ya se dispone de una versión de [python](https://www.python.org/) instalada
superior o igual a la 3.8 y la herramienta de entornos virtuales de python venv. Si se ha descargado
python de la página oficial debería estar instalada, si se ha instalado por terminal puede que se
deba instalar aparte.

También cabe destacar que todos los comandos mostrados a continuación serán para sistemas
unix, para windows podrían variar ligeramente, para lo que recomendamos consultar la [guía de
entornos virtuales de python](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).

El código fuente del simulador está disponible en [GitHub](https://github.com/RodrigoLlanes/Gramatical-inference-through-natural-computation), para utilizarlo, el primera paso será
clonar dicho repositorio en local. Si se tiene instalado el cliente de [git](https://git-scm.com/), es posible hacerlo con el
siguiente comando:
```
git clone https://github.com/RodrigoLlanes/Gramatical-inference-through-natural-computation.git
```
Una vez clonado el repositorio y situando la terminal en la carpeta raíz del mismo, crearemos
un entorno virtual, para no “ensuciar” nuestra instalación de python,
```
python3 -m venv env
```
después lo activamos
```
source env/bin/activate
```
y por último cargamos las librerías del proyecto mediante el archivo “requirements.txt”.
```
python3 -m pip install -r requirements.txt
```
Una vez completados todos estos pasos, ya disponemos de un entorno python listo para ejecutar el simulador.



# Uso del simulador

Para hacer uso del simulador, el primer paso es definir la gramática que deseamos inferir, para
ello creamos un fichero .json con el siguiente formato:
```json
{
    "name": "Dyck",
    "S": "S",
    "Vn" : ["S", "A", "B"],
    "Vt": ["a", "b"],
    "P": {
        "S": [["S", "S"], ["A", "B"]],
        "A": [["a"]],
        "B": [["S", "B"], ["b"]]
    }
}
```
Este fichero está definiendo el lenguaje de Dyck, el parámetro “name” puede emplear código latex y es opcional, solo se usa con fines estéticos. El resto de parámetros son obligatorios y
representan el símbolo terminal, los símbolos no terminales, terminales y las producciones respectivamente. Por lo que la gramática tendría la forma:

S → SS

S → AB

A → a

B → SB

B → b

Esta gramática y las otras dos usadas en este trabajo están accesibles en el repositorio, en la
carpeta grammars, como gramáticas de ejemplo.

Una vez definida nuestra gramática formal en forma normal de Chomsky, crearemos el fichero
con los casos de entrenamiento y test, para ello haremos uso de la primera utilidad del simulador,
cbuilder:
```
python3 main.py cbuilder grammars/wwr.json 50 50 cases.json
```
Donde “grammars/wwr.json” es la ruta al fichero json que define la gramática cuyos casos
queremos generar, el primer 50 es el número de casos positivos, el segundo 50 el número de casos
negativos y “cases.json” el fichero de salida.

Una vez generados los casos, definiremos los parámetros de nuestro experimento, para ello
crearemos un fichero json con el siguiente formato:
```json
{
    "n_non_term_sym": 3,
    "n_terminal_sym": 2,
    "n_non_term_prod": 3,
    "n_terminal_prod": 2,
    
    "n_grammars": 30,
    "n_cells": 5,
    
    "samples_size": 25,
    "epochs": 1,
    "batch_size": [1, 2, 5],
    "shuffle_epochs": true,
    
    "n_crossovers": 5,
    "n_mutations": 5,
    "mutation_size_min": 1,
    "mutation_size_max": 10,
    "mutate_out": false
}
```
Este fichero se encuentra a modo de ejemplo en el repositorio, en la carpeta experiments.
Los parámetros de este fichero se dividen en cuatro grupos, el primero hace referencia a las
gramáticas que vamos a emplear como población de los sistemas P del tejido, número de símbolos
y producciones no terminales y terminales.

El segundo hace referencia a la construcción del tejido, número de sistemas P y número de
gramáticas por sistema.

El tercer grupo gestiona el proceso de entrenamiento, tamaño del conjunto de entrenamiento,
épocas, tamaño de lote y la opción de “barajar” las muestras en cada época.
El último grupo controla todo lo relacionado con los algoritmos genéticos, el número de recombinaciones, el número de mutaciones, el número mínimo de símbolos cambiados por una
mutación, el número máximo y la opción de aplicar las mutaciones y recombinaciones también en
el sistema de salida.

Si cualquiera de estos parámetros se define como una lista (como en este ejemplo el tamaño
de lote), el simulador ejecutará todas las combinaciones posibles.
Una vez definido nuestro fichero de experimento, llega la hora de ejecutarlo, para ello haremos
uso de la principal utilidad del simulador, exp:
```
python3 main.py exp experiments/batch_size.json cases.json result.json
```
Donde “experiments/batch_size.json” es la ruta al fichero del experimento, “cases.json” es la
ruta al fichero de casos que queremos emplear y “result.json” la ruta de salida.

Además de esto se le pueden pasar adicionalmente los parámetros -v para aumentar la verbosidad y -r junto con un número entero para repetir cada experimento ese número de veces.
En el fichero “result.json” quedará el resultado de cada ejecución, los parámetros empleados,
la gramática resultante y su accuracy.



# Otras utilidades

Para acabar repasaremos las dos utilidades extra del simulador que nos permiten visualizar con
mayor facilidad los resultados.

### 1. Visualizador
El visualizador nos permite mostrar por pantalla una gráfica con el resultado de la ejecución
de un experimento, para ello haremos uso del siguiente comando:
```
python3 main.py plot result.json
```
Donde “result.json” es el fichero de salida de un experimento. Aparte de esto, puede recibir un
paramétro opcional -m seguido de “err”, “box” o “dot”, para configurar el modo de dibujo a barras
de error, box and whiskers o puntos.

### 2. Generador de código latex
Esta utilidad nos permite generar tablas y gráficas latex de un conjunto de experimentos, para
poder insertarlos directamente en documentos latex como este.

Para ello, seleccionamos distintos experimentos que o hagan uso del mismo archivo de experimentos o modifiquen los mismos parámetros (no es necesario que usen los mismos casos ni los
mismos lenguajes) y ejecutaremos el siguiente comando:
```
python3 main.py latex table.tex plot.tex -f out.json
```
Donde “table.tex” es el fichero de salida para la tabla, “plot.tex” es el fichero de salida para
la gráfica y el último parámetro -f puede recibir un número indefinido de ficheros que unirá para
generar las tablas y gráficas.