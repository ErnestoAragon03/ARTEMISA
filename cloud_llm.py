from openai import OpenAI
from local_db import get_context
from local_db import get_personality
from logger_config import logger
from proxy import get_OpenAI_Key

client = OpenAI(
    #organization= 'org-BLKMXfWSb6Ytc2bIO4tIJ6EM',
    api_key = get_OpenAI_Key()

)

def ask_to_openai(prompt, user, email):
    logger.info("Llegando a cloud_llm")
    try:
        ###Crear personalidad###
        logger.info("Apunto de crear la personalidad...")
        personalidadActual = get_personality(email)
        logger.info("Si obtuvo la personalidad: ", personalidadActual)
        if personalidadActual[0] is not None:
            personalidadActual = personalidadActual[0]
            logger.info("Personalidad creada: %s", personalidadActual)
            personality = {"role": "system",
                            "content": personalidadActual
                            }
        else:
            logger.info("Personalidad no creada ()")
        ###Obtener contexto###
        context = get_context(email, consults_limit=10)
        if personalidadActual[0] is not None:
            ###Añadir la personalidad y la pregunta al contexto (así es más fácil de entregar a la API)###
            context.insert(0, personality)
            context.append({"role": "user", "content": prompt})
            logger.info("Contexto creado: %s", context)
        else: 
            ###Añadir solo la pregunta al contexto (así es más fácil de entregar a la API)###
            context.append({"role": "user", "content": prompt})
            logger.info("Contexto creado: %s", context)
    except Exception as e:
        logger.error("Error creando la personalidad: %s", e)
    try:
        if context:
            answer_raw = client.chat.completions.create(
                messages=context,
                model="gpt-4o"
            )
        else:
             answer_raw = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o"
            )
        answer = answer_raw.choices[0].message.content
        #Extraer y retornar respuesta
        logger.info("Respuesta obtenida: %s", answer)
        return answer
    except Exception as e:
        print(f"Error al obtener respuesta de OpenAI: {e}")
        logger.error("Error al obtener respuesta de OpenAI: %s", e)
        return None