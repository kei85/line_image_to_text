from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (
    MessageEvent,
    FollowEvent,
    TextMessage,
    ImageMessage,
    TextSendMessage,
)

from google.cloud import vision
from google.cloud.vision import types

from pathlib import Path
from subprocess import run
import random, string
import os

# Create your views here.
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
CHAT = "画像をお送りいただくと、画像内の文字をテキストで返信します。"

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

@csrf_exempt
def callback(request):
    signature = request.META["HTTP_X_LINE_SIGNATURE"]
    body = request.body.decode('utf-8')
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        HttpResponseForbidden()
    return HttpResponse('OK', status=200)

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='初めまして、Image to Textです!\n' + CHAT)
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=CHAT)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):

    img_d = Path(__file__).parent.parent / 'img'
    img_path = 'img/{}.jpg'.format(randomname(8))
    client = vision.ImageAnnotatorClient()
    content = line_bot_api.get_message_content(event.message.id)

    with open(img_path, 'wb') as fw:
            for c in content.iter_content():
                fw.write(c)

    with open(img_path, 'rb') as fr:
        c = fr.read()
        image = types.Image(content=c)
        response = client.document_text_detection(image=image)

    '''for pr in img_d.iterdir():
        if pr.is_file():
            pr.unlink()'''

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response.full_text_annotation.text)
    )
