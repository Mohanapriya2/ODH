from webseal_log_parser import *
import datetime

def test_create_final_string_success():
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "POST /auth-handler/iam/authenticateuser/ HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    #output=webseal_log_parser.create_final_string(message)
    output=create_final_string(message)
    insert_time = str(datetime.datetime.now())
    print("insert_time",insert_time)
    del output['insert_time']
    del output['ip_address']
    print("output",output,type(output))
    assert output == {'agent_name': 'Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0', 'log_name': 'P152_lgi.de_capp_request_log', 'bearer': '', 'time_spent': 1913, 'request_url': '/auth-handler/iam/authenticateuser/', 'day': '2018-06-12', 'redirect_url': 'https://www.unitymedia.de/auth-handler/redirect.jsp', 'response_code': '302', 'channel_name': '', 'date_and_time': '2018-06-12T17:08:23.000000+0200', 'country_name': 'DE', 'scope': '', 'grant_type': '', 'user_name': '', 'method': 'POST'}

def test_create_final_string_failure():
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "POST /auth-handler/iam/authenticateuser/ HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    output=create_final_string(message)
    insert_time = str(datetime.datetime.now())
    print("insert_time",insert_time)
    del output['insert_time']
    del output['ip_address']
    print("output",output,type(output))
    assert output != 'xxx'


def test_get_country_from_log_name_success():
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "POST /auth-handler/iam/authenticateuser/ HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    text=message.split()
    country=get_country_from_log_name(text[0],message)
    assert country == 'de'


def test_get_country_from_log_name_failure():
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "POST /auth-handler/iam/authenticateuser/ HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    text=message.split()
    country=get_country_from_log_name(text[0],message)
    assert country != 'xxx'


def test_get_scope_and_grant_from_url_success():
    #message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "POST /auth-handler/iam/authenticateuser/ HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "GET /mga/sps/oauth/oauth20/authorize?state=app_lang_de&scope=country=DE+3rdparty=MyUPCApp&client_id=u6pMONT7FOeA2Vbss0Bqq&redirect_uri=http://localhost:8383/myupc/&response_type=code HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    text=split_data_m(message)
    print(text[9])
    scope,grant_type=get_scope_and_grant_from_url(text[9])
    print("scope",scope)
    #assert scope == ''
    assert scope=='country=DE+3rdparty=MyUPCApp'
    assert grant_type==''


def test_get_scope_and_grant_from_url_failure():
    #message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "POST /auth-handler/iam/authenticateuser/ HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "GET /mga/sps/oauth/oauth20/authorize?state=app_lang_de&scope=country=DE+3rdparty=MyUPCApp&client_id=u6pMONT7FOeA2Vbss0Bqq&redirect_uri=http://localhost:8383/myupc/&response_type=code HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0"'
    text=split_data_m(message)
    print(text[9])
    scope,grant_type=get_scope_and_grant_from_url(text[9])
    print("scope",scope)
    #assert scope == ''
    assert scope!='xxx'
    assert grant_type!='xxx'

def test_get_channel_and_country_from_url_success():
    #message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "GET /mga/sps/oauth/oauth20/authorize?state=app_lang_de&scope=country=DE+3rdparty=MyUPCApp&client_id=u6pMONT7FOeA2Vbss0Bqq&redirect_uri=http://localhost:8383/myupc/&response_type=code HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0" 123'
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "GET /mycare/app/scaffolding.customerproducts.json?chl=MyUPCApp_DE&cty=DE&lang=de&ver=1528816108291 HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0" 123'
    text=split_data_m(message)
    length_text=len(text)
    #print("length",len(text))
    country_name,channel_name=get_channel_and_country_from_url(text[9])
    print("country_name channel_name",country_name,channel_name)
    assert country_name == 'DE'
    assert channel_name == 'MyUPCApp_DE'

def test_get_channel_and_country_from_url_failure():
    #message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "GET /mga/sps/oauth/oauth20/authorize?state=app_lang_de&scope=country=DE+3rdparty=MyUPCApp&client_id=u6pMONT7FOeA2Vbss0Bqq&redirect_uri=http://localhost:8383/myupc/&response_type=code HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0" 123'
    message='P152_lgi.de_capp_request_log 4439 - - 209.84.3.11 - claas.hoops@gmx.de 12/Jun/2018:17:08:23 +0200 "GET /mycare/app/scaffolding.customerproducts.json?chl=MyUPCApp_DE&cty=DE&lang=de&ver=1528816108291 HTTP/1.1" 302 1913 "https://www.unitymedia.de/auth-handler/redirect.jsp?c_age=86400&referer=%2fauth-handler%2fiam%2fauthenticateuser%2f" "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0" 123'
    text=split_data_m(message)
    length_text=len(text)
    #print("length",len(text))
    country_name,channel_name=get_channel_and_country_from_url(text[9])
    print("country_name channel_name",country_name,channel_name)
    assert country_name != 'xxx'
    assert channel_name != 'xxx'
