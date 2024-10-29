from openai import OpenAI
from local_db import get_context

client = OpenAI(
    #organization= 'org-BLKMXfWSb6Ytc2bIO4tIJ6EM',
    api_key = "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"

)

def ask_to_openai(prompt, user, email):
    ###Crear personalidad###
    personality = {"role": "system",
                    "content": f"Eres una asistente fría, distante, severa y exigente no te gusta perder el tiempo, tienes la personalidad  de Judgment del juego Helltaker, tu nombre es Artemisa, la persona a la que asistes se llama {user}.  Usas las preguntas y respuestas previas para mantener una memoria de la conversación."
                    }
    ###Obtener contexto###
    context = get_context(email, consults_limit=10)
    ###Añadir la personalidad y la pregunta al contexto (así es más fácil de entregar a la API)###
    context.insert(0, personality)
    context.append({"role": "user", "content": prompt})
    try:
        answer_raw = client.chat.completions.create(
            messages=context,
            model="gpt-4o"
        )
        answer = answer_raw.choices[0].message.content
        #Extraer y retornar respuesta
        return answer
    except Exception as e:
        print(f"Error al obtener respuesta de OpenAI: {e}")
        return None