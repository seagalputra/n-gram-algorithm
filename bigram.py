import nltk
from nltk.tokenize import word_tokenize
import string
from collections import Counter
import re
from itertools import chain
from math import log10, exp
from functools import reduce
import argparse
nltk.download('punkt')

def get_texts():
    '''
    Fungsi untuk membaca semua file pada folder txt
    menjadi satu list kumpulan berita
    
    Input : null
    Output : List text berita
    '''

    f_path = "article/detikcom/"
    f_names = []
    for i in range(0,153):
        f_names.append("detik_" + str(i) + ".txt")

    texts = []
    for f_name in f_names:
        with open(f_path + f_name) as f:
            new_text = f.read()
            texts.append(new_text)
    return texts

def get_editor_notes(editor_txt):
    '''
    Fungsi mencari dan mendapatkan substring editor notes
    Menerima text yang berisikan editor notes
    Mengeluarkan editor notes
    '''

    match = re.search(r'\([a-z]+/[a-z]+\).*', editor_txt)
    if match:
        editor_notes = match.group()
    return editor_notes

def get_editor_free_text(editor_notes, dirty_txt):
    '''
    Fungsi menghilangkan editor notes dari sebuah text
    
    Input : Text kotor berisikan editor notes
    Output : Text bersih/bebas dari editor notes
    '''

    idx = dirty_txt.find(editor_notes)
    editor_free = dirty_txt[:idx]
    return editor_free

def remove_editor_notes(editor_free_texts, editor_texts):
    '''
    Prosedur untuk menghilangkan setiap editro notes dari
    semua berita pada sebuah list

    Input : List kotor berisikan berita kotor (editor notes)
    dan List kosong penampung hasil
    Output : List bersih berisikan berita bersih dari editor
    notes
    '''

    for index, text in enumerate(editor_texts):
        try:
            editor_notes = get_editor_notes(text)
        except UnboundLocalError:
            print("Editor notes not found!")
        else:
            editor_free_txt = get_editor_free_text(editor_notes, text)
            editor_free_texts.append(editor_free_txt)

def get_tokens(texts):
    '''
    Fungsi mengubah list text menjadi list token
    
    Input : List text berita
    Output : List token berita
    '''

    list_of_tokens = []
    for text in texts:
        tokens = word_tokenize(text)
        list_of_tokens.append(tokens)
    return list_of_tokens

def get_sentence_seperator_list(list_of_tokens):
    '''
    Fungsi menambah <s> dan </s> pada setiap token berita
    dari list token berita pada setiap kalimat

    Input : List token berita
    Output : List token berita dengan <s> dan </s>
    '''

    list_of_sentence_tokens = []
    for tokens in list_of_tokens:
        if (tokens[-1] != ".") and (tokens[-1] != "?") and (tokens[-1] != "!"):
            tokens.append(".")
    for tokens in list_of_tokens:
        tokens.insert(0, "<s>")
        for index, token in enumerate(tokens):
            if (token == ".") or (token == "?") or (token == "!"):
                tokens[index] = "<\s>"
                tokens.insert(index + 1, "<s>")
        del tokens[-1]
        list_of_sentence_tokens.append(tokens)
    return list_of_sentence_tokens

def fix_percentage_problem(list_of_sTokens):
    '''
    Memperbaiki bug dari tokenisasi NLTK berupa angka
    dan persentasenya yang terpisah

    Input : List token berita
    Output : List token berita yang diperbaiki
    '''

    list_of_pTokens = []
    for tokens in list_of_sTokens:
        for index, token in enumerate(tokens):
            if token == "%":
                old_word = tokens[index - 1]
                new_word = old_word +"%"
                tokens[index - 1] = new_word
        list_of_pTokens.append(tokens)
    return list_of_pTokens

def fix_dot_problem(list_of_pTokens):
    '''
    Memperbaiki bug dari kesalahan penulisan detik.com
    berupa dua kalimat yang tergabung dengan "."

    Input : List token berita
    Output : List token berita yang diperbaiki
    '''

    list_of_dTokens = []
    for tokens in list_of_pTokens:
        for index, token in enumerate(tokens):
            if "." in token:
                dot_index = token.find(".")
                before_dot = token[:dot_index]
                after_dot = token[dot_index + 1:]
                del tokens[index]
                tokens.insert(index, before_dot)
                tokens.insert(index + 1, after_dot)
                tokens.insert(index + 1, "<\s>")
                tokens.insert(index + 2, "<s>")
        list_of_dTokens.append(tokens)
    return list_of_dTokens

def remove_punctuation(list_of_dTokens):
    '''
    Menghilangkan token tanda baca dari setiap berita
    pada list token berita

    Input : List token berita
    Output : List token berita tanpa tanda baca
    '''

    list_of_puncTokens = []
    puncts = string.punctuation
    puncts += "''``"
    for tokens in list_of_dTokens:
        clean_tokens = [token for token in tokens if token not in puncts]
        list_of_puncTokens.append(clean_tokens)
    return list_of_puncTokens

def make_lowercase(list_of_puncTokens):
    '''
    Fungsi untuk mengubah seluruh string menjadi lowecase
    '''

    list_of_cleanT = []
    for tokens in list_of_puncTokens:
        tmp = []
        for token in tokens:
            tmp.append(token.lower())
        list_of_cleanT.append(tmp)
    return list_of_cleanT

def get_clean_tokens(texts):
    '''
    Fungsi semua preprocessing, menerima tokens hasil tokenisasi NLTK.
    Mengeluarkan token bersih, hasil preprocessing
    '''

    # 1. Menghilangkan editor notes dari semua berita
    editor_free_texts = []
    remove_editor_notes(editor_free_texts, texts)
    
    # 2. Tokenisasi semua teks berita
    list_of_tokens = get_tokens(editor_free_texts)
    
    # 3. Menambahkan <s> dan <\s> pada setiap kalimat
    list_of_sTokens = get_sentence_seperator_list(list_of_tokens) 

    # 4. Menyatukan dua token terpisah berupa angka dan persentase yang
    # Terpisah setelah tokenisasi NLTK. Seperti : ['25', %] -> ['25%']
    list_of_pTokens = fix_percentage_problem(list_of_sTokens)
            
    # 5. Memisahkan dua kata yang menjadi satu karena salah tulis pada
    # Awal dan akhir kalimat. Lalu menambahkan <s> dan <\s> pada
    # Tempatnya. Seperti : ["DNS.Parahnya"] -> ["DNS", "<\s>","<s>", "Parahnya"]
    list_of_dTokens = fix_dot_problem(list_of_pTokens)
    
    # 6. Menghilangkan tanda baca
    list_of_puncTokens = remove_punctuation(list_of_dTokens)
    
    # 7. Mengubah semua kata menjadi lowercase
    list_of_cleanT = make_lowercase(list_of_puncTokens)
    return list_of_cleanT

# Fungsi membuat bigram dan countnya. Menerima token bersih berita
# Mengeluarkan bigram matrix

def get_bigram_matrix(clean_tokens):
    '''
    Fungsi membuat bigram dan countnya. Menerima token bersih berita
    Mengeluarkan bigram matrix
    '''

    bigrams = []
    for i in range(len(clean_tokens) - 1 ):
        bigrams.append((clean_tokens[i], clean_tokens[i + 1]))
    bi_matrix = Counter(bigrams)
    return(bi_matrix)

def get_sentence_probability(sentence, list_token, list_bigram):
    '''
    Fungsi menghitung probabilitas kemunculan sebuah kalimat

    Input : Kalimat
    Output : Probabilitas dalam decimal
    mengeluarkan nilai 0 jika terdapat kata pada kalimat yang tak
    dikenal. Dengan implementasi Laplace
    '''

    test = word_tokenize(sentence.lower())
    punct = string.punctuation
    test_clean = [token for token in test if token not in punct]
    test_bigram = [(test_clean[i], test_clean[i+1]) for i in range(len(test_clean) - 1)]
    start = "<s>"
    end = "<\s>"
    test_bigram.insert(0, (start, test_bigram[0][0]))
    test_bigram.append((test_bigram[-1][-1], end))

    count_token = dict(Counter(list_token))
    count_bigrams = dict(list_bigram)

    probability = 0
    log_probability = 0
    # Implementasi prediksi kumunculan kalimat + Laplace
    for tup in test_bigram:
        try:
            pembagi = count_token[tup[0]] + len(count_token)
        except KeyError:
            pembagi = len(count_token)
            pembilang = 1
            log_probability = log10(pembilang/pembagi)
        else:
            try:
                pembilang = count_bigrams[tup] + 1
            except KeyError:
                pembilang = 1
                log_probability = log10(pembilang/pembagi)
            else:
                log_probability = log10(pembilang/pembagi)
    probability = exp(log_probability)
    return probability

def get_next_word(sentence, list_bigram):
    '''
    Fungsi memprediksi kata selanjutnya
    
    Input : Kalimat
    Output : Kata selanjutnya
    '''

    punct = string.punctuation.replace("%", "")
    clean_token = [token for token in word_tokenize(sentence.lower()) if token not in punct]
    last_word = clean_token[-1]

    max_value = -1
    word_prediction = ""
    idx = 0
    count_bigrams = dict(list_bigram)

    for tup, count in count_bigrams.items():
        if last_word == tup[0]:
            if tup[1] != "<\s>":
                if max_value < count:
                    max_value = count
                    word_prediction = tup[1]
    if word_prediction == "":
        return "Error, kata terakhir tak dikenal"
    else:
        return word_prediction

def get_probability(word, prev_word, length_corpus, list_token, list_bigrams):
    '''
    Fungsi untuk menghitung probabilitas dari suatu kalimat
    '''
    count_token = dict(Counter(list_token))
    count_bigrams = dict(Counter(list_bigrams))
    
    try:
        return (count_bigrams[word] + 1) / (count_token[prev_word] + length_corpus)    
    except KeyError:
        try:
            return 1 / (count_token[prev_word] + length_corpus)
        except Exception:
            return 0

def get_bigram(clean_tokens):
    '''
    Fungsi untuk membuat bigram
    '''
    bigrams = []
    for i in range(len(clean_tokens)-1):
        bigrams.append((clean_tokens[i], clean_tokens[i+1]))
    return bigrams

def get_perplexity(sentences, list_final_tokens, bigram_matrix):
    '''
    Fungsi untuk menghitung perplexity dari suatu kalimat
    Input : Kalimat
    Output : Perplexity dari kalimat tersebut
    '''
    n_root = lambda number, root: number ** (1/root)
    count_token = dict(Counter(list_final_tokens))
    words = word_tokenize(sentences)
    bigram = get_bigram(words)
    length_corpus = len(count_token)

    probability = [get_probability(bigram[i], bigram[i][0], length_corpus, list_final_tokens, bigram_matrix) for i in range(len(bigram))]

    non_zero_probability = list(filter(lambda x: x != 0, probability))
    inv_probability = []
    for i in range(len(non_zero_probability)):
        inv_probability.append(1/non_zero_probability[i])
        temp_perplexity = reduce(lambda x, y: x*y, inv_probability)
        perplexity = n_root(temp_perplexity, len(words))
    
    return perplexity

def main():
    texts = get_texts()
    list_of_cleanT = get_clean_tokens(texts)

    list_final_tokens = list(chain.from_iterable(list_of_cleanT))
    bigram_matrix = get_bigram_matrix(list_final_tokens)

    parser = argparse.ArgumentParser()
    parser.add_argument("kalimat", help="Kalimat yang akan diprediksi kata berikutnya.")
    parser.add_argument("-prob", "--probability", help="Menghitung probabilitas dari kalimat input", action="store_true")
    parser.add_argument("-plex", "--perplexity", help="Menghitung perplexity dari suatu kalimat", action="store_true")
    args = parser.parse_args()
    word_prediction = get_next_word(args.kalimat, bigram_matrix)
    print(word_prediction)

    if args.probability:
        probabilitas = get_sentence_probability(args.kalimat, list_final_tokens, bigram_matrix)
        print(probabilitas)
    
    if args.perplexity:
        perplexity = get_perplexity(args.kalimat, list_final_tokens, bigram_matrix)
        print(perplexity)

if __name__ == "__main__":
    main()