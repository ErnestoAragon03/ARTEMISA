from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

#Inicializar el modelo (Flan-T5) y el tokenizer
def initialize_llm():
    #Definir el nombre del modelo que se usará
    model_name = "./LLM/Local/models--mrm8488--distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es/snapshots/dcadd98e59cd7ce8efd00cb4c61a024e2895b4c1" 
    #Inicializar tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, clean_up_tokenization_spaces=True)
    #Inicializar modelo
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    return model, tokenizer

#Obtener respuesta del modelo
def generate_response(question, context, model, tokenizer):
    max_length = 512    #Longitud máxima de tokens para el modelo
    inputs = tokenizer(question, context, return_tensors="pt", truncation=True, max_length=max_length)

    #Realizar predicción
    with torch.no_grad():
        outputs = model(**inputs)

    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))

    return answer
