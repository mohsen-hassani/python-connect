import requests
import xml.etree.ElementTree as ET
from gvars import DOMAIN, FOLDER_ID, AC_LOGIN, AC_PASSWORD


# The cookie which hold your login state after a success loign 
BREEZE = ''


def request(action, parameters):
    base_url = DOMAIN + '/api/xml'
    params = ''
    for key in parameters:
        params = params + '&' + key + '=' + str(parameters[key])
    url = '{base_url}?action={action}{params}'.format(
        base_url=base_url, action=action, params=params)
    response = requests.get(url)
    return response

def login(username, password):
    action = 'login'
    params = {
        'login': username,
        'password': password,
    }
    breeze_session = None
    response = request(action, params)
    headers = response.headers
    cookie = headers['Set-Cookie']
    breeze_session = cookie.split('=')[1].split(';')[0]
    global BREEZE
    BREEZE = breeze_session
    return breeze_session

def create_empty_meeting(name, url):
    action = 'sco-update'
    params = {
        'type': 'meeting',
        'name': name,
        'folder-id': FOLDER_ID,
        'url-path': url,
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'sco':
                    return et[1].attrib['sco-id']
        return None
    except:
        return None

def update_meeting(sco_id, name):
    action = 'sco-update'
    params = {
        'type': 'meeting',
        'name': name,
        'sco-id': sco_id,
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                return True
        return False
    except:
        return False

def add_user_to_meeting(meeting_id, user_id, role='view'):
    action = 'permissions-update'
    params = {
        'acl-id': meeting_id,
        'principal-id': user_id,
        'permission-id': role,
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                return True
        return None
    except:
        return None

def change_sco_access_type(acl_id, permission='view-hidden'):
    if permission not in ['denied', 'remove', 'view-hidden']:
        return 'Invalid permission'
    action = 'permissions-update'
    params = {
        'acl-id': acl_id,
        'principal-id': 'public-access',
        'permission-id': permission,
        'session': BREEZE,
    }
    response = request(action, params)
    principals = None
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            return et[0].attrib['code']
        return None
    except:
        return None

def create_user(fname, lname, sut_id, nid):
    action = 'principal-update'
    params = {
        'first-name': fname,
        'last-name': lname,
        'login': sut_id,
        'password': nid,
        'type': 'user',
        'has-children': 'false',
        'send-email': 'false',
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'principal':
                    return et[1].attrib['principal-id']
        return None
    except:
        return None

def get_user_by_login(login):
    action = 'principal-list'
    params = {
        'filter-login': login,
        'session': BREEZE
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'principal-list':
                    if len(et[1]) >= 1:
                        return et[1][0].attrib['principal-id']
        return None
    except:
        return None

def users_list():
    action = 'principal-list'
    params = {
        'filter-type': 'user',
        'session': BREEZE,
    }
    principals = {}
    response = request(action, params)
    if response.status_code != 200:
        return {}
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'principal-list':
                    if len(et[1]) >= 0:
                        for principal in et[1]:
                            principals[principal[1].text] = principal.attrib['principal-id']
                        return principals
        return {}
    except:
        return {}

def groups_list():
    action = 'principal-list'
    params = {
        'filter-type': 'group',
        'session': BREEZE,
    }
    principals = {}
    response = request(action, params)
    if response.status_code != 200:
        return {}
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'principal-list':
                    if len(et[1]) >= 0:
                        for principal in et[1]:
                            principals[principal[1].text] = principal.attrib['principal-id']
                        return principals
        return {}
    except:
        return {}

def delete_principal(principal):
    action = 'principals-delete'
    params = {
        'principal-id': principal,
        'session': BREEZE,
    }
    response = request(action, params)
    if response.status_code != 200:
        return None
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                return True
        return False
    except:
        return False

def get_group_by_name(name):
    action = 'principal-list'
    params = {
        'filter-name': name,
        'session': BREEZE
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'principal-list':
                    if len(et[1]) >= 1:
                        return et[1][0].attrib['principal-id']
        return None
    except:
        return None

def create_group(name):
    action = 'principal-update'
    params = {
        'name': name,
        'type': 'group',
        'has-children': 'true',
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'principal':
                    return et[1].attrib['principal-id']
        return None
    except:
        return None

    return response

def add_user_to_group(group_id, user_id):
    action = 'group-membership-update'
    params = {
        'group-id': group_id,
        'principal-id': user_id,
        'is-member': 'true',
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                return True
        return None
    except:
        return None

def change_permission(acl_id, principle_id, permission):
    action = 'permissions-update'
    params = {
        'acl-id': acl_id,
        'principal-id': principle_id,
        'permission-id': permission,
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        if response.status_code == 200:
            et = ET.fromstring(response.text)
            if et[0].tag == 'status':
                if et[0].attrib['code'] == 'ok':
                    return True
        return False
    except:
        return False

def get_meetings_in_folder(folder_id):
    action = 'sco-contents'
    params = {
        'sco-id': folder_id,
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        if response.status_code == 200:
            et = ET.fromstring(response.text)
            if et[0].tag == 'status':
                if et[1].tag == 'scos':
                    if len(et[1]) > 0:
                        scos = {}
                        for item in et[1]:
                            url_tag = item[1]
                            scos[url_tag.text[1:-1]] = item.attrib['sco-id']
                        return scos
            return {}
    except:
        return {}

def concurrent_users(length):
    action = 'report-meeting-concurrent-users'
    params = {
        'length': length,
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        if response.status_code == 200:
            et = ET.fromstring(response.text)
            if et[0].tag == 'status':
                if et[1].tag == 'report-meeting-concurrent-users':
                    return et[1].attrib['max-users']
            return None
    except:
        return None

def get_meetings_name_in_folder(folder_id):
    action = 'sco-contents'
    params = {
        'sco-id': folder_id,
        'session': BREEZE,
    }
    response = request(action, params)
    response.encoding = 'utf-8'
    try:
        if response.status_code == 200:
            et = ET.fromstring(response.text)
            if et[0].tag == 'status':
                if et[1].tag == 'scos':
                    scos = {}
                    if len(et[1]) > 0:
                        for item in et[1]:
                            scos[item[1].text] = item[0].text
                        return scos
            return {}
    except:
        return {}

def principal_info(principal_id, session=BREEZE):
    action = 'principal-info'
    params = {
        'principal-id': principal_id,
        'session': session,
    }
    response = request(action, params)
    try:
        if response.status_code == 200:
            response.encoding = 'utf-8'
            et = ET.fromstring(response.text)
            if et[0].tag == 'status':
                if et[1].tag == 'contact':
                    return {
                        'fname': et[1][0].text, 
                        'lname': et[1][1].text,
                    }
            return None
    except:
        return None

def principal_update(pid, fname, lname):
    action = 'principal-update'
    params = {
        'principal-id': pid,
        'fist-name': fname,
        'last-name': lname,
        'type': 'user',
        'session': BREEZE,
    }
    response = request(action, params)
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                return True
        return False
    except:
        return False

    return response

def principal_in_sco(acl_id, permission_id):
    action = 'permissions-info'
    params = {
        'acl-id': acl_id,
        'filter-permission-id': permission_id,
        'session': BREEZE,
    }
    response = request(action, params)
    principals = []
    try:
        et = ET.fromstring(response.text)
        if et[0].tag == 'status':
            if et[0].attrib['code'] == 'ok':
                if et[1].tag == 'permissions':
                    for e in et[1]:
                        principals.append(e.attrib['principal-id'])
                    return principals
        return  principals
    except:
        return []

# A sample use:
# login(AC_LOGIN, AC_PASSWORD)
# meetings = get_meetings_in_folder(FOLDER_ID)
# print(meetings)