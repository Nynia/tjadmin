# -*-coding=utf-8-*-
from . import main
from app.models import USER, FOCUSPRODUCT, SPINFO, BLACKLIST, BlACKUSER
from flask import render_template, request, flash, make_response, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from .form import UploadForm, SingleAddForm, FilterForm
import os, hashlib, time, re, datetime, urllib
from app import db
from flask_login import login_required, current_user
from app.tasks.datatask import datahandle,export_numbers,filter_numbers


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
    print request.url
    print request.remote_addr
    create_person = BlACKUSER.query.get(int(current_user.id)).username
    filenames = []
    print request.form
    print request.files
    type = '1' if request.form.get('type') == 'black' else '2'
    remark = request.form.get('remark')
    for file in request.files.getlist('blackfile'):
        suffix = file.filename[file.filename.rindex('.'):]
        print suffix
        if suffix not in ['.txt','.csv','.xls','.xlsx']:
            continue
        filename = hashlib.md5(secure_filename(file.filename) + str(time.time())).hexdigest()[:15]+suffix
        file.save(os.path.join('./res/', filename))
        filenames.append(filename)
    task = datahandle.delay(filenames, type, remark, create_person)
    return jsonify({}), 202, {'Location': url_for('main.taskstatus',
                                                  task_id=task.id)}
@main.route('/filter', methods=['POST'])
def filter():
    sourcefile = request.files['sourcefile']
    source_filename = hashlib.md5(secure_filename(sourcefile.filename) + str(time.time())).hexdigest()[:15]
    download_filename = sourcefile.filename[:-4] + '_filtered' + '.txt'
    print source_filename,download_filename
    sourcefile.save(os.path.join('./res/', source_filename))
    task = filter_numbers.delay(source_filename, download_filename)
    return jsonify({}), 202, {'Location': url_for('main.taskstatus',
                                                  task_id=task.id)}

@main.route('/status/<task_id>',methods=['GET'])
def taskstatus(task_id):
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
            'content': task.info.get('content', ''),
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
    singleaddform = SingleAddForm()
    filterform = FilterForm()
    blackitem = None
    totalcount = BLACKLIST.query.count()
    if request.method == 'POST':
        print request.url
        phone_pattern = re.compile('(86)?((173|177|180|181|189|133|153|170|149)\d{8}$)')
        tel_parttern = re.compile('^(0(25|510|516|519|512|513|518|517|515|514|511|523||527)\d{8}$)')
        create_person = BlACKUSER.query.get(int(current_user.id)).username
        if singleaddform.validate_on_submit():
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
            download_file.close()
            return redirect(url_for('main.admin', filter=urllib.quote(download_name.encode('utf-8'))))
    elif request.args.get('blacksearch'):
        blackitem = BLACKLIST.query.get(request.args.get('blacksearch').strip())
        if not blackitem:
            flash(u'此号码不在黑名单库中')
    elif request.args.get('filter'):
        # print repr(str(request.args.get('filter')))
        filename = urllib.unquote(str(request.args.get('filter')))
        filter_path = '..' + os.sep + 'res' + os.sep + filename.decode('utf-8')
        response = make_response(send_file(filter_path))
        response.headers["Content-Disposition"] = "attachment; filename=%s;" % filename
        return response
    return render_template('admin.html',singleaddform=singleaddform,blackitem=blackitem, totalcount=totalcount)

@main.route('/export', methods=['GET'])
def export():
    task = export_numbers.delay()
    return jsonify({}), 202, {'Location': url_for('main.taskstatus',
                                                  task_id=task.id)}

@main.route('/download', methods=['GET'])
def download():
    filename = request.args.get('filename')
    print filename,repr(filename)
    print type(filename)

    print repr(filename.encode('utf-8'))
    fp = open('./res/' + filename.decode('utf-8'), 'r')
    content = ''
    for line in fp.readlines():
        content += line.strip('\n') + '\r\n'
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=%s;" % filename
    return response
