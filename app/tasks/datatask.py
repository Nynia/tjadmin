# -*-coding=utf-8-*-
from app import celery,redisClient
import re, datetime
from pyexcel_xls import get_data

@celery.task(bind=True)
def datahandle(self, filenames, type, remark, create_person):
    success_count = 0
    fail_count = 0
    repeat_count = 0
    number_list = []
    phone_pattern = re.compile('^(86)?((173|177|180|181|189|133|153|170|149)\d{8})$')
    tel_parttern = re.compile('^((025|0510|0516|0519|0512|0513|0518|0517|0515|0514|0511|0523||0527)?\d{8}$)')
    number_parttern = re.compile('\d{8,13}')
    areano_dict = {
        u'南京': '025',
        u'无锡': '0510',
        u'镇江': '0511',
        u'苏州': '0512',
        u'南通': '0513',
        u'扬州': '0514',
        u'盐城': '0515',
        u'徐州': '0516',
        u'淮安': '0517',
        u'连云': '0518',
        u'常州': '0519',
        u'泰州': '0523',
        u'宿迁': '0527'
    }
    for filename in filenames:
        filename = './res/' + filename
        if filename[-3:] == 'txt':
            fp = open(filename, 'r')
            for number in fp.readlines():
                number = filter(str.isdigit, str(number.strip()))
                match = phone_pattern.match(number)
                if match:
                    number = match.group(2)
                else:
                    match = tel_parttern.match(number)
                    if match:
                        number = match.group(1)
                        if len(number) == 8 and len(areano) > 0:
                            number = areano + number
                    else:
                        fail_count += 1
                        continue
                number_list.append(number)
                #success_count += 1
            fp.close()
        else:
            xls_data = get_data(filename)
            for sheet_name in xls_data.keys():
                areaname = sheet_name[:2]
                areano = areano_dict.get(areaname, '')
                sheet_data = xls_data[sheet_name]
                for row in sheet_data:
                    for cell in row:
                        for number in number_parttern.findall(unicode(cell)):
                            match = phone_pattern.match(number)
                            if match:
                                number = match.group(2)
                            else:
                                match = tel_parttern.match(number)
                                if match:
                                    number = match.group(1)
                                    if len(number) == 8 and len(areano) > 0:
                                        number = areano + number
                                else:
                                    fail_count += 1
                                    continue
                            number_list.append(number)
                            #success_count += 1
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    for number in number_list:
        if not redisClient.hexists('index', number):
            redisClient.hset(number, 'id', number)
            redisClient.hset(number, 'createtime',timestamp)
            redisClient.hset(number, 'state', '1')
            redisClient.hset(number, 'type', type )
            redisClient.hset(number, 'remark', remark)
            redisClient.hset(number, 'create_person', create_person)
            redisClient.hset(number, 'create_mode', '2')

            redisClient.hset('index', number, True)
            success_count += 1
        else:
            repeat_count += 1

    count_after = redisClient.hlen('index')

    print success_count, fail_count, repeat_count
    content = (u'成功导入%d个黑名单号码，重复号码%d个，非法号码%d个') % (success_count, repeat_count, fail_count)

    return {'content': content, 'status': 'Task completed!','action':'upload',
            'result': count_after}


@celery.task(bind=True)
def export_numbers(self):
    numbers = []
    for number in redisClient.hkeys('index'):
        numbers.append(redisClient.hget(number,'id'))
    export_file_name = 'blacklist_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt'
    export_file = open('./res/' + export_file_name, 'w+')
    export_file.write('\n'.join(numbers))
    export_file.close()
    return {'content': export_file_name, 'status': 'Task completed!','action':'export',
            'result': 0}

@celery.task(bind=True)
def filter_numbers(self,source_filename, download_filename):
    filter_count = 0
    phone_pattern = re.compile('^(86)?((173|177|180|181|189|133|153|170|149)\d{8})$')
    tel_parttern = re.compile('^((025|0510|0516|0519|0512|0513|0518|0517|0515|0514|0511|0523||0527)?\d{8}$)')
    source_file = open('./res/' + source_filename, 'r')
    download_file = open('./res/' + download_filename, 'w+')
    for item in source_file.readlines():
        number = filter(str.isdigit, item.strip())
        match = phone_pattern.match(number)
        if match:
            number = match.group(2)
        else:
            match = tel_parttern.match(number)
            if match:
                number = match.group(1)
        if number and not redisClient.hexists('index',number):
            download_file.write(item)
        else:
            filter_count += 1
    source_file.close()
    download_file.close()
    return {'content': download_filename, 'status': 'Task completed!', 'action': 'filter',
            'result': filter_count}