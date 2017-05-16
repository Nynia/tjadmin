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

    print success_count, fail_count, illegal_numbers
    self.update_state(state='FINISHED',
                      meta={'success': success_count,
                            'fail': fail_count,
                            'illegal': illegal_numbers})

    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}
