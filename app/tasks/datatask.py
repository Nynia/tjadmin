# -*-coding=utf-8-*-
from app import celery, db
from app.models import BLACKLIST
import re, datetime
from pyexcel_xls import get_data


@celery.task(bind=True)
def datahandle(self, filenames, type, remark, create_person):
    success_count = 0
    fail_count = 0
    repeat_count = 0

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
        print filename
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
                                if len(number) == 8:
                                    number = areano + number
                            else:
                                fail_count += 1
                                continue
                        if not BLACKLIST.query.get(number):
                            blackitem = BLACKLIST()
                            blackitem.id = number
                            blackitem.createtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                            blackitem.state = '1'
                            blackitem.type = type
                            blackitem.remark = remark if remark else u'无'
                            blackitem.create_person = create_person
                            blackitem.create_mode = '2'
                            db.session.add(blackitem)
                            success_count += 1
                        else:
                            repeat_count += 1
    db.session.commit()

    print success_count, fail_count, repeat_count
    content = (u'成功导入%d个黑名单号码，重复号码%d个，非法号码%d个') % (success_count, repeat_count, fail_count)

    return {'content': content, 'status': 'Task completed!',
            'result': 0}
