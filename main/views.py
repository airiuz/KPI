from django.shortcuts import render, redirect
from .models import KpiModel, SportModel, EvrikaModel, BookModel, WorkModel, BookItem, DeadlineModel, MeetingModel, \
    MeetingDateModel, SportDateModel
# MeetingDateModel, SportDateModel
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils import IsAdminOrReadOnly
from django.shortcuts import render
from . import utils
from django.db.models import Count, Max


# Create your views here.

def index(request):
    kpi_models = KpiModel.objects.all().order_by('name')
    result = []
    for x in kpi_models:
        books = sum(0 if x.score == "-" else int(x.score) for x in BookModel.objects.filter(kpi=x))
        sports = sum(0 if x.score == "-" else int(x.score) for x in SportModel.objects.filter(kpi=x))
        evrikas = sum(x.score for x in EvrikaModel.objects.filter(kpi=x))
        works = sum(0 if x.score == "-" else float(x.score) for x in WorkModel.objects.filter(kpi=x))
        meetings = sum(0 if x.score == "-" else float(x.score) for x in MeetingModel.objects.filter(kpi=x))
        result.append(
            {"kpi": x, "sports": sports, "evrikas": evrikas, "works": works, "books": books, 'meetings': meetings})

    return render(request, 'index.html', context={"results": result})


@IsAdminOrReadOnly
def all_meetings(request):
    if 'create_date' in request.POST:
        meet_date = MeetingDateModel.objects.create(date=request.POST.get('meeting_date'))
        meet_date.save()
        for i in KpiModel.objects.all():
            MeetingModel.objects.update_or_create(meeting_date=meet_date, kpi=i, defaults={'score': "-"})
        return redirect('/all_meetings/')
    elif 'save_meeting' in request.POST:
        n_score, meeting_id = request.POST.get('n_score'), request.POST.get('meeting_id')
        meeting_date_id, kpi_id = request.POST.get('meeting_date_id'), request.POST.get('kpi_id')
        kpi_user, meeting_date_obj = KpiModel.objects.get(id=kpi_id), MeetingDateModel.objects.get(id=meeting_date_id)
        if meeting_id == 'None':
            MeetingModel.objects.create(meeting_date=meeting_date_obj, score=n_score, kpi=kpi_user).save()
            return redirect('/all_meetings/')

        obj = MeetingModel.objects.get(id=meeting_id)
        obj.score = n_score
        obj.meeting_date = meeting_date_obj
        # obj.kpi = kpi_user
        obj.save()
        return redirect('/all_meetings/')

    data = []
    kpi_objects = [x for x in KpiModel.objects.all()]
    deadlines = list(x for x in MeetingDateModel.objects.all().order_by('deadline'))
    # deadline_pairs = {x.date: x.id for x in MeetingDateModel.objects.all().order_by('deadline')}

    for z, kpi_obj in enumerate(deadlines):
        kpi_data = {kpi_obj.date.strftime('%Y-%m-%d'): []}
        meeting_dic = {}
        # Iterate through each WorkModel object and add to the kpi_data dictionary

        for meeting_item in kpi_obj.meeting_date_items.all():
            meeting_dic[kpi_obj.date.strftime('%Y-%m-%d')] = {'score': meeting_item.score,
                                                              'meeting_id': meeting_item.id,
                                                              'meeting_date_id': meeting_item.meeting_date.id,
                                                              'kpi_user': meeting_item.kpi}
        for i in kpi_objects:
            kpi_data[kpi_obj.date.strftime('%Y-%m-%d')].append({
                'score': i.meeting_items.all()[z].score,
                'meeting_id': i.meeting_items.all()[z].id,
                'meeting_date_id': meeting_dic[kpi_obj.date.strftime('%Y-%m-%d')]['meeting_date_id'],
                'kpi_user': i.meeting_items.all()[z].kpi
            })
        data.append(kpi_data)
    return render(request, 'all_meetings.html', context={'data': data, 'kpi_objects': kpi_objects})


@IsAdminOrReadOnly
def meeting(request, id=None):
    kpi = get_object_or_404(KpiModel, id=id)
    meetings = MeetingModel.objects.filter(kpi=kpi).order_by("meeting_date")
    return render(request, 'meeting.html', {"meetings": meetings, 'kpi': kpi})


def meeting_increase_decrease_score(request, meeting_id=None):
    if request.method != 'POST':
        return HttpResponseNotAllowed(('POST',))
    score_dic = {'increase_meeting_score': 0, 'decrease_meeting_score': -5, 'reset_meeting_score': "-"}
    post_data = list(request.POST.items())
    last_key = post_data[-1][0]
    utils.change_meeting_score(meeting_id, request.POST.get('meeting_date_id'), request.POST.get('kpi_id'),
                               score=score_dic[last_key])
    return redirect(to='all_meetings')


def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if User.objects.filter(email=email).exists():
            error_message = 'Email is already taken.'
            return render(request, 'signup.html', {'error_message': error_message})

        # Check if passwords match
        if pass1 != pass2:
            error_message = "Passwords don't match."
            return render(request, 'signup.html', {'error_message': error_message})

        # Create a new user account
        User.objects.create_user(username=uname, email=email, password=pass1)

        return redirect('login')  # Redirect to the login page after successful sign-up

    return render(request, 'signup.html')


def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        user = authenticate(request, username=username, password=pass1)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Username or Password is incorrect")

    return render(request, 'login.html')


def LogoutPage(request):
    logout(request)
    return redirect("/")


def Navbar(request):
    return render(request, 'navbar.html')


@IsAdminOrReadOnly
def book(request, id):
    kpi = get_object_or_404(KpiModel, id=id)
    books = BookModel.objects.filter(kpi=kpi)
    return render(request, 'book.html', {"books": books, 'kpi': kpi})


@IsAdminOrReadOnly
def bookItems(request):
    bookitems = BookItem.objects.all()
    if request.method == 'POST':
        title = request.POST.get("title")
        bookitem = BookItem.objects.create(title=title)
        bookitem.save()
        return redirect('/')
    return render(request, 'book_items.html', {"bookitems": bookitems})


@IsAdminOrReadOnly
def work(request, id=None):
    kpi = get_object_or_404(KpiModel, id=id)
    works = WorkModel.objects.filter(kpi=kpi).order_by("deadline")
    return render(request, 'work.html', {"works": works, 'kpi': kpi})


@IsAdminOrReadOnly
def work_increase_reset_decrease_score(request, work_id=None):
    if request.method != 'POST':
        return HttpResponseNotAllowed(('POST',))
    score_dic = {'increase_work_score': 0.5, 'decrease_work_score': -1, 'reset_work_score': "-"}
    post_data = list(request.POST.items())
    last_key = post_data[-1][0]
    utils.change_score(work_id, request.POST.get('deadline_id'), request.POST.get('kpi_id'), score=score_dic[last_key])
    return redirect(to='all_works')


def reminder(request):
    return render(request, 'reminder.html')


@IsAdminOrReadOnly
def sport(request, id=None):
    kpi = get_object_or_404(KpiModel, id=id)
    sports = SportModel.objects.filter(kpi=kpi)
    return render(request, 'sport.html', {"sports": sports, 'kpi': kpi})


def edit_sport(request, kpi_id, sport_id):
    kpi = get_object_or_404(KpiModel, id=kpi_id)
    sport = get_object_or_404(SportModel, id=sport_id)

    if request.method == 'POST':
        details = request.POST.get('details')
        score = request.POST.get('score')

        sport.details = details
        sport.score = score
        sport.save()

        return redirect(f'/sport/{kpi_id}/')

    return render(request, 'edit_sport.html', {'kpi': kpi, 'sport': sport})


def delete_sport(request, kpi_id, sport_id):
    if request.method == 'POST':
        sport = get_object_or_404(SportModel, id=sport_id)
        sport.delete()
        return redirect(f'/sport/{kpi_id}/')


def create_sport(request, kpi_id):
    kpi = get_object_or_404(KpiModel, id=kpi_id)

    if request.method == 'POST':
        details = request.POST.get('n_details')
        score = request.POST.get('n_score', '')

        new_sport = SportModel.objects.create(details=details, score=score, kpi=kpi)
        new_sport.save()

        return redirect(f'/sport/{kpi_id}/')

    return render(request, 'sport.html', {'kpi': kpi})


@IsAdminOrReadOnly
def evrika(request, id=None):
    kpi = get_object_or_404(KpiModel, id=id)
    evrikas = EvrikaModel.objects.filter(kpi=kpi)
    return render(request, 'evrika.html', {"evrikas": evrikas, 'kpi': kpi})


@IsAdminOrReadOnly
def all_works(request):
    if 'create_deadline' in request.POST:
        deadline = DeadlineModel.objects.create(date=request.POST.get('new_deadline'))
        deadline.save()
        for i in KpiModel.objects.all():
            WorkModel.objects.update_or_create(deadline=deadline, kpi=i, defaults={'score': "-"})
        return redirect('/all_works/')
    elif 'save_work' in request.POST:
        n_score, work_id = request.POST.get('n_score'), request.POST.get('work_item_id')
        deadline_id, kpi_id = request.POST.get('deadline_id'), request.POST.get('kpi_id')
        kpi_user, dead_obj = KpiModel.objects.get(id=kpi_id), DeadlineModel.objects.get(id=deadline_id)
        if work_id == 'None':
            WorkModel.objects.create(deadline=dead_obj, score=n_score, kpi=kpi_user).save()
            return redirect('/all_works/')
        obj = WorkModel.objects.get(id=work_id)
        obj.score = n_score
        obj.kpi = kpi_user
        obj.save()
        return redirect('/all_works/')
    data = []
    kpi_objects = KpiModel.objects.all()
    deadlines = list(x.date for x in DeadlineModel.objects.all().order_by('created_at'))
    deadline_pairs = {x.date: x.id for x in DeadlineModel.objects.all().order_by('created_at')}

    for kpi_obj in kpi_objects:
        kpi_data = {kpi_obj: []}
        work_dic = {}

        # Iterate through each WorkModel object and add to the kpi_data dictionary
        for work_item in kpi_obj.work_items.all():
            work_dic[work_item.deadline.date] = {'score': work_item.score, 'work_id': work_item.id,
                                                 "deadline_id": work_item.deadline.id}
        for i in range(len(deadlines)):
            if deadlines[i] in work_dic:
                kpi_data[kpi_obj].append({
                    'date': deadlines[i].strftime('%Y-%m-%d'),
                    'score': work_dic[deadlines[i]]['score'],
                    'work_id': work_dic[deadlines[i]]['work_id'],
                    'deadline_id': work_dic[deadlines[i]]['deadline_id']
                })
            else:
                kpi_data[kpi_obj].append({
                    'date': deadlines[i].strftime('%Y-%m-%d'),
                    'score': "-",
                    'work_id': 0,
                    'deadline_id': deadline_pairs[deadlines[i]]
                })

        data.append(kpi_data)
    return render(request, 'all_works.html', {"deadlines": deadlines, "data": data})


@IsAdminOrReadOnly
def book_increase_decrease_score(request, book_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(('POST',))
    score_dic = {'increase_book_score': 1, 'decrease_book_score': 0, 'reset_book_score': "-"}
    post_data = list(request.POST.items())
    last_key = post_data[-1][0]

    kpi_id, book_item_id = request.POST.get('kpi_id'), request.POST.get('book_item_id')
    kpi_user = KpiModel.objects.get(id=kpi_id)
    book_item_obj = BookItem.objects.get(id=book_item_id)
    BookModel.objects.update_or_create(book=book_item_obj, kpi=kpi_user, defaults={'score': score_dic[last_key]})
    return redirect(to='all_books')


@IsAdminOrReadOnly
def all_books(request):
    if 'create_book_item' in request.POST:
        book_item = BookItem.objects.create(title=request.POST.get('new_book_item'))
        book_item.save()
        for i in KpiModel.objects.all():
            BookModel.objects.update_or_create(book=book_item, kpi=i, defaults={'score': "-"})
        return redirect('/all_books/')
    elif 'save_book' in request.POST:
        book_score, book_id = request.POST.get('book_score'), request.POST.get('book_id')
        book_item_id, kpi_id = request.POST.get('book_item_id'), request.POST.get('kpi_id')
        kpi_user = KpiModel.objects.get(id=kpi_id)
        book_item_obj = BookItem.objects.get(id=book_item_id)
        if book_id == 'None':
            BookModel.objects.create(book=book_item_obj, score=book_score, kpi=kpi_user).save()
            return redirect('/all_books/')

        obj = BookModel.objects.get(id=book_id)
        obj.score = book_score
        obj.kpi = kpi_user
        obj.save()
        return redirect('/all_books/')

    data = []
    kpis = KpiModel.objects.all()
    book_items = list(x.title for x in BookItem.objects.all().order_by('created_at'))
    for kpi_obj in kpis:
        kpi_data = {kpi_obj: []}
        book_dic = {}

        # Iterate through each BookModel object and add to the kpi_data dictionary
        for book in kpi_obj.book_items.all():
            book_dic[book.book.title] = {'score': book.score, 'book_id': book.id, "book_item_id": book.book.id}

        for i in range(len(book_items)):
            if book_items[i] in book_dic:
                kpi_data[kpi_obj].append({
                    'book_id': book_dic[book_items[i]]['book_id'],
                    'score': book_dic[book_items[i]]['score'],
                    'book_item_id': book_dic[book_items[i]]['book_item_id'],
                })
            else:
                kpi_data[kpi_obj].append({
                    'book_id': -1,
                    'score': "-",
                    'book_item_id': -1,
                })
        data.append(kpi_data)

    return render(request, 'all_books.html', {"book_items": book_items, "data": data})


@IsAdminOrReadOnly
def evrika_increase_decrease_score(request, evrika_id=0):
    if request.method != 'POST':
        return HttpResponseNotAllowed(('POST',))
    score_dic = {'increase_evrika_score': 5, 'decrease_evrika_score': 0}
    post_data = list(request.POST.items())
    last_key = post_data[-1][0]
    kpi_id, details = request.POST.get('kpi_id'), request.POST.get('details')
    kpi_user = KpiModel.objects.get(id=kpi_id)
    if evrika_id == 0 or evrika_id == '':
        EvrikaModel.objects.create(details=details, score=score_dic[last_key], kpi=kpi_user).save()
        return redirect('/all_evrika/')
    evrika = get_object_or_404(EvrikaModel, id=evrika_id)
    evrika.score = score_dic[last_key]
    evrika.save()
    return redirect(to='all_evrika')


@IsAdminOrReadOnly
def all_evrikas(request):
    if 'save_evrika' in request.POST:
        score = request.POST.get('score')
        details = request.POST.get('details')
        obj = EvrikaModel.objects.get(id=request.POST.get('evrika_id'))
        obj.score = score
        obj.details = details
        obj.save()
    elif 'create_evrika' in request.POST:
        kpi_obj = KpiModel.objects.get(id=request.POST.get('kpi_user_id'))
        EvrikaModel.objects.create(details=request.POST.get('details'), score=request.POST.get('score'),
                                   kpi=kpi_obj).save()
        return redirect('/all_evrika/')
    data = []
    evrikas = [x for x in EvrikaModel.objects.all().order_by("created_at")]
    kpi_users = KpiModel.objects.all()
    kpi_users_with_evrika_count = KpiModel.objects.annotate(evrika_count=Count('evrika_items')).order_by(
        '-evrika_count').first()

    evrika_dic = {}
    for x in kpi_users:
        evrika_dic[x] = []
        for y in evrikas:
            if y.kpi == x:
                evrika_dic[x].append({'score': y.score, 'details': y.details, 'evrika_id': y.id})
            # else:
            #     evrika_dic[x].append({'score':0, 'details':'','evrika_id':None})
    data.append(evrika_dic)
    return render(request, 'all_evrikas.html', {'data': data, 'kpi_users': kpi_users, 'evrikas': evrikas,
                                                'ball_detail_len': range(kpi_users_with_evrika_count.evrika_count)})


@IsAdminOrReadOnly
def sport_increase_decrease_score(request, sport_id=None):
    if request.method != 'POST':
        return HttpResponseNotAllowed(('POST',))
    score_dic = {'decrease_sport_score': -1, 'increase_sport_score': 0, 'reset_sport_score': "-"}
    post_data = list(request.POST.items())
    last_key = post_data[-1][0]
    utils.change_sport_score(sport_id, request.POST.get('sport_date_id'), request.POST.get('kpi_id'),
                             score=score_dic[last_key])
    return redirect(to='all_sports')


@IsAdminOrReadOnly
def all_sports(request):
    if 'create_sport_date' in request.POST:
        sport_date_item = SportDateModel.objects.create(date=request.POST.get('sport_date_obj'))
        sport_date_item.save()
        for i in KpiModel.objects.all():
            SportModel.objects.update_or_create(sport_date=sport_date_item, kpi=i, defaults={'score': "-"})
        return redirect('/all_sports/')
    elif 'save_sport' in request.POST:
        sport_score, sport_id = request.POST.get('sport_score'), request.POST.get('sport_id')
        sport_date_id, kpi_id = request.POST.get('sport_date_id'), request.POST.get('kpi_user_id')
        kpi_user = KpiModel.objects.get(id=kpi_id)
        sport_date_obj = SportDateModel.objects.get(id=sport_date_id)
        if sport_id == 'None':
            SportModel.objects.create(sport_date=sport_date_obj, score=sport_score, kpi=kpi_user).save()
            return redirect('/all_sports/')
        obj = SportModel.objects.get(id=sport_id)
        obj.score = sport_score
        # obj.kpi = kpi_user
        obj.save()
        return redirect('/all_sports/')

    #   get method
    data = []
    kpi_objects = [x for x in KpiModel.objects.all()]
    sport_dates = list(x for x in SportDateModel.objects.all().order_by('created_at'))

    for z, sport_date_obj in enumerate(sport_dates):
        sport_data = {sport_date_obj.date.strftime('%Y-%m-%d'): []}
        sport_dic = {}

        # Iterate through each SportModel object and add to the sport_data dictionary
        for sport_item in sport_date_obj.sport_date_items.all():
            sport_dic[sport_date_obj.date.strftime('%Y-%m-%d')] = {'score': sport_item.score, 'sport_id': sport_item.id,
                                                                   "sport_date_id": sport_item.sport_date.id,
                                                                   'kpi_user': sport_item.kpi}
        print(sport_dic)
        print(kpi_objects)
        for i in kpi_objects:
            if i in sport_dic:
                sport_data[sport_date_obj.date.strftime('%Y-%m-%d')].append({
                    'score': i.sport_items.all()[z].score,
                    'sport_id': i.sport_items.all()[z].id,
                    'sport_date_id': sport_dic[sport_date_obj.date.strftime('%Y-%m-%d')]['sport_date_id'],
                    'kpi_user': i.sport_items.all()[z].kpi
                })
            else:
                sport_data[sport_date_obj.date.strftime('%Y-%m-%d')].append({
                    "sport_id": -1,
                    "score": "-",
                    "sport_date_id": -1,
                    'kpi_user': -1
                })
        data.append(sport_data)
    return render(request, 'all_sports.html', {'data': data, 'kpi_objects': kpi_objects})


# [{<KpiModel: sadriddin>: [{'date': '2023-08-17', 'score': '-1', 'work_id': 1, 'deadline_id': 1}, {'date': '1221-12-21', 'score': 0, 'work_id': None, 'deadline_id': 2}]}]
# [{<KpiModel: sadriddin>: [{'date': '2023-08-17', 'score': '-1', 'work_id': 1, 'deadline_id': 1}, {'date': '1221-12-21', 'score': 0, 'work_id': None, 'deadline_id': 2}]}, {<KpiModel: user-1>: [{'date': '2023-08-17', 'score': 0, 'work_id': None, 'deadline_id': 1}, {'date': '1221-12-21', 'score': 0, 'work_id': None, 'deadline_id': 2}]}]

@IsAdminOrReadOnly
def edit_kpi(request, kpi_id):
    kpi = get_object_or_404(KpiModel, id=kpi_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        book_comment = request.POST.get('book_comment', None)
        upwork = request.POST.get('upwork', None)

        kpi.name = name
        kpi.book_comment = book_comment
        kpi.upwork = upwork
        kpi.save()

        return redirect(f'/kpi/')

    return render(request, 'edit_kpi.html')


@IsAdminOrReadOnly
def delete_kpi(request, kpi_id):
    kpi = get_object_or_404(KpiModel, id=kpi_id)
    if request.method == 'POST':
        kpi.delete()
        return redirect(f'/kpi/')


@IsAdminOrReadOnly
def create_kpi(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        book_comment = request.POST.get('book_comment', '')
        upwork = request.POST.get('upwork', '')

        new_kpi = KpiModel.objects.create(name=name, book_comment=book_comment, upwork=upwork)
        new_kpi.save()

        return redirect(f'/kpi/')

    return render(request, 'kpi.html')


@IsAdminOrReadOnly
def kpi_view(request):
    kpi_models = KpiModel.objects.all()

    if request.method == 'POST':
        if 'edit_kpi' in request.POST:
            kpi_id = request.POST.get('kpi_id')
            return redirect('edit_kpi', kpi_id=kpi_id)
        elif 'delete_kpi' in request.POST:
            kpi_id = request.POST.get('kpi_id')
            return redirect('delete_kpi', kpi_id=kpi_id)
        elif 'create_kpi' in request.POST:
            return redirect('create_kpi')
    return render(request, 'kpi.html', {"kpi_models": kpi_models})


def get_data(request):
    data = []
    kpi_objects = KpiModel.objects.all()
    deadlines = list(x.date for x in DeadlineModel.objects.all().order_by('created_at'))

    for kpi_obj in kpi_objects:
        kpi_data = {kpi_obj.name: []}
        work_dic = {}
        for x in kpi_obj.work_items.all():
            work_dic[x.deadline.date] = x.score

        # Iterate through each WorkModel object and add to the kpi_data dictionary
        for i in range(len(deadlines)):
            if deadlines[i] in work_dic:
                kpi_data[kpi_obj.name].append({deadlines[i].strftime('%Y-%m-%d'): work_dic[deadlines[i]]})
            else:
                kpi_data[kpi_obj.name].append({deadlines[i].strftime('%Y-%m-%d'): 0})
        data.append(kpi_data)
    return JsonResponse(data, safe=False)
