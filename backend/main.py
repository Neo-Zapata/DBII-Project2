import json
import linecache as lc
from operator import index
import os
import io
from re import A
import sys
from queue import PriorityQueue
import nltk
try:
	nltk.data.find('tokenizers/punkt')
except:
	nltk.download('punkt')
from nltk.stem.snowball import SnowballStemmer
import math

cwd = os.getcwd() # get the current working directory

stoplist_filename       = "stoplist.txt" # stoplist filename
data_filename           = "arxiv-metadata.json" # data filename
inv_ind_filename        = "inv_ind" # inverted_index filename
norm_doc_filename       = "norm_doc.json" # vector norm document filename
final_inv_ind_filename  = "final_inv_ind.json"

stoplist_path       = os.path.join(cwd + "/stoplist/"                       , stoplist_filename)
data_path           = os.path.join(cwd + "/documents/data/"                 , data_filename)
norm_doc_path       = os.path.join(cwd + "/documents/norm_doc/"             , norm_doc_filename)
final_inv_ind_path  = os.path.join(cwd + "/documents/final_inverted_index/"  , final_inv_ind_filename)
inv_ind_path        = cwd + "/documents/inverted_index/" + inv_ind_filename
path_to_clean_1     = cwd + "/documents/norm_doc"
path_to_clean_2     = cwd + "/documents/inverted_index"
path_to_clean_3     = cwd + "/documents/final_inverted_index"
data_folder_path    = cwd + "/documents/data/"
datafile_size       = os.path.getsize(data_path)

class UBetterFixEverything():
    terminos_procesados = 0
    NUMBER_OF_DOCUMENTS = 0
    AUX_FILE_NUMBER = 1
    BLOCK_SIZE = 0 # bytes
    MAX_DOCUMENTS_DEFAULT = 1000

    def __init__(self):
        self.clean_directories()
        print("El dataset pesa: " + str(self.B_to_MB(datafile_size)) + " MB") # MB
        if 0: #dataset_size > 1000: # more than a GB
            pass
            # print("El archivo es muy pesado, se realiza slicing para generar más archivos de menor tamaño.") # cada archivo de 55 MB aprox.
            # exit_code_1 = os.system("split -b 53750k arxiv-metadata.json")
            # exit_code_2 = os.system("cat xa* > arxiv-metadata.json")
            # if not exit_code_1 and not exit_code_2: # successful
            #     os.remove(data_path)
            #     print("Slicing successfully")
            #     lista_auxiliar = os.listdir(data_folder_path)
            #     aprox_bloques_por_crear, aprox_block_size = self.approximation(os.path.getsize(data_folder_path + "/" + str(lista_auxiliar[0])))
            #     print("Se calcula la creación de aproximadamente " + str(round(aprox_bloques_por_crear,3)) + " archivos (bloques), con un block_size de " + str(round(aprox_block_size,3)) + " MB cada uno")
            #     self.BLOCK_SIZE = self.MB_to_B(aprox_block_size/100) 
            #     print("Actual block_size is: " + str(round(self.BLOCK_SIZE/1048576,3)) + " MB")
            # else: # abort
            #     print("Error, aborting slicing.")
            #     lista_auxiliar = os.listdir(data_folder_path)
            #     for file in lista_auxiliar:
            #         if str(file) == str(data_path):
            #             pass
            #         else:
            #             os.remove(data_folder_path + str(file))
            #     print("Abort successfully")
        else:
            aprox_bloques_por_crear, aprox_block_size = self.approximation(datafile_size)
            print("Se calcula la creación de aproximadamente " + str(round(aprox_bloques_por_crear,3)) + " archivos (bloques), con un block_size de " + str(round(aprox_block_size,3)) + " MB cada uno")
            self.BLOCK_SIZE = self.MB_to_B(math.log(aprox_block_size,10)) # to reduce the scale according to the approximation from the file size
            print("Actual block_size is: " + str(self.B_to_MB(self.BLOCK_SIZE)) + " MB")
        

    def approximation(self, datafile_size):
        aprox_bloques_por_crear = math.log(datafile_size, 2)
        aprox_block_size = self.B_to_MB((datafile_size / aprox_bloques_por_crear)) # MB
        return aprox_bloques_por_crear, aprox_block_size

    def MB_to_B(self, MB):
        return round(MB*1048576,3)

    def B_to_MB(self, B):
        return round(B/1048576,3)

    def procesamiento_palabra(self, word):
        new_word = ""
        abecedario = "abcdefghijklmnopqrstuvwxyz"
        for c in word:
            if c in abecedario:
                new_word = new_word + c
            else:
                new_word = new_word + '-' # in case of rare characters
        return new_word.strip('-') # we remove them



    def preprocesamiento(self, texto): # tokenization | Stopwords filter | Stemming

        # tokenizar
        palabras = nltk.word_tokenize(texto.lower())

        # crear el stoplist
        stoplist = []

        try:

            with open(stoplist_path, encoding='latin-1') as f:
                for line in f:
                    stoplist.append(line.strip())

            stoplist += [',', '!', '.', '?', '-', ';','"','¿',')','(','[',']','>>','<<','\'\'','``', '%', '$','_','-','{','}',"'"]
            
            # filtrar stopwords
            palabras_limpias = []
            for token in palabras:
                if token not in stoplist:
                    palabras_limpias.append(token)

            # process each clean word
            final_clean_words = []
            for clean_token in palabras_limpias:
                word = self.procesamiento_palabra(clean_token)
                if word != "": # else it was not a word at all
                    final_clean_words.append(word)

            # reducir palabras
            stemmer = SnowballStemmer(language='english')

            for i in range(len(final_clean_words)):
                final_clean_words[i] = stemmer.stem(final_clean_words[i])
            
            return final_clean_words

        except IOError:
            print("Problem reading: " + stoplist_filename + " path.")



    def insert_document_into_local_inverted_index(self, local_inverted_index, texto, doc_id):
    # the local inverted index has the following form: [keyword] -> {doc_id_1, freq}, {doc_id_2, freq}, ...
    # a dictionary of a dictionary of integers
        for token in texto:
            if token in local_inverted_index:
                if doc_id in local_inverted_index[token]: # more than 1 appearance in the same doc
                    local_inverted_index[token][doc_id] = local_inverted_index[token][doc_id] + 1
                else: # first appearance in the document, but not first appearance of the keyword
                    local_inverted_index[token][doc_id] = 1
            else: # first appearance of the keyword
                local_inverted_index[token] = {doc_id: 1} 



    def get_size(self, obj, seen=None):
        """Recursively finds size of objects"""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_size(v, seen) for v in obj.values()])
            size += sum([self.get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += self.get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_size(i, seen) for i in obj])
        return size



    def upload_block_to_disk(self, local_inverted_index):
        # sent
        sorted_keys = sorted(local_inverted_index.keys())
        try:
            with open(inv_ind_path + str(self.AUX_FILE_NUMBER) + ".json", 'a', encoding = "utf-8") as inv_ind_file:
                for keyword in sorted_keys:
                    inv_ind_file.write(json.dumps({keyword: local_inverted_index[keyword]}, ensure_ascii = False))
                    inv_ind_file.write("\n")
                inv_ind_file.close()
            local_inverted_index.clear()
            return 1
        except IOError:
            print("Problem reading: " +  str(self.AUX_FILE_NUMBER) + " path.")
            return 0



    def check_block_size(self, local_inverted_index):
        size = self.get_size(local_inverted_index)
        if size >= self.BLOCK_SIZE:
            print("uploading block " + str(self.AUX_FILE_NUMBER) + " to disk...")
            if(self.upload_block_to_disk(local_inverted_index)):
                print("block " + str(self.AUX_FILE_NUMBER) + " successfully uploaded.")
                self.AUX_FILE_NUMBER = self.AUX_FILE_NUMBER + 1
            else:
                print("Error uploading the block " + str(self.AUX_FILE_NUMBER) + " to disk.")



    def process_document_frequency(self, document_frequency, doc_id):
        sum = 0
        for key in document_frequency:
            sum = sum + ( math.log(1 + document_frequency[key], 10) * math.log(1 + document_frequency[key], 10) )
        sum = math.sqrt(sum)
        json_object = json.dumps({doc_id: sum}, ensure_ascii = False)
        return json_object


    def upload_document_frequency_to_disk(self, document_frequency):
        try:
            with open(norm_doc_path, 'a', encoding = "utf-8") as norm_file:
                norm_file.write(document_frequency)
                norm_file.write("\n")
            norm_file.close()
        except IOError:
            print("Problem reading: " + norm_doc_filename + " path.")
            return 0



    def clean_directories(self):
        clean_dir_1 = os.listdir(path_to_clean_1) # archivos de normas
        clean_dir_2 = os.listdir(path_to_clean_2) # archivo de indices invertidos
        clean_dir_3 = os.listdir(path_to_clean_3) # archivo con el final inverted index
        for file in clean_dir_1:
            os.remove(path_to_clean_1 + "/" + file)
        for file in clean_dir_2:
            os.remove(path_to_clean_2 + "/" + file)
        for file in clean_dir_3:
            os.remove(path_to_clean_3 + "/" + file)



    def initialize_list_of_buffers(self, buffers, active_files_index, priority_queue, buffers_line_number):
        for i in range(self.AUX_FILE_NUMBER):
            inv_ind = lc.getline(inv_ind_path + str(i+1) + ".json", 1).rstrip() # get first line from the auxiliar file. which is the keywords and a posting list of all the documents it appears, along with the document frequency of each document.
            if inv_ind != "":
                json_object = json.load(io.StringIO(inv_ind)) # load json object
                key = list(json_object.keys()) # get keywords from the json object
                buffer_format_list = [key[0], list(json_object.get(key[0]).items())] # list of keyword and its posting lists
                buffers.append(buffer_format_list) # append the line as a list [keyword, posting lists] to read_buffer (and the line of reading for each file)
    # buffers has 1 entry from each auxiliar file, they are in order so its getting the first from each auxiliar file
                buffers_line_number.append(2) # next line starting from 1
                priority_queue.put((buffers[i][0], i)) # append to priority_queue the keyword and the auxiliar file it is in.
                # print(buffers)
                active_files_index.append(i) # stores 0, 1, 2, 3, 4, 5, 6, ... (auxiliar files remaining)
            # print(buffers[i])
        


    def merge(self, buffers, active_files_index, priority_queue, buffers_line_number):
        aux_list = []
        try:
            with open(final_inv_ind_path, 'a', encoding="utf-8") as final_inv_ind:

                while not priority_queue.empty():
                    temp_inv_ind = {} # to store the new inverted_index keyword (but complete)
                    keyword, index_file = priority_queue.get() 
                    temp_inv_ind["keyword"] = keyword
                    temp_inv_ind["IDF"] = 0 # temporal inverted document frequency
                    temp_inv_ind["doc-ids"] = [] # list of doc id's

                    if buffers[index_file][0] == temp_inv_ind["keyword"]:
                        for posting_list in buffers[index_file][1]: # getting the posting list
                            temp_inv_ind["doc-ids"].append(posting_list)
    # replace the buffer read
                        inv_ind = lc.getline(inv_ind_path + str(index_file+1) + ".json", buffers_line_number[index_file]).rstrip() 
                        buffers_line_number[index_file] = buffers_line_number[index_file] + 1
                        if inv_ind == "": # end of the file has been reached
                            active_files_index.remove(index_file)
                            os.remove(inv_ind_path + str(index_file+1) + ".json")
                        else:
                            json_object = json.load(io.StringIO(inv_ind)) # load json object
                            key = list(json_object.keys()) # get keywords from the json object
                            buffers[index_file] = [key[0], list(json_object.get(key[0]).items())] # list of keyword and its posting lists
                            priority_queue.put((buffers[index_file][0], index_file)) # add next keyword to priority queue from document
                    else:
                        print("ERROR DE MAGNITUD DESPROPORCIONADA!")

                    while not priority_queue.empty():
                        other_keyword, other_index_file = priority_queue.get()
                        if other_keyword == keyword:
                            for posting_list in buffers[other_index_file][1]: # getting the posting list
                                temp_inv_ind["doc-ids"].append(posting_list) 
    # replace the buffer read
                            inv_ind = lc.getline(inv_ind_path + str(other_index_file+1) + ".json", buffers_line_number[other_index_file]).rstrip() 
                            buffers_line_number[other_index_file] = buffers_line_number[other_index_file] + 1
                            if inv_ind == "": # end of the file has been reached
                                active_files_index.remove(other_index_file)
                                os.remove(inv_ind_path + str(other_index_file+1) + ".json")
                            else:
                                json_object = json.load(io.StringIO(inv_ind)) # load json object
                                key = list(json_object.keys()) # get keywords from the json object
                                buffers[other_index_file] = [key[0], list(json_object.get(key[0]).items())] # list of keyword and its posting lists
                                priority_queue.put((buffers[other_index_file][0], other_index_file)) # add next keyword to priority queue from document
                        else:
                            # print("Se acabo el keyword " + str(keyword) + ", ahora estamos en " + str(other_keyword))
                            priority_queue.put((other_keyword, other_index_file))
                            break;

            # at this point, 1 keyword has been succesfully processed (it means we have the complete posting lists for that keyword)
            # to avoid many accesses to disk, we store it into a list and when it reaches a specific size, we upload it to disk (as a block)

                    temp_inv_ind["IDF"] = round(math.log(self.NUMBER_OF_DOCUMENTS/len(temp_inv_ind["doc-ids"]), 10), 5) # log_10(number_documents / document frequency)
                    # for inv_ind in aux_list:
                    final_inv_ind.write(json.dumps(temp_inv_ind, ensure_ascii=False)) # write to file
                    final_inv_ind.write("\n")
                    self.terminos_procesados = self.terminos_procesados + 1 # number of terms processed + 1
            final_inv_ind.close()

            print("Se procesaron " + str(self.terminos_procesados) + " terminos, en un total de " + str(self.NUMBER_OF_DOCUMENTS) + " documentos")
            return 1

        except IOError:
            print("Problem reading: " + final_inv_ind_filename + " path.")
            return 0



    def load(self, MAX = 5000):
    # clean the files (or delete the directory) from previous iterations
        # self.clean_directories()

        print("Processing only a total of " + str(MAX) + " documents. (parameter specified)")

        local_inverted_index = {}
        documents_frequencies_list = []
        try:
            with open(data_path, 'r') as f:
                for line in f: # a line is a document
                    document_frequency = {}
                    line = line.rstrip()
                    doc_object = json.load(io.StringIO(line)) # load the json object

    # separate the attributes needed (the id and the abstract) // maybe also the title
                    doc_id = doc_object.get("id") 
                    texto_procesado = self.preprocesamiento(doc_object.get("abstract"))
                    self.insert_document_into_local_inverted_index(local_inverted_index, texto_procesado, doc_id)

    # update the document_frequency
                    for token in texto_procesado:
                        if token in document_frequency:
                            document_frequency[token] = document_frequency[token] + 1
                        else:
                            document_frequency[token] = 1

    # insert into documents_frequencies_list, we do this to avoid accessing to disk each time a document is read, instead we send a block of frequency documents
                    document_frequency = self.process_document_frequency(document_frequency, doc_id)
                    # documents_frequencies_list.append(document_frequency)
                    # if self.get_size(documents_frequencies_list) >= self.BLOCK_SIZE:
                    #     for document_frequency in documents_frequencies_list:
                    self.upload_document_frequency_to_disk(document_frequency)  

    # checking local_inverted_index size, if it exceeds the block size, we store it into an auxiliar file, else, we continue
    # we avoid doing the cheking after every word insertion to avoid a lot of computation and to handle the 'leftovers' from a document (the id's)
                    self.check_block_size(local_inverted_index) # here the local_inverted_index is sent to disk and cleand or not

                    self.NUMBER_OF_DOCUMENTS = self.NUMBER_OF_DOCUMENTS + 1
                    # print("documents read: " + str(self.NUMBER_OF_DOCUMENTS))

                    # print(self.NUMBER_OF_DOCUMENTS)

                    # STOPPER: JUST FOR TESTING
                    if self.NUMBER_OF_DOCUMENTS >= MAX:
                        break

            f.close()
    # check the last block (it probably has not exceed the BLOCK_SICE limits)
            size = self.get_size(local_inverted_index)
            if size > 0:
                print("uploading block " + str(self.AUX_FILE_NUMBER) + " to disk...")
                if(self.upload_block_to_disk(local_inverted_index)):
                    print("block " + str(self.AUX_FILE_NUMBER) + " successfully uploaded.")
                else:
                    print("Error uploading the block " + str(self.AUX_FILE_NUMBER) + " to disk.")

    # at this points, all documents have been processed
            print("Se crearon " + str(self.AUX_FILE_NUMBER) + " archivos que contienen indices invertidos.")
            print("Se procesaron un total de " + str(self.NUMBER_OF_DOCUMENTS) + " documentos del dataset.")

    # merging process
    # essential variables 
            buffers = [] # this buffer reads from each inv_ind_file. It is a list of buffers
            priority_queue = PriorityQueue() # to keep the buffers ordered
            active_files_index = [] # keep track of the inv_ind files that are completed or not (to remove the files)
            buffers_line_number = []

            print("Merging files...")
            self.initialize_list_of_buffers(buffers, active_files_index, priority_queue, buffers_line_number) # reading the first line from each inv_ind_file
            if(self.merge(buffers, active_files_index, priority_queue, buffers_line_number)):
                print("The files were successfully merged.")
            else:
                print("Error merging the files.")
        except IOError:
            print("Problem reading: " + data_filename + " path.")


    def binary_search(self, query_doc_frequency, query_keyword_inv_ind):
        for keyword in query_doc_frequency:
            low = 1
            high = self.terminos_procesados
            while low <= high:
                mid = (low + high) // 2
                candidate = lc.getline(final_inv_ind_path, mid).rstrip()
                candidate_json = json.load(io.StringIO(candidate))
                token = candidate_json.get("keyword") # get token from the line read
                if token < keyword:
                    low = mid + 1
                elif token > keyword:
                    high = mid - 1
                else:
                    query_keyword_inv_ind[keyword] = dict(candidate_json)
                    break


    def tf_idf_weight_and_cosine_score(self, docs_ids, scores, query_keyword_inv_ind, query_doc_frequency):
        for keyword in query_keyword_inv_ind:
            query_tf_idf_weight = math.log(query_doc_frequency[keyword] + 1, 10) * query_keyword_inv_ind[keyword]["IDF"]
            for doc_id, frequency in query_keyword_inv_ind[keyword]["doc-ids"]:
                if doc_id not in scores:
                    scores[doc_id] = 0.0 # as a temp value, just to create the entry in the dictionary
                    docs_ids.append(doc_id)
                document_tf_idf_weight = math.log(frequency + 1, 10) * query_keyword_inv_ind[keyword]["IDF"]
                
                scores[doc_id] += query_tf_idf_weight * document_tf_idf_weight


    def score_normalization(self, docs_ids, scores):
        query_norms = {}
        try:
            with open(norm_doc_path, 'r', encoding="utf-8") as norm_doc:
                for line in norm_doc:
                    json_object = json.load(io.StringIO(line))
                    key = list(json_object.keys())
                    if key[0] in docs_ids:
                        query_norms[key[0]] = json_object.get(key[0])
                norm_doc.close()
            for doc_id in scores:
                scores[doc_id] = scores[doc_id] / query_norms[doc_id] # normalization

        except IOError:
            print("Problem reading: " + norm_doc_filename + " path.")

    def get_documents(self, scores, documents_retrieved, docs_to_read):
        try:
            with open(data_path, 'r', encoding="utf-8") as datafile:
                counter = 0
                for document in datafile:
                    json_object = json.load(io.StringIO(document))
                    counter = counter + 1
                    doc_id = str(json_object.get("id"))
                    if doc_id in scores:
                        documents_retrieved[doc_id] = json_object 
                    if counter >= docs_to_read:
                        break
                datafile.close()
        except IOError:
            print("Problem reading: " + data_filename + " path.")


    def score(self, query, docs_to_read, k):
        if self.NUMBER_OF_DOCUMENTS == 0:
            print("No documents were found. (0 documents loaded)")
            return 0
        # process query
        query = self.preprocesamiento(query)
        
        # some variables
        query_doc_frequency = {}
        query_keyword_inv_ind = {}
        docs_ids = []
        scores = {} # {doc_id: score}
        documents_retrieved = {}

        #create inverted index for query 
        for token in query:
            if token in query_doc_frequency:
                query_doc_frequency[token] = query_doc_frequency[token] + 1
            else:
                query_doc_frequency[token] = 1
        
        # now we search the keyword in the final inverted index
        print("Realizando busqueda binaria de los keyword en query.")
        self.binary_search(query_doc_frequency, query_keyword_inv_ind) # we get all posting lisit from keyword in query into query_keywords_inverted_index

        print("Calculando pesos TF_IDF y Cosine Score.")
        self.tf_idf_weight_and_cosine_score(docs_ids, scores, query_keyword_inv_ind, query_doc_frequency)

        print("Normalizando vectores.")
        self.score_normalization(docs_ids, scores)
 
        print("Ordenando scores.")
        scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse = True)) # order the scores in descending order
        docs_ids = list(scores.keys())

        # for i in range(10):
        #     print("scores[" + str(docs_ids[i]) + "] -> " + str(scores[docs_ids[i]]))

        print("Buscando documentos en el dataset.")
        self.get_documents(scores, documents_retrieved, docs_to_read)

        print("El query ha retornado un total de " + str(len(documents_retrieved)) + " documentos")
        
        return self.retrieve(k, docs_ids, scores, documents_retrieved)

    def retrieve(self, k, docs_ids, scores, documents_retrieved):
        k = int(k) # parsing, bc we receive strings from the frontend
        documents_to_retrieve = []

        for i in range(k):
            if i < len(docs_ids):
                temp_doc = {}
                temp_doc["id"] = docs_ids[i]
                temp_doc["score"] = scores[docs_ids[i]]
                temp_doc["submitter"] = documents_retrieved[docs_ids[i]].get("submitter")
                temp_doc["authors"] = documents_retrieved[docs_ids[i]].get("authors")
                temp_doc["title"] = documents_retrieved[docs_ids[i]].get("title")
                temp_doc["comments"] = documents_retrieved[docs_ids[i]].get("comments")
                temp_doc["journal-ref"] = documents_retrieved[docs_ids[i]].get("journal-ref")
                temp_doc["doi"] = documents_retrieved[docs_ids[i]].get("doi")
                temp_doc["report-no"] = documents_retrieved[docs_ids[i]].get("report-no")
                temp_doc["categories"] = documents_retrieved[docs_ids[i]].get("categories")
                temp_doc["license"] = documents_retrieved[docs_ids[i]].get("license")
                temp_doc["abstract"] = documents_retrieved[docs_ids[i]].get("abstract")
                temp_doc["versions"] = documents_retrieved[docs_ids[i]].get("versions")
                temp_doc["update_date"] = documents_retrieved[docs_ids[i]].get("update_date")
                temp_doc["authors_parsed"] = documents_retrieved[docs_ids[i]].get("authors_parsed")
                documents_to_retrieve.append(temp_doc)
            else:
                break

        return documents_to_retrieve


def main():
    docs_to_read = 1000
    instance = UBetterFixEverything()
    instance.load(docs_to_read) 
    query_1 = "A fully differential calculation in perturbative quantum chromodynamics is presented for the production of massive photon pairs at hadron colliders. All next-to-leading order perturbative contributions from quark-antiquark, gluon-(anti)quark, and gluon-gluon subprocesses are included, as well as all-orders resummation of initial-state gluon radiation valid at next-to-next-to-leading logarithmic accuracy. The region of phase space is specified in which the calculation is most reliable. Good agreement is demonstrated with data from the Fermilab Tevatron, and predictions are made for more detailed tests with CDF and DO data. Predictions are shown for distributions of diphoton pairs produced at the energy of the Large Hadron Collider (LHC). Distributions of the diphoton pairs from the decay of a Higgs boson are contrasted with those produced from QCD processes at the LHC, showing that enhanced sensitivity to the signal can be obtained with judicious selection of events."
    query_2 = "We systematically explore the evolution of the merger of two carbon-oxygen\n(CO) white dwarfs. The dynamical evolution of a 0.9 Msun + 0.6 Msun CO white\ndwarf merger is followed by a three-dimensional SPH simulation. We use an\nelaborate prescription in which artificial viscosity is essentially absent,\nunless a shock is detected, and a much larger number of SPH particles than\nearlier calculations. Based on this simulation, we suggest that the central\nregion of the merger remnant can, once it has reached quasi-static equilibrium,\nbe approximated as a differentially rotating CO star, which consists of a\nslowly rotating cold core and a rapidly rotating hot envelope surrounded by a\ncentrifugally supported disc. We construct a model of the CO remnant that\nmimics the results of the SPH simulation using a one-dimensional hydrodynamic\nstellar evolution code and then follow its secular evolution. The stellar\nevolution models indicate that the growth of the cold core is controlled by\nneutrino cooling at the interface between the core and the hot envelope, and\nthat carbon ignition in the envelope can be avoided despite high effective\naccretion rates. This result suggests that the assumption of forced accretion\nof cold matter that was adopted in previous studies of the evolution of double\nCO white dwarf merger remnants may not be appropriate. Our results imply that\nat least some products of double CO white dwarfs merger may be considered good\ncandidates for the progenitors of Type Ia supernovae. In this case, the\ncharacteristic time delay between the initial dynamical merger and the eventual\nexplosion would be ~10^5 yr. (Abridged)."
    query_2 = query_2.rstrip("\n")
    docs = instance.score(query_2, docs_to_read, 10)

    for i in docs:
        print(i)


main()


