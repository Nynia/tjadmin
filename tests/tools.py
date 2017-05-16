#-*-coding:utf-8-*-
import re
from pyexcel_xls import get_data

phone_pattern = re.compile('^(86)?((173|177|180|181|189|133|153|170|149)\d{8})$')
tel_parttern = re.compile('^((025|0510|0516|0519|0512|0513|0518|0517|0515|0514|0511|0523||0527)?\d{8}$)')
areano_dict = {
    u'南京':'025',
    u'无锡':'0510',
    u'镇江':'0511',
    u'苏州':'0512',
    u'南通':'0513',
    u'扬州':'0514',
    u'盐城':'0515',
    u'徐州':'0516',
    u'淮安':'0517',
    u'连云':'0518',
    u'常州':'0519',
    u'泰州':'0523',
    u'宿迁':'0527'
}

phone_list = []
tel_list = []

def read_xls_file():
    xls_data = get_data("test.xlsx")
    for sheet_name in xls_data.keys():
        areaname = sheet_name[:2]
        areano = areano_dict.get(areaname,'')

        sheet_data = xls_data[sheet_name]
        for row in sheet_data:
            for cell in row:
                item = unicode(cell)
                if phone_pattern.match(item):
                    phone_list.append(item)
                elif tel_parttern.match(item):
                    if len(item) == 8:
                        item = areano + item
                    if len(item) > 8:
                        tel_list.append(item)


if __name__ == '__main__':
    read_xls_file()
    print len(phone_list),len(tel_list)
    print phone_list
    print tel_list


