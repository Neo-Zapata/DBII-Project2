# DBII-Project2

# **Integrantes**
* Neo Marcelo Zapata Gallegos
* Harold Canto Vidal
* Christian Rojas Rojas
* Eros Carhuancho Espejo
# Objetivo:
El objetivo del proyecto es crear un motor de búsqueda que a partir de una query textual podamos buscar los artículos académicos de nuestra base de datos que más se asemejan a esta, rankeando los resultados mediante un score. Este proceso se dará aplicando los conceptos aprendidos en clase como el índice invertido, la similitud de cosenos, la normalización de términos, etc. Posteriormente mediremos el tiempo que tarda esta filtración de información aplicada con Python y lo compararemos con el tiempo que tarda hacerlo con postgres.  

#Backend

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


#Frontend



