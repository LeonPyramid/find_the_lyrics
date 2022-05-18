from word_treater.treatment import DictionaryTreater
import dictionary_organizer as do

dt = DictionaryTreater()
en_dict = do.read_dictionary("data/english_dict.txt")
treated_en = dt.treat_english_dictionary(en_dict)
do.write_dictionary("data/treated_en.txt",treated_en)