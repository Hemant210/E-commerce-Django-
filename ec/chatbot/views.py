from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import openai
import json

# Your OpenAI API key (replace with your actual key or use environment variable)
openai.api_key = 'your_openai_api_key_here'

@csrf_exempt
def get_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            chatbot_reply = response.choices[0].message.content.strip()
            return JsonResponse({'response': chatbot_reply})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
