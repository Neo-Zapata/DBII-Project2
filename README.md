# DBII-Project2

## **Integrantes**
* Neo Marcelo Zapata Gallegos
* Harold Canto Vidal
* Christian Rojas Rojas
* Eros Carhuancho Espejo
## Objetivo:
El objetivo del proyecto es crear un motor de búsqueda que a partir de una query textual podamos buscar los artículos académicos de nuestra base de datos que más se asemejan a esta, rankeando los resultados mediante un score. Este proceso se dará aplicando los conceptos aprendidos en clase como el índice invertido, la similitud de cosenos, la normalización de términos, etc. Posteriormente mediremos el tiempo que tarda esta filtración de información aplicada con Python y lo compararemos con el tiempo que tarda hacerlo con postgres.  


## Métodos
>TODO
>
## Inverted index
>TODO

## **Tabla de contenido**
* [Dataset](#dataset)
* [TODO](#todo)

## **Anotaciones**
El dataset fue obtenido de: [![Dataset]()](https://www.kaggle.com/datasets/Cornell-University/arxiv/versions/99?resource=download)
el dataset se ubica en el siguiente path: "/backend/documents/data/"
el nombre del archivo utilizado (en caso sea actualizado) es: "arxiv-metadata.json"
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
