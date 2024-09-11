from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

#Inicializar el modelo (BLOOM 560-M) y el tokenizer
def initialize_llm():
    model_name = "bigscience/bloom-560m" #Aquí se define el nombre del modelo que se usará
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return model, tokenizer

#Obtener respuesta del modelo
def generate_response(prompt, model, tokenizer):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"],max_length=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
