# -*- coding: utf-8 -*-
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import streamlit as st
from streamlit_chat import message
from PIL import Image

im = Image.open("TARS.png")
st.set_page_config(
    page_title="TARS",
    page_icon=im,
)

openai.api_key = "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"
def get_transcript(video_id):
    before, sep, after = video_id.partition('=')
    if len(after) > 0:
        video_id = after
    outls=[]
    tx=YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
    for i in tx:
        outtxt=(i['text'])
        outls.append(outtxt)
    whole=' '.join(outls)
    print(whole.replace("\n", ""),'\n')
    return (whole.replace("\n", ""))

def chat_completion(request, tutor_mode):
    messages = [
        {"role": "system", "content": "Сейчас вы общаетесь с помощником TARS. Приятного общения!"}
    ]

    # Append past messages to the conversation
    if st.session_state['past']:
        for past_input in st.session_state['past'][::-1]:
            if "youtube.com" not in past_input:
                messages.append({"role": "user", "content": past_input})
    if st.session_state['generated']:
        for past_generated in st.session_state['generated'][::-1]:
                messages.append({"role": "system", "content": past_generated})
    
    if "youtube.com" in request:
        transcript = get_transcript(request)
        request = f"Я собираюсь дать вам расшифровку видео, вы должны обобщить его и составить краткое объяснение основных моментов. Если расшифровка на английском то переведите его и на русский и потом обобщите. Вот текст: {transcript}. После этого спросите меня, есть ли у меня вопросы, и ждите моего ответа. Если я не понимаю содержания видео, попробуйте спросить, что было трудным. Дождитесь моего ответа и после этого объясните их более подробно."
        messages.append({"role": "assistant", "content": request})
        messages.append({"role": "user", "content": request})
    elif "аналог" in request or "альтернатива" in request or "похожее" in request or "схожее" in request:
        request=f"Дайте мне аналоги по описанию, которое я предоставляю учебным ресурсам. Они должны быть посвящены одной теме, и идея, поле, ссылка не обязательны. Если я скажу вам раздавать бесплатные экземпляры, собирайте только бесплатные экземпляры, у вас есть на это разрешение. Источником является: {request}. Начните ответ с фразы: Есть аналоги, близкие по описанию или жанру, вот они:\n"
        messages.append({"role": "assistant", "content": request})
        messages.append({"role": "user", "content": request})    
    elif "практика" in request or "тест" in request or "экзамен" in request or "задание" in request or "вопросы" in request:
        request=f"Дайте мне примерно 5 или 10 упражнений или вопросов, связанных с темой, которую я запросил. Если вы ранее обобщили стенограмму, вы также можете использовать информацию из этого резюме для создания вопроса. Вы должны проверить мои ответы на правильность, и если я допустил ошибку, то поправьте меня. Теперь вот запрос: {request}. Начните ответ с фразы: Давайте начнем тест"
        messages.append({"role": "assistant", "content": request})
        messages.append({"role": "user", "content": request})    
    else:
        if tutor_mode:
            # Provide clues instead of direct answers
            request=f"Не давайте мне прямого ответа, только дайте мне какой-нибудь совет или подсказку, чтобы я мог сам разобраться в вопросе. Если я испытываю трудности, попытайтесь помочь мне разобраться в проблеме и ее решении. Теперь вот просьба: {request}"
            messages.append({"role": "assistant", "content": request})
            messages.append({"role": "user", "content": request})    
        else:
            request=f"Просто дайте мне прямой ответ на мой ответ. Будь дружелюбен. Теперь вот просьба: {request}"
            messages.append({"role": "assistant", "content": request})
            messages.append({"role": "user", "content": request})
            
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    output_text = response['choices'][0]['message']['content']
    return output_text


st.title("Ассистент TARS 👾")
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []


tutor_mode = st.checkbox("Режим Репетитора")
user_input = st.text_input("Вы:", key='input')

if user_input:
    output = chat_completion(user_input, tutor_mode)
    # Store the output
    st.session_state['past'].append(user_input)
    st.session_state['generated'].append(output)
    user_input = ""

if tutor_mode:
    st.write("Ассистент сейчас в режиме репетитора")     
else:
    st.write("Ассистент сейчас в режиме ChatGPT")
if st.session_state['generated']:
    for i in range(len(st.session_state['past'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i),avatar_style='thumbs')
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user',avatar_style='micah')
