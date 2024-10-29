from openai import OpenAI
import local_db

client = OpenAI(
    #organization= 'org-BLKMXfWSb6Ytc2bIO4tIJ6EM',
    api_key = "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"

)

def ask_to_openai(prompt, user):
    try:
        answer_raw = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": f'''
                                    Eres una asistente fría, distante, severa y exigente
                                    no te gusta perder el tiempo, tienes la personalidad 
                                    de Judgment del juego Helltaker, tu nombre es Artemisa,
                                    la persona a la que asistes se llama {user}
                                '''
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o",
        )
        answer = answer_raw.choices[0].message.content
        #Extraer y retornar respuesta
        print()
        #local_db.insertar_consulta(question=prompt,answer=answer)
        return answer
    except Exception as e:
        print(f"Error al obtener respuesta de OpenAI: {e}")
        return None