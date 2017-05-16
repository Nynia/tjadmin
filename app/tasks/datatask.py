# -*-coding=utf-8-*-
from app import celery, db
from app.models import BLACKLIST
import re, datetime


@celery.task(bind=True)
def datahandle(self, filenames, type, remark, create_person):
    phone_pattern = re.compile('(86)?((173|177|180|181|189|133|153|170|149)\d{8}$)')
    tel_parttern = re.compile('^(0(25|510|516|519|512|513|518|517|515|514|511|523||527)\d{8}$)')

    success_count = 0
    fail_count = 0
    repeat_count = 0
    illegal_numbers = ''

    for filename in filenames:
        fp = open('./res/' + filename, 'r')
        for item in fp.readlines():
            number = filter(str.isdigit, item.strip())
            if number == '':
                continue
            match = phone_pattern.match(number)
            if match:
                number = match.group(2)
            else:
                match = tel_parttern.match(number)
                if match:
                    number = match.group(1)
                else:
                    illegal_numbers += number + ';'
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
        fp.close()
    db.session.commit()

    print success_count, fail_count, repeat_count,illegal_numbers
    content = (u'成功导入%d个黑名单号码，重复号码%d个，非法号码%d个') % (success_count, repeat_count, fail_count)

    return {'content': content, 'numbers': illegal_numbers, 'status': 'Task completed!',
            'result': 0}
