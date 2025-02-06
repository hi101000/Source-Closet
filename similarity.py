import spacy
nlp = spacy.load('en_core_web_md')

def similarity(text1:str, text2:str)->float:
    doc1 = nlp(text1)
    doc2 = nlp(text2)
    return doc1.similarity(doc2)

print(similarity("ISCOT 399 A British SIGINT intercept of a COMINTERN message regarding the gassing of Hungarian Jews in Auschwitz", "Jäger Report"))

print(similarity("Telegram", "ISCOT 399 A British SIGINT intercept of a COMINTERN message regarding the gassing of Hungarian Jews in Auschwitz"))