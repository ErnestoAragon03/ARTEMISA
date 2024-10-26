import openai

#Configurar API key de OpenAI
openai.api_key = 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

def ask_to_openai(prompt):
    try:
        answer = openai.Completion.create(
            engine="text-davinchi-003"
            prompt=prompt,
            max_tokens=150,     #Limitar palabras en la respuesta
            temperature=0.7     #Ajustar creatividad de respuesta
        )

        #Extraer y retornar respuesta
        print(answer)
        return answer.choices[0].text.strip()
    except Exception as e:
        print(f"Error al obtener respuesta de OpenAI: {e}")
        return None