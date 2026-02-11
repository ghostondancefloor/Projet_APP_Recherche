import os
from sentence_transformers import SentenceTransformer
from transformers import BartTokenizer, BartForConditionalGeneration, T5Tokenizer, T5ForConditionalGeneration

# stocker les modèles dans l'image Docker
BASE_PATH = "./models_local"
EMBED_PATH = f"{BASE_PATH}/embedding"
BART_PATH = f"{BASE_PATH}/bart"
T5_PATH = f"{BASE_PATH}/t5"

def download_and_save():
    print(f"BUILD DOCKER : Téléchargement des modèles vers {BASE_PATH}")
    os.makedirs(BASE_PATH, exist_ok=True)

    # modèle embedding :
    print("Téléchargement SentenceTransformer...")
    model_emb = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    model_emb.save(EMBED_PATH)
    
    # modèle BART :
    model_name = "sshleifer/distilbart-cnn-12-6"
    print(f"Téléchargement BART ({model_name})...")
    
    tokenizer_bart = BartTokenizer.from_pretrained(model_name)
    model_bart = BartForConditionalGeneration.from_pretrained(model_name)
    
    tokenizer_bart.save_pretrained(BART_PATH)
    model_bart.save_pretrained(BART_PATH)


    # modèle T5 :
    model_name_t5 = "google/flan-t5-base" 
    print(f"Téléchargement T5 ({model_name_t5})...")
    
    tokenizer_t5 = T5Tokenizer.from_pretrained(model_name_t5)
    model_t5 = T5ForConditionalGeneration.from_pretrained(model_name_t5)
    
    tokenizer_t5.save_pretrained(T5_PATH)
    model_t5.save_pretrained(T5_PATH)

    print("Téléchargement terminé")

if __name__ == "__main__":
    download_and_save()