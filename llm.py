#from transformers import GPT2LMHeadModel, GPT2Tokenizer #Para GPT2
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

#Inicializar el modelo (Flan-T5) y el tokenizer
def initialize_llm():
    #model_name = "google/flan-t5-large" #Aquí se define el nombre del modelo que se usará
    model_name = "mrm8488/distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es"
    #tokenizer = T5Tokenizer.from_pretrained(model_name)
    #model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    return model, tokenizer

#Obtener respuesta del modelo
def generate_response(prompt, context, model, tokenizer):
    #Establecer un token de padding
    #tokenizer.pad_token_id = tokenizer.eos_token_id
    #Codificar el texto de entrada
    inputs = tokenizer.encode_plus(prompt, context, return_tensors="pt")
    inputs_ids = inputs["input_ids"].tolist()[0]
    #Crear máscara de atención, esto evita confusión entre pad y eos token
    #attention_mask = inputs.ne(tokenizer.pad_token_id).long()
    #Generar la respuesta del modelo, pasar la atención
    outputs = model(**inputs)
    answer_start = torch.argmax(outputs.start_logits)
    answer_end = torch.argmax(outputs.end_logits) + 1
    #Decodificar la respuesta a texto y devolverla
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs_ids[answer_start:answer_end]))
    return answer
