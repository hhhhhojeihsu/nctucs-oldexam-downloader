#!/usr/bin/env python3
import requests, os, sys, json, csv, shutil
from bs4 import BeautifulSoup

# It is suggest that you put your account/password as env variable
# But you can hard coded them into the file if you want
cred = {
    'dep': 'cs',
    #'id': os.getenv('USER'),
    'id': 'YOUR CS ID',
    #'pw': os.getenv('D_PASS')
    'pw': 'YOUR CS PW'
}

def main():

    # Create folder
    if not os.path.exists('oldexam_dump'):
        os.makedirs('oldexam_dump')
        os.chdir('oldexam_dump')
    else:
        print('Older version exists. Please delete \'oldexam_dump\' before trying again')
        sys.exit(1)

    with requests.session() as s:
        # Create connection
        try:
            s.post('https://oldexam.nctucs.tw/login_chk', data=cred)
            resp = s.get('https://oldexam.nctucs.tw/main')
        except:
            print("Cannot connect to server.")
            sys.exit(1)

        # Start crawling
        soup = BeautifulSoup(resp.text, 'html5lib')

        # Get category lists
        try:
            ul = soup.find(id='left').find_next('ul')
        except AttributeError:
            print("Invalid credentials.")
            sys.exit(1)
        for li in ul.find_all('li'):
            print('- Downloading \'', li.get_text(), '\'')
            os.makedirs(li.get_text())
            os.chdir(li.get_text())

            # Get course lists
            raw_course = BeautifulSoup(s.post('https://oldexam.nctucs.tw/ajax_show_course', data={'cid': li['value']}).text, 'html5lib')
            for course in raw_course.find_all('li'):
                print('  - Downloading \'', course.get_text(), '\'')
                foldername = course.get_text().replace('\t', '')
                os.makedirs(foldername)
                os.chdir(foldername)
                file_list = json.loads(s.post('https://oldexam.nctucs.tw/ajax_show_exam', data={'cid': course['value']}).text)
                with open('list.csv', 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['ID', '西元年', '講師', '類型', '提供者', '上傳者', '附註', '上傳日期'])

                    for idx, file in enumerate(file_list):
                        writer.writerow([idx, file['semester'], file['type'], file['instructor'], file['provider'], file['uploader'], file['comment'], file['day']])
                        # Download the file
                        filename = '-'.join([str(idx).rjust(2, '0'), file['semester'], file['instructor'], file['type']])
                        print('    - Downloading \'', filename, '\'')
                        archive = s.get('https://oldexam.nctucs.tw/down/' + file['eid'], stream=True)
                        with open((filename + os.path.splitext(archive.headers['Content-Disposition'])[1]).replace('";', ''), 'wb') as f:
                            shutil.copyfileobj(archive.raw, f)
                            f.close()
                    csvfile.close()
                os.chdir('..')
            os.chdir('..')

if __name__ == '__main__':
    main()
