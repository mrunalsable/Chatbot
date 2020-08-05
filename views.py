
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings
from dialogflow_lite.dialogflow import Dialogflow
from django.http import HttpResponse
from .models import Templog
from dictsearch.search import iterate_dictionary
import json
from django.db import connection
from django.views.generic import TemplateView
from random import randint
from chartjs.views.lines import BaseLineChartView

from django.contrib.auth.decorators import login_required


def my_custom_sql(parameters):
    print(parameters)
    with connection.cursor() as cursor:
        cursor.execute("select * from templog WHERE datetime = %s ", parameters)
        row = cursor.fetchall()
        print(row)
        jsonObj = json.dumps(row, indent=4, sort_keys=True, default=str)
        print(jsonObj)
    return row


#@csrf_exempt
#@require_http_methods(['POST'])
# def webhook(request):
#     return HttpResponse('Works like a charm!')


def convert(data):
    if isinstance(data, bytes):
        return data.decode('ascii')
    if isinstance(data, dict):
        return dict(map(convert, data.items()))
    if isinstance(data, tuple):
        return map(convert, data)

    return data

@login_required
@require_http_methods(['GET'])
def index_view(request):
    return render(request, 'app.html')

#@require_http_methods(['GET'])
# def foo(request):
#     time_series_json = json.dumps(items)
#     return render(request, "templates/chart.html", context={'time_series': time_series_json})


@require_http_methods(['POST'])
def chat_view(request):

    dialogflow = Dialogflow(**settings.DIALOGFLOW)
    #print(dialogflow)
    input_dict = convert(request.body)
    print("Input dictionary: ",input_dict)
    input_text = json.loads(input_dict)['text']
    print("Input text: ",input_text)
    responses = dialogflow.text_request(str(input_text))
    print("Response output: ",responses)

    abc = dialogflow._query(input_text)
    print(abc) #this is the diagnostic info of the dialogflow
    action = abc['result']['action']
    print("Action:"+action)

    #this helps to display the keys in the json
    #print(abc.keys())


   # check_dictitem = iterate_dictionary(abc,"result/parameters/date")

    #parameters = abc['result']['parameters']['date'];

   # if(check_dictitem is None):
    #    print("no date parameter")
   ## else:
     #   parameters = abc['result']['parameters']['date'];
     #   print(str(parameters))
        #my_custom_sql(parameters)

    print("------------")

    # people = Templog.objects.raw('SELECT * FROM templog WHERE datetime = %s', [parameters])
    # print(people)
    items= []
    for p in Templog.objects.all():
        items.append({'id':p.id, 'datetime':str(p.datetime), 'temperature':p.temperature, 'humidity':p.humidity})
    print(items)

    print("................")
    #print(json.dumps({'items':items}))

    #people2 = Person.objects.raw('SELECT id, first_name FROM myapp_person')
    # if "temperature" in input_text:
    #     print(json.dumps(dict, indent=4, sort_keys=True))

    check_dictitem1 = iterate_dictionary(abc, "result/parameters/on")
    # parameters = abc['result']['parameters']['on']


    if(check_dictitem1 is None):
        print("on ledlight parameter")

    else:
        print("lights are on")
        parameters = abc['result']['parameters']['on']
        os.system('GPIOZERO_PIN_FACTORY=pigpio PIGPIO_ADDR=192.168.1.105 python3.6 /home/swapnil/projects/hello.py')

        #add ur code here

    if request.method == "GET":
        # Return a method not allowed response
        data = {
            'detail': 'You should make a POST request to this endpoint.',
            'name': '/chat'
        }
        return JsonResponse(data, status=405)
    elif request.method == "POST":
        data = {
            'text': responses[0],
        }
        return JsonResponse(data, status=200)
    elif request.method == "PATCH":
        data = {
            'detail': 'You should make a POST request to this endpoint.',
            'name': '/chat'
        }

        # Return a method not allowed response
        return JsonResponse(data, status=405)

    elif request.method == "DELETE":
        data = {
            'detail': 'You should make a POST request to this endpoint.',
            'name': '/chat'
        }

        # Return a method not allowed response
        return JsonResponse(data, status=405)

# # working chart.js
class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels."""
        items= []
        for p in Templog.objects.all():
            items.append([ p.datetime])
        return items
        #return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Temperature", "humidity"]

    def get_data(self):
        """Return 3 datasets to plot."""
        #print(Templog.objects.all())
        items= []
        for p in Templog.objects.all():
            items.append([ p.temperature, p.humidity])

        items1= []
        for p in Templog.objects.all():
            items1.append(p.temperature)

        items2= []
        for q in Templog.objects.all():
            items2.append(q.humidity)

        items3 = [items1]+[items2]
        print(items3)
        return items3

line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = LineChartJSONView.as_view()
