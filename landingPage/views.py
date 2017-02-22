from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from mysql import connector
import datetime
import pytz
from _datetime import date
from django.template.context import RenderContext
from django.template import Template
from django.template import Context
import django
def index(responce):
    logArrival(responce)
    page = ""
    page += getHeader("Landing Page","Utility",responce)
    page += getTitleBlock("Utility","Landing Page",responce)
    page += getRegisterBlock(responce)
    page += getDescription()
    page += getUpdatesDisplay()
    page += getQuestions(responce)
    return HttpResponse(page)
def getHeader(page, site,responce):
    parameters = {'page' : page, 'site' : site}
    template = loader.get_template("modules/header.html");
    return template.render(parameters,responce) 
def getTitleBlock(site, page,responce):
    parameters = {'page' : page, 'site' : site}
    template = loader.get_template("modules/title.html");
    return template.render(parameters,responce)
def getConnection(DBName,username_,password_,port_,host_):
    return connector.Connect(user=username_,password=password_,database=DBName,host=host_,port=port_)
def getQuery(query, connection = "",hasResult = True):
    isNewEngine = False
    if connection == "":
        connection = getConnection("landingpage","pma","mQqXmT6TsNhuMa9Y","3306","localhost")#patchfkj55
        isNewEngine = True
    cursor = connection.cursor(buffered=True)
    cursor.execute(query)
    output = ""
    if hasResult:output = cursor.fetchall()
    else:connection.commit()
    cursor.close()
    if isNewEngine:connection.close()
    return output
def getRegisterBlock(responce):
    registeredEmail = responce.POST.get("registerEmail")
    extraPrompt = ""
    if isinstance(registeredEmail, str):
        if registeredEmail.count('@') == 1 and registeredEmail.count('.') >= 1:
            emailValid = True
            emailComponents = registeredEmail.split('@')
            domainComponents = emailComponents[1].split('.')
            emailComponents.remove(emailComponents[1])
            for component in domainComponents:
                emailComponents.append(component)
            for component in emailComponents:
                emailValid = len(component) > 1
                if not emailValid:
                    extraPrompt = "Email does not exist"
                    break
            if emailValid:
                try:
                    email = getQuery("SELECT * FROM followers WHERE email='{}'".format(registeredEmail))
                    if len(email) != 0:
                        emailValid = False
                        extraPrompt = "Email is already registered"
                except():
                    pass;
                if emailValid:
                    datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                    print("INSERT INTO followers (email,date) VALUES ('{}','{}')".format(registeredEmail,datetime.datetime.now()))
                    getQuery("INSERT INTO followers (email,date) VALUES ('{}','{}')".format(registeredEmail,datetime.datetime.now()),hasResult = False)
                    extraPrompt = "Thanks for Registering"
        elif(len(registeredEmail) > 0): extraPrompt = "Email format is incorrect"
    params = {"directory": responce.get_full_path(),"extraPrompt":extraPrompt}
    showreg = ""
    if extraPrompt != "":showreg = "<script>show('register')</script>"
    template = loader.get_template("modules/registerBlock.html")
    return template.render(params,responce)+showreg
def getDescription(n = 0):
    nIsZero = n == 0
    descriptions = getQuery("SELECT * FROM testcontent ORDER BY `Id` DESC")
    for (id,desc) in descriptions:
        if nIsZero:n = id
        if int(id) == int(n):
            descHyperlinks = desc.split("%a")
            area = ""
            for i in range(1,len(descHyperlinks),2):
                linkId = descHyperlinks[i].split("$i")[1]
                if linkId != str(id):content = getDescription(linkId)
                area = "<button id='revealDesc:{}' onclick=\"show('description:{}')\">{}</button>{}".format(linkId,linkId,descHyperlinks[i].split("$i")[0],content)
                descHyperlinks[i] = area
            desc = ""
            for part in descHyperlinks:
                desc += part
                if not nIsZero:desc += "<button id='hide:{}' onclick=\"collapse('description:{}')\" class=\"boardered\">-</button>".format(id,id)
            styleClass = "description"
            if nIsZero: styleClass += " mainDesc mainSec"
            else: desc += "<script>collapse('description:{}')</script>".format(id)
            return "<div id='description:"+str(id)+"' class='"+styleClass+"'>"+desc+"</div>"
    return "description not found: id:({}) does not exist </br>".format(n)
def getUpdatesDisplay():
    updates = getQuery("SELECT * FROM updates ORDER BY date DESC")
    block = "<div class=\"mainSec\"><iframe id=\"updates\">"
    data = "<script>iframeInsert('updates','<sec class=\"updateBlock\"><h3 class=\"fixed\">Updates</h3></br><ul>"
    for (id, date, title, desc) in updates:
        data += "<li><h3>{}</h3><h5>{}</h5><p>{}</p></li>".format(title,date,desc)
    data += "</sec>"
    block += "</iframe></div>{}</ul>')</script>".format(data)
    return block
def getQuestions(response):
    module = "<ul id=\"poll\" class=\"mainSec\"><form action=\""+response.get_full_path()+"\" method=\"post\" value=\"submited\" id=\"pollForm\"><h3>Questionnaire</h3><input type='hidden' name='csrfmiddlewaretoken' value='{}'>".format(django.middleware.csrf.get_token(response))
    connection = getConnection("landingpage","pma","mQqXmT6TsNhuMa9Y","3306","localhost")
    questions = getQuery("SELECT * FROM questions",connection)
    for (qId,desc,type) in questions:
        if isinstance(response.POST.get("q:{}".format(qId)), str):
            datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            getQuery("INSERT INTO qanswers (qId,date,value) VALUES ({},'{}','{}')".format(qId,datetime.datetime.now(),response.POST.get("q:{}".format(qId))), connection, hasResult=False)
        module += "<li id=\"question:{}\"><p>{}</p>".format(qId,desc)
        if type == "textbox":
            parameters = getQuery("SELECT * FROM `qparameters` WHERE `qId`= {}".format(qId),connection)
            exceptions = []
            minrange = 0
            maxrange = -1
            for (id,qId,type,value) in parameters:
                if type == "Min":minrange = value
                elif type == "Max":maxrange = value
                elif type == "value":exceptions.append(value)
            module+= "<script>getSubmitParameters({},'{}',{})</script>".format(qId,exceptions,minrange)
            module+= "<input type=\"text\" maxlength=\"{}\" name=\"q:{}\" id=\"q:{}\">".format(maxrange,qId,qId)
        else:  
            parameters = getQuery("SELECT value FROM `qparameters` WHERE `qId` = {} && type='value'".format(qId),connection)
            options = []
            for value in parameters:
                options.append(value)
            if type == "dropbox":
                module += "<select name=\"q:{}\" id=\"q:{}\">".format(qId,qId)
                for value in parameters:
                    module += "<option value=\"{}\">".format(value)
                module +="</select>"
            else:
                for value in parameters:
                    module += "<input type=\"{}\" name=\"q:{}\" value=\"{}\" id=\"q:{}\">".format(type,qId,value,qId)
        module += "</li>"
    module += "</form><button onclick=\"checkSubmitPoll()\" id=\"qSubmit\">Submit</button></ul>"
    connection.close()
    return module
def arrayToString(array):
    newString = ""
    for item in array:
        newString+= item
    return newString
def logArrival(response):
    ip = ""
    x_forwarded_for = response.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for#.split(',')[0]
    else:
        ip = response.META.get('REMOTE_ADDR')
    if not ip: ip = "unspecified"
    getQuery("INSERT INTO arrivals (location,datetime) VALUES ('{}','{}')".format(ip,getDateTime()),hasResult = False)
def getDateTime():
    datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    return datetime.datetime.now();