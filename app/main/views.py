# -*-coding=utf-8-*-
from . import main
from app.models import USER, FOCUSPRODUCT, SPINFO, BLACKLIST, BlACKUSER
from flask import render_template, request, flash, make_response, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from .form import UploadForm, SingleAddForm, FilterForm
import os, hashlib, time, re, datetime, urllib
from app import db
from flask_login import login_required, current_user
from app.tasks.datatask import datahandle


@main.route('/config', methods=['GET'])
def root():
    users = USER.query.all()
    spinfos = SPINFO.query.all()
    userlist = []
    for u in users:
        userdict = {}
        userdict['id'] = u.uid
        userdict['name'] = u.username
        userdict['level'] = u.privilege

        namelist = {}
        for item in u.splist.split(','):
            if len(item) < 10:
                spinfo = SPINFO.query.get(item)
                if spinfo:
                    print spinfo
                    namelist[item] = spinfo.spname
            else:
                productinfo = FOCUSPRODUCT.query.get(item)
                if productinfo:
                    namelist[item] = productinfo.servicename
        userdict['namelist'] = namelist
        userlist.append(userdict)

    return render_template('index.html', users=userlist, spinfos=spinfos)


@main.route('/upload', methods=['POST'])
def upload():
    create_person = BlACKUSER.query.get(int(current_user.id)).username
    filenames = []
    print request.form
    print request.files
    type = '1' if request.form.get('type') == 'black' else '2'
    remark = request.form.get('remark')
    for file in request.files.getlist('blackfile'):
        filename = hashlib.md5(secure_filename(file.filename) + str(time.time())).hexdigest()[:15]
        file.save(os.path.join('./res/', filename))
        filenames.append(filename)
    task = datahandle.delay(filenames, type, remark, create_person)
    return jsonify({}), 202, {'Location': url_for('main.taskstatus',
                                                  task_id=task.id)}
@main.route('/status/<task_id>',methods=['GET'])
def taskstatus(task_id):
    print request.url
    print task_id
    task = datahandle.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@main.route('/admin', methods=['GET', 'POST'])
def admin():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    uploadform = UploadForm()
    singleaddform = SingleAddForm()
    filterform = FilterForm()
    blackitem = None

    blacklist = BLACKLIST.query.all()
    if request.method == 'POST':
        phone_pattern = re.compile('(86)?((173|177|180|181|189|133|153|170|149)\d{8}$)')
        tel_parttern = re.compile('^(0(25|510|516|519|512|513|518|517|515|514|511|523||527)\d{8}$)')
        create_person = BlACKUSER.query.get(int(current_user.id)).username
        if uploadform.validate_on_submit():
            filenames = []
            type = '1' if uploadform.type.data == 'black' else '2'
            remark = uploadform.remark.data
            for file in request.files.getlist('blackfile'):
                filename = hashlib.md5(secure_filename(file.filename) + str(time.time())).hexdigest()[:15]
                file.save(os.path.join('./res/', filename))
                filenames.append(filename)
            datahandle.delay(filenames, type, remark, create_person)
            flash(u'正在处理...')
            return redirect(url_for('main.admin'))
            #     fp = open('./res/'+filename,'r')
            #     type = '1' if uploadform.type.data == 'black' else '2'
            #     remark = uploadform.remark.data
            #     for item in fp.readlines():
            #         number = filter(str.isdigit, item.strip())
            #         if number == '':
            #             continue
            #         match = phone_pattern.match(number)
            #         if match:
            #             number = match.group(2)
            #         else:
            #             match = tel_parttern.match(number)
            #             if match:
            #                 number = match.group(1)
            #             else:
            #                 illegal_numbers += number + ';'
            #                 fail_count += 1
            #                 continue
            #         #print number
            #         if not BLACKLIST.query.get(number):
            #             blackitem = BLACKLIST()
            #             blackitem.id = number
            #             blackitem.createtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            #             blackitem.state = '1'
            #             blackitem.type = type
            #             blackitem.remark = remark if remark else '无'
            #             blackitem.create_person = create_person
            #             blackitem.create_mode = '2'
            #             db.session.add(blackitem)
            #             success_count += 1
            #         else:
            #             repeat_count += 1
            #     fp.close()
            # uploadform.remark.data = ''
            # flash((u'成功导入%d个黑名单号码，重复号码%d个，非法号码%d个') % (success_count,repeat_count,fail_count))
            # flash((u'非法号码列表：%s') % illegal_numbers)
            # db.session.commit()
            # return redirect(url_for('main.admin'))
        elif singleaddform.validate_on_submit():
            success_count = 0
            fail_count = 0
            repeat_count = 0
            data = singleaddform.number.data
            for number in re.split('[,;\n]', data):
                number = filter(str.isdigit, str(number.strip()))
                match = phone_pattern.match(number)
                if match:
                    number = match.group(2)
                else:
                    match = tel_parttern.match(number)
                    if match:
                        number = match.group(1)
                    else:
                        # flash(u'%s 添加失败，号码不符合规范或者非电信号码' % number)
                        fail_count += 1
                        continue
                if not BLACKLIST.query.get(number):
                    blackitem = BLACKLIST()
                    blackitem.id = number
                    blackitem.createtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                    blackitem.state = '1'
                    blackitem.type = '1' if singleaddform.type.data == 'black' else '2'
                    blackitem.remark = singleaddform.remark.data if singleaddform.remark.data else u'无'
                    blackitem.create_person = create_person
                    blackitem.create_mode = '1'
                    db.session.add(blackitem)
                    success_count += 1
                else:
                    repeat_count += 1
                    # flash(u'%s 已存在，请不要重复添加' % number)
            flash((u'成功添加%d个黑名单号码，重复号码%d个，非法号码%d个') % (success_count, repeat_count, fail_count))
            singleaddform.number.data = ''
            singleaddform.remark.data = ''
            db.session.commit()
            return redirect(url_for('main.admin'))
        elif filterform.validate_on_submit():
            filter_count = 0
            sourcefile = request.files['sourcefile']
            filename = hashlib.md5(secure_filename(sourcefile.filename) + str(time.time())).hexdigest()[:15]
            download_name = sourcefile.filename[:-4] + '_filtered' + '.txt'
            sourcefile.save(os.path.join('./res/', filename))
            fp = open('./res/' + filename, 'r')
            download_file = open('./res/' + download_name, 'w+')
            for item in fp.readlines():
                number = filter(str.isdigit, item.strip())
                match = phone_pattern.match(number)
                if match:
                    number = match.group(2)
                else:
                    match = tel_parttern.match(number)
                    if match:
                        number = match.group(1)
                if not BLACKLIST.query.get(number):
                    download_file.write(item)
                else:
                    filter_count += 1
            flash(u'过滤成功，共过滤黑名单号码%d个' % filter_count)
            fp.close()
            db.session.commit()
            download_file.close()
            return redirect(url_for('main.admin', filter=urllib.quote(download_name.encode('utf-8'))))
    elif request.args.get('blacksearch'):
        blackitem = BLACKLIST.query.get(request.args.get('blacksearch').strip())
        if not blackitem:
            flash(u'此号码不在黑名单库中')
    elif request.args.get('filter'):
        # print repr(str(request.args.get('filter')))
        filename = urllib.unquote(str(request.args.get('filter')))
        # print repr(filename)
        filter_path = '..' + os.sep + 'res' + os.sep + filename.decode('utf-8')
        response = make_response(send_file(filter_path))
        response.headers["Content-Disposition"] = "attachment; filename=%s;" % filename
        return response
    return render_template('admin.html', uploadform=uploadform, singleaddform=singleaddform, filterform=filterform,
                           blackitem=blackitem, totalcount=len(blacklist))


@main.route('/export', methods=['GET'])
def export():
    blacklist = BLACKLIST.query.all()
    export_file_name = 'blacklist_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.txt'
    # export_file = open('./res/'+export_file_name,'w+')
    content = ''
    for item in blacklist:
        content += item.id + '\r\n'
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=%s;" % export_file_name
    return response
