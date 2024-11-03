from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
import os
from logger_config import logger

#Inicializar el modelo (Flan-T5) y el tokenizer
def initialize_llm():
    logger.info("Llegando a local_llm.py")
    try:
        #Determina la ruta base, donde está ubicado el script actual
        base_path = os.path.dirname(os.path.abspath(__file__))
        logger.info("Base_path: %s", base_path)
        # Rutas relativas al modelo y archivo de configuración
        #Definir el nombre del modelo que se usará
        model_path = os.path.join(base_path, 'LLM', 'Local', 'models--mrm8488--distill-bert-base-spanish-wwm-cased-finetuned-spa-squad2-es')
        logger.info("Model path: %s", model_path)
        #Inicializar tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path, clean_up_tokenization_spaces=True)
        #Inicializar modelo
        model = AutoModelForQuestionAnswering.from_pretrained(model_path)
        return model, tokenizer
    except Exception as e:
        logger.error("Error en initialize_llm: %s", e)

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
