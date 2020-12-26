import yaml
from datetime import datetime, date, timedelta
import modules.c19norge as c19norge

with open('./config/config.yml', 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


def update_data(category='ALL'):
    categories = ['tested',
                  'confirmed',
                  'dead',
                  'admissions',
                  'respiratory']

    if category == 'ALL':
        for c in categories:
            currentData = c19norge.metadata(c, 'total')
            file_write(c, currentData)
    else:
        currentData = c19norge.metadata(category, 'total')
        file_write(category, currentData)


def file_open(category):
    return open('./data/{}.txt'.format(category), 'r').read()


def file_write(category, data):
    fh = open('./data/{}.txt'.format(category), 'w')
    fh.write(str(data))
    fh.close()


def get_messagetext(name, diff):
    if diff is None:
        return None
    if diff == 1:
        messagetext = cfg['twitter']['jobs'][name]['text_pos_singular']
    elif diff > 1:
        messagetext = cfg['twitter']['jobs'][name]['text_pos_plural']
    elif diff == -1:
        messagetext = cfg['twitter']['jobs'][name]['text_neg_singular']
    elif diff < -1:
        messagetext = cfg['twitter']['jobs'][name]['text_neg_plural']
    else:
        return None

    return messagetext


def get_datetimestr():
    datestr = datetime.now().strftime('%d.%m.%y')
    timestr = datetime.now().strftime('%H:%M')

    ret_str = datestr + ' kl ' + timestr

    return ret_str


def get_date_yesterday():
    datestr = (date.today() - timedelta(days=1)).strftime('%d.%m.%Y')

    return datestr
