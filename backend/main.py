import json
import linecache as lc
from operator import index
import os
import io
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
final_inv_ind_path  = os.path.join(cwd + "/documents/final_inverted_index"  , final_inv_ind_filename)
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

    def __init__(self):
        self.clean_directories()
        dataset_size = round(datafile_size/1048576,3)
        print("El dataset pesa: " + str(dataset_size) + " MB") # MB
        # if dataset_size > 1000: # more than a GB
        #     pass
        #     # print("El archivo es pesado, se realiza slicing para generar otros archivos con menor tamaño.")
        #     # number_slices, new_slices_size = self.data_slicing()
        #     # print("se crearon " + str(number_slices) + " archivos, con un tamaño aproximado de " + str(new_slices_size) + " MB cada uno.")
        # else:
        #     new_slices_size = dataset_size
        aprox_bloques_por_crear, aprox_block_size = self.approximation(datafile_size)
        print("Se calcula la creación de aproximadamente " + str(round(aprox_bloques_por_crear,3)) + " archivos (bloques), con un block_size de " + str(round(aprox_block_size,3)) + " MB cada uno")
        self.BLOCK_SIZE = self.MB_to_B(aprox_block_size/100) 
        print("Actual block_size is: " + str(round(self.BLOCK_SIZE/1048576,3)) + " MB")

#     def data_slicing(self):
#         number_slices = 0
#         new_slices_size = 0
# #you need to add you path here
#         with open(data_path , 'r', encoding='utf-8') as f1:
#             ll = [json.loads(line.strip()) for line in f1.readlines()]

#             #this is the total length size of the json file
#             print(len(ll))

#             #in here 2000 means we getting splits of 2000 tweets
#             #you can define your own size of split according to your need
#             size_of_the_split = 2000
#             total = len(ll) // size_of_the_split

#             #in here you will get the Number of splits
#             number_slices = total + 1
#             print(number_slices)

#             for i in range(number_slices):
#                 json.dump(ll[i * size_of_the_split:(i + 1) * size_of_the_split], open(data_folder_path + "data_split" + str(i+1) + ".json", 'w',encoding='utf8'), ensure_ascii=False, indent=True)
#                 print("archivo " + str(i) + " creado")

#             os.remove(data_path)

#             new_slices_size = os.path.getsize(data_folder_path + "data_split1.json")
#         return number_slices, new_slices_size

    def approximation(self, datafile_size):
        aprox_bloques_por_crear = math.log(datafile_size, 2)
        aprox_block_size = (datafile_size / aprox_bloques_por_crear)/1048576 # MB
        return aprox_bloques_por_crear, aprox_block_size

    def MB_to_B(self, MB):
        # 1 MB = 1048576 B
        return MB*1048576

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



    def score(self, query):
        if self.NUMBER_OF_DOCUMENTS == 0:
            print("No documents were found. (0 documents loaded)")
            return 0



def main():
    instance = UBetterFixEverything()
    instance.load(1000) 
    # query = "A fully differential calculation in perturbative quantum chromodynamics is presented for the production of massive photon pairs at hadron colliders. All next-to-leading order perturbative contributions from quark-antiquark, gluon-(anti)quark, and gluon-gluon subprocesses are included, as well as all-orders resummation of initial-state gluon radiation valid at next-to-next-to-leading logarithmic accuracy. The region of phase space is specified in which the calculation is most reliable. Good agreement is demonstrated with data from the Fermilab Tevatron, and predictions are made for more detailed tests with CDF and DO data. Predictions are shown for distributions of diphoton pairs produced at the energy of the Large Hadron Collider (LHC). Distributions of the diphoton pairs from the decay of a Higgs boson are contrasted with those produced from QCD processes at the LHC, showing that enhanced sensitivity to the signal can be obtained with judicious selection of events."
    # instance.score(query)

main()


