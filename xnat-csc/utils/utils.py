import os
import subprocess
import json
import errno
import requests
import pydicom


## assumes inside container

class xnat_utils:
    def __init__(self, usr, pwd, xnat_host):
        #usr = os.environ['XNAT_USER']
        #pwd = os.environ['XNAT_PASS']
        # self.xnat_host = os.environ['XNAT_HOST']

        self.xnat_host = xnat_host
        usr = usr
        pwd = pwd


        if self.xnat_host.endswith('/'):
            self.xnat_host = self.xnat_host[:-1]
        xnat_url = self.xnat_host.replace('https://', '').replace('http://', '')
        jsession = requests.post('{}/data/JSESSION'.format(self.xnat_host), auth=(usr, pwd))
        self.session = requests.Session()
        if 'localhost' in self.xnat_host:
            self.session.cookies.set("JSESSIONID", jsession.text, domain='localhost.local')
        else:
            self.session.cookies.set("JSESSIONID", jsession.text, domain="{}".format(xnat_url))



    def close(self):
        """Closes all adapters and as such the session"""
        for v in self.session.adapters.values():
            v.close()

    def is_dicom_file(self,f):
        try:
            dataset = pydicom.dcmread(f)
            return True, dataset
        except Exception as e:
            return False, ''

    #Trigger piplines, autorun etc:
    #curl -u  -X PUT 'http://10..../data/archive/projects/KCL/experiments/uploader_E00003?triggerPipelines=true'

    def download_file(self, url, download_file=""):
        url = "{}/{}".format(self.xnat_host,url)
        r = self.session.get(url, allow_redirects=True)
        #print(r.text)
        open(download_file, 'wb').write(r.content)
        return r.content

    def dicom_dump(self,  project,session_id,subject_id='',scan_id='', tags=''):
        #https://wiki.xnat.org/display/XAPI/DICOM+Dump+Service+API
        url = "{}/data/services/dicomdump?src=/archive/projects/{}/experiments/{}".format(self.xnat_host,project,session_id)
        if len(subject_id) > 0:
            url = "{}/data/services/dicomdump?src=/archive/projects/{}/subjects/{}/experiments/{}".format(self.xnat_host,project,subject_id,session_id)
        if len(scan_id) > 0:
            url = '{}/scans/{}'.format(url, scan_id)
        if len(tags) > 0:
           url = '{}&field={}'.format(url, tags)
        print(url)
        r = self.session.get(url)
        json_data = json.loads(r.text)
        dicom_header = json_data['ResultSet']['Result']
        #convert to pydicom ?
        return dicom_header

    def upload_roi(self, project,session_id, assessor_label, dicom_path):
        headers = {'Content-Type': 'application/octet-stream', "Accept": "text/plain"}
        url = "{}/xapi/roi/projects/{}/sessions/{}/collections/{}?type=RTSTRUCT&overwrite=true".format(self.xnat_host, project,session_id, assessor_label )
        print(url)
        print(dicom_path)
        r = self.session.put(url, headers=headers, data=open(dicom_path, 'rb'))

        print(r)
        return r



    def trigger_autorun(self,project,session_id):
        url = "{}/data/archive/projects/{}/experiments/{}?triggerPipelines=true".format(self.xnat_host, project, session_id)
        r = self.session.put(url)
        return r

    def delete(self,command):
        r = self.session.delete('{}{}'.format(self.xnat_host,command))
        return r



    def get_scan(self,experiment_id, scan_id, project="NO PROJECT", xsitype='ALL SCANS', format='json'):
        # any experiment type - assessor included. id can be label IF porject specified
        url = "{}/data/archive/projects/{}/experiments/{}/scans/{}?format={}".format(self.xnat_host, project, experiment_id, scan_id, format)
        if "NO PROJECT" in project:
            url ="{}/data/archive/experiments/{}/scans/{}?".format(self.xnat_host, experiment_id, scan_id)
        if 'ALL SCANS' not in xsitype:
            url = '{}xsiType={}&'.format(url, xsitype)
        url = '{}format={}'.format(url, format)
        print(url)
        r = self.session.get(url)
        json_data = r.text
        if 'json' in format:
            json_data = json.loads(r.text)
        return json_data



    def get_assessor(self,assessor_id, experiment_id, project="NO PROJECT",  format='json'):
        # any experiment type - assessor included. id can be label IF porject specified
        url = "{}/data/archive/projects/{}/experiments/{}?format={}".format(self.xnat_host, project, assessor_id, format)
        if "NO PROJECT" in project:
            url ="{}/data/archive/experiments/{}/assessors/{}?format={}".format(self.xnat_host, experiment_id, assessor_id, format)
        print(url)
        r = self.session.get(url)
        json_data = r.text
        if 'json' in format:
            json_data = json.loads(r.text)
        return json_data



    def get_assessors(self,experiment_id, project="NO PROJECT", subject="NONE", format='json'):
        url = "{}/data/archive/projects/{}/experiments/{}/assessors?format={}".format(self.xnat_host, project, experiment_id, format)
        #must be exp id not label
        if "NO PROJECT" in project:
            url ="{}/data/archive/experiments/{}/assessors?format={}".format(self.xnat_host, experiment_id, format)
        print(url)
        r = self.session.get(url)
        json_data = r.text
        if 'json' in format:
            json_data = json.loads(r.text)
        return json_data

    def get_experiment(self,experiment_id, project="NO PROJECT", format='json'):
        # any experiment type - assessor included. id can be label IF porject specified
        url = "{}/data/archive/projects/{}/experiments/{}?format={}".format(self.xnat_host, project, experiment_id, format)
        if "NO PROJECT" in project:
            url ="{}/data/archive/experiments/{}?format={}".format(self.xnat_host, experiment_id, format)
        print(url)
        r = self.session.get(url)
        json_data = r.text
        if 'json' in format:
            json_data = json.loads(r.text)
        return json_data


    def get_experiments(self,project="NO PROJECT", modality="ALL", xsitype='ALL EXPERIMENTS', format='json'):
        # any experiment type - assessor included. id can be label IF porject specified
        url = "{}/data/archive/projects/{}/experiments?".format(self.xnat_host, project)
        if "NO PROJECT" in project:
            url = "{}/data/archive/experiments?".format(self.xnat_host, format)
        if 'ALL EXP' not in xsitype:
            url = '{}xsiType={}&'.format(url, xsitype)
        if 'ALL' not in modality:
            url = '{}modality={}&'.format(url, modality.upper())
        url = '{}format={}'.format(url, format)
        print(url)
        r = self.session.get(url)
        #print(r.text)
        json_data = r.text
        if 'json' in format:
            json_data = json.loads(r.text)
        return json_data


    def get_projects(self,format='json'):
        url = "{}/data/projects?format=xml".format(self.xnat_host)
        if 'json' in format:
            url = "{}/data/projects?format=json".format(self.xnat_host)
        r = self.session.get(url)
        json_data = r.text
        if 'json' in format:
            json_data = json.loads(r.text)
        return json_data



    def get_project_json(self,project):
        url = "{}/data/projects/{}?format=json".format(self.xnat_host,project)
        r = self.session.get(url)
        json_data = json.loads(r.text)
        return json_data



    def upload_xml(self,url, file_path):
        files = {'upload_file': open(file_path,'rb')}
        url = "{}{}".format(self.xnat_host,url)
        r = self.session.put(url, files=files)
        return r

    def upload_file_as_resource(self,url, resource_name, file_path):
        #first create resource
        url2 = "{}{}/resources/{}".format(self.xnat_host,url, resource_name)
        r = self.session.put(url2)
        files = {'upload_file': open(file_path,'rb')}
        url2 = "{}{}".format(self.xnat_host,url)
        r = self.session.put(url2, files=files)

    def create_subject(self,project, subject_label):
        #first create resource
        url = "{}/data/archive/projects/{}/subjects/{}".format(self.xnat_host,project, subject_label)
        r = self.session.put(url)


    def get_jsession(self):
        #errr.... already have if using requests.... delete?
        url = "{}/data/JSESSION/".format(self.xnat_host)
        r = self.session.post(url)
        js = r.text.split()
        jsession = js[0]
        print ('Created jsesison', jsession)
        return jsession

    def timeout( p ):
        if p.poll() is None:
            try:
                p.kill()
                print ('Error: process taking too long to complete--terminating')
            except OSError as e:
                if e.errno != errno.ESRCH:
                    raise




    def put(self,command, upload_file='none'):
        url = '{}{}'.format(self.xnat_host, command)
        if 'none' != upload_file:
            files = {'upload_file': open(upload_file, 'rb')}
            r = self.session.put(url, files=files)
        else:
            r = self.session.put(url)
        return r


    def post(self,command):
        url = '{}{}'.format(self.xnat_host, command)
        r = self.session.post(url)
        return r


    def make_dirs(filepath):

        folder_names = filepath.split('/')
        outfolder = '/'
        for folder in folder_names:
            outfolder = os.path.join(outfolder, folder)
            if not os.path.exists(outfolder ) and len(outfolder)>1:
                os.mkdir(outfolder)
        return outfolder


    def get(self,command, data='none', head='none', format='json'):
        url = '{}{}'.format(self.xnat_host, command)
        print(url)
        if 'none' != data and 'none' == head:
            r = self.session.get(url, data=data)
        elif 'none' != data and 'none' != head:
            r = self.session.get(url, headers=head, data=data)
        else:
            r = self.session.get(url)
        print(r.text)
        if 'json' in format:
            data = json.loads(r.text)
            return data
        return r.text




    def dcm_dicomToSQLTime(dicom_time):
        #143642.000000 to 14:36:42
        sql_time = dicom_time[:2] + ':' + dicom_time[2:4] + ':' + dicom_time[4:6]
        #print dicom_time + "  converted to:" +sql_time
        return sql_time

    def dcm_dicomToSQLDate(dicom_date):
        #20050130 to 2005-01-30
        sql_date = dicom_date[:4] + '-' + dicom_date[4:6] + '-' + dicom_date[6:8]
        #print dicom_date + "  converted to:" +sql_date
        return sql_date

    def dcm_tidy_string(dicom_string):
        return str(dicom_string).replace("^", "_").replace(" ","_").replace("'", "").replace("[","").replace("]","")





    def share_session(self,project, session_label,project_to_share_to):
        url = "{}/data/archive/projects/{}/experiments/{}/projects/{}".format(self.xnat_host,project, session_label,project_to_share_to)
        r = self.session.put(url)
        return r.status_code






    def nii_zip(folder, nifti_file):

        n_in = os.path.join(folder, nifti_file)
        nifti_file = nifti_file.replace('(','').replace(')','')
        os.rename(n_in, os.path.join(folder, nifti_file.replace('(','').replace(')','') ))
        print ('RENAMED FILE {} {}'.format(n_in, nifti_file))
        zip_command= 'gzip -fq {}/{}'.format( folder, nifti_file)
        print( '     Command: {}'.format(zip_command))
        suc = subprocess.check_call(zip_command, shell=True)


    def is_scan_of_interest(modality, exclude_list):
        if modality in exclude_list:
            return False
        else:
            return True


    def extract_values(self, obj, key):
        """Pull all values of specified key from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        results = extract(obj, arr, key)
        return results
