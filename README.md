# DBII-Project2

# **Integrantes**
* Neo Marcelo Zapata Gallegos
* Harold Canto Vidal
* Christian Rojas Rojas
* Eros Carhuancho Espejo


# Tabla de contenido
- [Cuadro de Actividades](#Cuadro-de-Actividades)
- [Cuadro de Participación](#Cuadro-de-Participación)
- [Objetivo](#Objetivo)
- [Backend](#Backend)
  * [Dataset](#Dataset)
  * [Inverted index](#Inverted-index)
  * [Funciones importantes](#Funciones-importantes)
    + [Clase principal](#Clase-principal)
    + [Función load](#Función-load)
    + [Función score](#Función-score)
    + [Función retrieve](#Función-retrieve)
- [Frontend](#Frontend)
  * [Comparativa de Python y Postgres](#Comparativa-de-Python-y-Postgres)
  * [Comparación de tiempo](#Comparación-de-tiempo)


# Cuadro de Actividades:

<table>
  <tbody>
    <tr>
      <th>Lista de actividades realizadas</th>
      <th align="center">Responsable</th>
    </tr>
    <tr>
      <td>Implementación de la función init </td>
      <td align="center">Harold Canto Vidal</td>
    </tr>
    <tr>
      <td>Implementación de la función load</td>
      <td align="center">Neo Marcelo Zapata Gallegos</td>
    </tr>
    <tr>
      <td>Implementación de la función score</td>
      <td align="center">Christian Rojas Rojas y Neo Marcelo Zapata Gallegos</td>
    </tr>
    <tr>
      <td>Implementación de la función retrieve</td>
      <td align="center">Harold Canto Vidal y Neo Marcelo Zapata Gallegos</td>
    </tr>
    <tr>
      <td>Implementación de la función preprocesamiento</td>
      <td align="center">Christian Rojas Rojas </td>
    </tr>
    <tr>
      <td>Implementación del Frontend</td>
      <td align="center">Eros Carhuancho</td>
    </tr>
    <tr>
      <td>Escritura del informe</td>
      <td align="center">Eros Carhuancho</td>
    </tr>
  </tbody>
</table>


# Cuadro de Participación:

<table>
  <tbody>
    <tr>
      <th>Integrantes</th>
      <th align="center">Participación</th>
    </tr>
    <tr>
      <td>Neo Marcelo Zapata Gallegos</td>
      <td align="center">100%</td>
    </tr>
    <tr>
      <td>Harold Canto Vidal</td>
      <td align="center">100%</td>
    </tr>
    <tr>
      <td>Christian Rojas Rojas</td>
      <td align="center">100%</td>
    </tr>
    <tr>
      <td>Eros Carhuancho Espejo</td>
      <td align="center">100%</td>
    </tr>
  </tbody>
</table>

# Objetivo:
El objetivo del proyecto es crear un motor de búsqueda que a partir de una query textual podamos buscar los artículos académicos de nuestra base de datos que más se asemejan a esta, rankeando los resultados mediante un score. Este proceso se dará aplicando los conceptos aprendidos en clase como el índice invertido, la similitud de cosenos, la normalización de términos, etc. Posteriormente mediremos el tiempo que tarda esta filtración de información aplicada con Python y lo compararemos con el tiempo que tarda hacerlo con postgres.  



# Backend

## Dataset
El dataset contiene información sobre un conjunto muy grande de artículos académicos de los cuales solo extraeremos los más importantes correspondientes a una query
El dataset fue obtenido de: [![Dataset]()](https://www.kaggle.com/datasets/Cornell-University/arxiv/versions/99?resource=download)
El dataset se ubica en el siguiente path: "/backend/documents/data/"
El nombre del archivo utilizado (en caso sea actualizado) es: "arxiv-metadata.json"
Metadata del archivo de datos escogido:
* id
* submitter
* authors
* title
* comments
* journal-ref
* doi
* report-no
* categories
* license
* abstract
* versions
* update_date
* authors_parsed
Sin embargo, la data más relevante correspone de la columna "id" y "abstract" que son las utilizadas en el motor de busqueda.

## Inverted index
Es un método para estructurar la información más importante de un texto completo. La composición se da mediante un documento el cual tiene términos con una determinada frecuencia. En el caso del proyecto la información de la base de datos es organizada para retornar datos de una forma rápida y óptima. La consulta enviada también se procesa y organiza de la misma manera, posteriormente se genera un score de similitud con todos los documentos de la base de datos antes descritos. Finalmente se devuelven los documentos con mayor score los cuales se consideran más importantes.

## Funciones importantes
A continuación explicaremos brevemente las funciones más importantes de nuestra implementación.

### Clase principal
Es una clase que contiene todas las funciones necesarias para procesar la query y todos los artículos académicos de forma eficiente.
```python
class UBetterFixEverything():
```

### Función init
El constructor en primera instancia lo que hará es leer los stopwords de un archivo de texto.
```python
def __init__(self, c):
```


### Función load
Esta función procesa todos los datos del json. Extrae todos los términos importantes evitando todos los stopwords de la lista dada y va generando índice para cada término el cual contiene todo los documentos científicos que lo contienen y su frecuencia respectiva. Estos diccionarios tienen un límite de tamaño, el cual si es superado pasa a memoria secundaria guardando en archivos secundarios y durante el procesamiento se va guardando la norma de estos términos.

Finalmente  se realiza el merge de los archivos auxiliares creados que posteriormente elimina y finalmente este merge lo coloca en un Priority Queue. Estos datos dependiendo de los parámetros que inserte el usuario posteriormente nos serán útiles para retornar los primeros k resultados más similares a una query. 

```python
def load(self, MAX):
```

### Función score
Esta función descarta los stopwords antes procesados por el constructor y traerá los documentos científicos más parecidos a la query. Luego utilizaremos la  función tf_idf_weight_and_cosine_score para devolver un ranking de estos mismos documentos.
```python
def score(self, query, docs_to_read, k):
```

### Función retrieve
Finalmente esta función retorna solo los k documentos más parecidos a la query.
```python
def retrieve(self, k, docs_ids, scores, documents_retrieved):
```


# Frontend
Para el frontend se utilizó html y bootstrap. También se utilizó el motor de plantillas de jinja2 para poder manejar la cantidad de documentos similares a la consulta del usuario. 

## Comparativa de Python y Postgres
Las imágenes muestran los resultados de una consulta con la implementación de python y postgres con sus respectivos tiempos de ejecución.


![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/Resultado.png)
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/Resultado2.png)



## Comparación de tiempo
Para esta sección nos apoyamos de las variables que usamos en nuestra clase de indice invertido, con el print de estas variables obtuvimos datos relevantes como accesos a memoria en general y tiempo, de acuerdo al siguiente query obtuvimos los siguientes resultados:

### Query analizada
We construct a model of the CO remnant that\nmimics the results of the SPH simulation using a one-dimensional hydrodynamic\nstellar evolution code and then follow its secular evolution. The stellar\nevolution models indicate that the growth of the cold core is controlled by\nneutrino cooling at the interface between the core and the hot envelope, and\nthat carbon ignition in the envelope can be avoided despite high effective\naccretion rates. This result suggests that the assumption of forced accretion\nof cold matter that was adopted in previous studies of the evolution of double\nCO white dwarf merger remnants may not be appropriate. Our results imply that\nat least some products of double CO white dwarfs merger may be considered good\ncandidates for the progenitors of Type Ia supernovae. In this case, the\ncharacteristic time delay between the initial dynamical merger and the eventual\nexplosion would be ~10^5 yr. (Abridged).

10 000 datos con 40292 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem10.jpeg)

25 000 datos con 82171 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem25.jpeg)

50 000 datos con 178952 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem50.jpeg)

150 000 datos con 536261 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem150.jpeg)

200 000 datos con 724858 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem200.jpeg)

250 000 datos con 915224 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem250.jpeg)

500 000 datos con 1891505 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem500.jpeg)

1 000 000 datos con 1891505 accesos a memoria
![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/exp_mem1000.jpeg)

Posteriormente a esto guardaremos los datos de tiempo y cantidad de datos, esto nos ayudará a ver una comparativa entre el índice invertido en python y el de GIN de postgres.

![Image text](https://github.com/Neo-Zapata/DBII-Project2/blob/main/images/Resultado3.PNG)

Para la creación de la gráfica usamos el logaritmo de los valores para tener un gráfico más apreciable. Finalmente podemos notar que, para el query analizado, el índice invertido realizado en python es mejor para datos pequeños, pasada una cantidad de datos de 90 000 aproximadamente (inflexión), el indice GIN de postgres empieza a tener un mejor rendimiento en adelante.
