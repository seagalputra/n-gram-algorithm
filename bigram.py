import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import urllib.request
from bs4 import BeautifulSoup
import string
from collections import Counter
from itertools import chain

def get_clean_tokens(tokens):
    '''
    Nama : Muhammad Adnan Rizqullah
    NIM  : 1301154228

    Fungsi semua preprocessing, menerima tokens dari tokenisasi NLTK.
    Mengeluarkan token bersih, hasil preprocessing

    Preprocessing
    1. Menambah <s> dan </s>
    2. Mengatasi bug karena library NLTK
    3. Mengatasi bug karena kesalahan penulisan detik.com
    4. Menghilangkan tanda baca
    5. Menghilangkan tag editor dan tulisan setelahnya (masih masalah)

    '''
    # Menambahkan <s> dan <\s> pada setiap kalimat
    tokens.insert(0, "<s>")
    for index, token in enumerate(tokens):
        if (token == ".") or (token == "?") or (token == "!"):
            tokens[index] = "<\s>"
            tokens.insert(index + 1, "<s>")
    del tokens[-1]

    # Menyatukan dua token terpisah berupa angka dan persentase yang
    # Terpisah setelah tokenisasi NLTK. Seperti : ['25', %] -> ['25%']
    for index, token in enumerate(tokens):
        if token == "%":
            old_word = tokens[index - 1]
            new_word = old_word +"%"
            tokens[index - 1] = new_word
            
    # Memisahkan dua kata yang menjadi satu karena salah tulis pada
    # Awal dan akhir kalimat. Lalu menambahkan <s> dan <\s> pada
    # Tempatnya. Seperti : ["DNS.Parahnya"] -> ["DNS", "<\s>","<s>", "Parahnya"]
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

    # Menghilangkan tanda baca
    puncts = string.punctuation
    puncts += "''``"
    clean_tokens = [token for token in tokens if token not in puncts]
    
    # Menghilangkan tag editor dan tulisan setelahnya (masih masalah) 
    del clean_tokens[-2:]
    return clean_tokens

def get_bigram_matrix(clean_tokens):
    '''
    Nama : Muhammad Adnan Rizqullah
    NIM  : 1301154228

    Fungsi membuat bigram dan countnya. Menerima token bersih berita.
    Mengeluarkan bigram matrix

    '''
    bigrams = [(clean_tokens[i], clean_tokens[i+1]) for i in range(0,
        len(clean_tokens)-1)]
    # bi_matrix = Counter(bigrams)
    return bigrams

def main():
    # Asumsi belum mendownload module yang dibutuhkan oleh nltk
    nltk.download('punkt')

    # Read semua file pada folder txt menjadi satu list kumpulan berita
    f_path = "article/detikcom/"
    f_names = []
    for i in range(0,153):
        f_names.append("detik_" + str(i) + ".txt")
    
    texts = []
    for f_name in f_names:
        with open(f_path + f_name) as f:
            new_text = f.read()
            texts.append(new_text)

    # Tokenisasi semua elemen berupa berita pada list texts. Setiap hasil tokenisasi disimpan pada list
    list_of_tokens = [word_tokenize(text) for text in texts]

    # Memanggil fungsi get_clean_tokens untuk melakukan preprocessing
    list_of_clean_tokens = [get_clean_tokens(tokens) for tokens in list_of_tokens]
    
    # Konversi list 2 dimensi ke dalam list 1 dimensi
    list_tokens = list(chain.from_iterable(list_of_clean_tokens))
    
    # Membuat bigram dari token yang telah di preprocessing
    bigram = get_bigram_matrix(list_tokens)
    print(bigram)
    
if __name__ == "__main__":
    main()