import os
import requests
from statistics import median, stdev
import plotly.graph_objects as go
from collections import Counter


# API_URL = "http://0.0.0.0:5000"
API_URL = "https://research.ludoeducation.fr"

def get_student_list():
    '''Load student id from ENDPOINT api'''
    endpoint = "/admin/students"
    uri = API_URL + endpoint
    print(uri)
    r = requests.get(uri)
    data = r.json()
    return [s["_id"] for s in data["students"] if s["group"]!= "guest"]


def get_student_timespent_subject(student, subject="numbers"):
    endpoint = "/activity/students/{}/subjects/{}".format(student, subject)
    uri = API_URL + endpoint
    print(uri)
    r = requests.get(uri)
    data = r.json()
    if "data" in data:
        return round(data["data"][0]["timespent_sec"]/60, 0)
    else:
        #if no data this means that we have no data for this student on this subject
        return None

def get_classroom_timespent_subject(classroom, subject="numbers"):
    '''Load the timespent for each student of a classroom'''
    endpoint = "/activity/classroom/{}/subjects/{}".format(classroom, subject)
    uri = API_URL + endpoint
    print(uri)
    r = requests.get(uri)
    data = r.json()
    if "data" in data:
        return round(data["data"][0]["timespent_sec"]/60, 0)
    else:
        #if no data this means that we have no data for this classroom on this subject
        return None

def get_timespent_subject(subject="numbers"):
    endpoint = "/activity/subjects/{}".format(subject)
    uri = API_URL + endpoint
    print(uri)
    r = requests.get(uri)
    data = r.json()
    lines = sorted([(x["student"], x["timespent_min"]) for x in data["activity"] if x["timespent_min"] is not None ], key=lambda x:x[1])
    x,y = zip(*lines)  
    return x,y

def get_timespent_dataset(dataset="numbers"):
    endpoint = "/activity/datasets/{}".format(dataset)
    uri = API_URL + endpoint
    print(uri)
    r = requests.get(uri)
    data = r.json()
    # print(data)
    lines = sorted([(x["student"], x["timespent_min"]) for x in data["activity"] if x["timespent_min"] is not None ], key=lambda x:x[1])
    x,y = zip(*lines)  
    return x,y

def show_stats(x,y, datatype, name):
    nb_student = len(x)
    less_five_minute = [z for z in y if z < 5]
    more_two_hour = [z for z in y if z > 120]
    between_one_and_two = [z for z in y if z > 60 and z <= 120]
    more_than_two = [z for z in y if z > 120]
    print("============")
    print(datatype, ':', name)
    print("Population:", nb_student)
    print("% of student who played less than 5 min", (len(less_five_minute)/nb_student)*100, "i.e ", len(less_five_minute))
    print("% of student who played between 1 hour and 2 hours", (len(between_one_and_two)/nb_student)*100, "i.e ", len(between_one_and_two))
    print("% of student who played more than 2 hours",(len(more_two_hour)/nb_student)*100, "i.e ", len(more_two_hour))

def build_histogram(x,y,datatype="subject",name='numbers'):
    fig = go.Figure(data=[go.Bar(
            x=x, y=y,
            # text=["Elève "+str(s) for s in x],
        )])
    fig.update_layout(xaxis_type='category',
                  title_text='Timespent in minutes by student on {} `{}`'.format(datatype, name))
    # fig.update_yaxes(tick0=15, dtick=15)
    fig.show()

def build_frequency_histogram(y, datatype="subject",name='numbers'):
    freq = Counter(y)
    # print(freq)
    freq_l = sorted(list(counter.items()), key=lambda x: x[1])
    x,y = zip(freq_l)
    fig = go.Figure(data=[go.Bar(
            x=list(freq.keys()), y=list(freq.values()),
            # text=["Elève "+str(s) for s in x],
        )])
    fig.update_layout(xaxis_type='category',
                  title_text='Frequency of student timespent in minutes on {} `{}`'.format(datatype, name))
    # fig.update_yaxes()
    fig.show()

    
# def build_histogram_by_student(subject="numbers"):
#     x = get_student_list()
#     y = [get_student_timespent_subject(s, subject) for s in x]
#     text = ["Eleve {}".format(s) for s in x] 
#     # Use textposition='auto' for direct text
#     fig = go.Figure(data=[go.Bar(
#             x=text, y=y,
#             text=["Elève"+str(s) for s in x],
#         )])
#     fig.update_layout(xaxis_type='category',
#                   title_text='Timespent in minutes by student on subject numbers')
#     fig.update_yaxes(tick0=0, dtick=60)
#     fig.show()


if __name__ == "__main__":
    datatype = "subject"
    subject = "letters"
    
    x,y = get_timespent_subject(subject="letters")
    show_stats(x,y, datatype, subject)
    build_histogram(x,y, datatype, subject)
    
    x,y = get_timespent_subject(subject="numbers")
    show_stats(x,y, datatype, subject=numbers)
    build_histogram(x,y, datatype, subject="numbers")   
    build_frequency_histogram(y, datatype, "numbers")
    