from django.contrib.sessions.models import Session
from django.db.models import Q
from django.shortcuts import render
import json
import requests

from django.contrib.auth import authenticate, logout, login as dj_login
from django.shortcuts import render, redirect
from django.utils import timezone
import re

from truck_app.models import HouseShiftingDetails
from truck_app.models import VehicleShiftingDetails
from truck_app.models import WareHouseStorageDetails
from truck_app.models import UserProfile
from truck_app.models import Register
from truck_app.models import CustomUser as User
from django.contrib import messages
from django.db import connections
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from datetime import datetime
from django.utils import timezone
from datetime import datetime as dt
import pytz


def login(request):
    """Login the Registered Users in the app"""
    if request.method == "POST":
        if request.POST["phone_number"]:
            phone_number = request.POST["phone_number"]
        else:
            phone_number = "Empty"

        if request.POST["password"]:
            password = request.POST["password"]
        else:
            password = "Empty"

        user = authenticate(request, phone_number=phone_number, password=password)
        print("user>>>>>>>>>>>",user)
        if user is not None:
            dj_login(request, user)
            user_ids = request.user.id
            print("user_ids", user_ids)

            return redirect('Dashboard')
        else:
            messages.success(request, 'Incorrect Credential.')
            return render(request, 'truck_app_web/login.html')

    return render(request, 'truck_app_web/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    request_user_id = request.user.id
    if request_user_id == 9:
        dashboard_list = ["1000", "2200", "1700", "3000", "2500", "4000", "3500", "9000", "3400", "5000", '5500',
                          '8000']
        house_shifting_count = HouseShiftingDetails.objects.all().count()
        if house_shifting_count is None or "":
            house_shifting_count = "0"
        vehicle_shifting_count = VehicleShiftingDetails.objects.all().count()
        if vehicle_shifting_count is None or "":
            vehicle_shifting_count = "0"
        warehouse_shifting_count = WareHouseStorageDetails.objects.all().count()
        if warehouse_shifting_count is None or "":
            warehouse_shifting_count = "0"

        user_profile_count = UserProfile.objects.all().count()
        if user_profile_count is None or "":
            user_profile_count = "0"

        house_shifting_completed_count = HouseShiftingDetails.objects.filter(completed=True).count()
        warehouse_shifting_completed_count = WareHouseStorageDetails.objects.filter(completed=True).count()
        vehicle_shifting_completed_count = VehicleShiftingDetails.objects.filter(completed=True).count()
        completed_count = house_shifting_completed_count + warehouse_shifting_completed_count + vehicle_shifting_completed_count
        house_shifting_pending_count = HouseShiftingDetails.objects.filter(Q(completed=False) | Q(completed__isnull=True)).count()
        warehouse_shifting_pending_count = WareHouseStorageDetails.objects.filter(Q(completed=False) | Q(completed__isnull=True)).count()
        vehicle_shifting_pending_count = VehicleShiftingDetails.objects.filter(Q(completed=False) | Q(completed__isnull=True)).count()
        pending_count = house_shifting_pending_count + warehouse_shifting_pending_count + vehicle_shifting_pending_count
        return render(request,
                      'truck_app_web/dashboard.html',
                      {"dashboard_list": dashboard_list,
                       "house_shifting_count": house_shifting_count,
                       "vehicle_shifting_count": vehicle_shifting_count,
                       "warehouse_shifting_count": warehouse_shifting_count,
                       "user_profile_count": user_profile_count,
                       "completed_count": completed_count,
                       "pending_count": pending_count})
    else:
        return redirect("login")


@login_required
def customer_details(request):
    request_user_id = request.user.id
    if request_user_id == 9:
        # establish connection to MySQL database
        cursor = connections['default'].cursor()

        # execute a select query to retrieve all rows from the table
        cursor.execute("SELECT * FROM truck_app_userprofile")
        print("cursor", cursor)

        # fetch all rows of data and store as list of dictionaries
        rows = cursor.fetchall()
        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        dic_data = {"data": data}
        # return data
        # return data as JSON response
        return render(request, 'truck_app_web/customer_details.html', dic_data)
    else:
        return redirect("login")


@login_required
def house_shifting(request):
    request_user_id = request.user.id
    if request_user_id == 9:
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)
        if request.method == "POST":
            status = request.POST.get('status')
            search_query = request.POST.get('search')
            if status == "all":
                house_shifting = HouseShiftingDetails.objects.all().order_by('-created')
            elif status == "completed":
                house_shifting = HouseShiftingDetails.objects.filter(completed=True).order_by('-created')
            elif status == "pending":
                house_shifting = HouseShiftingDetails.objects.filter((Q(completed=False) | Q(completed__isnull=True))).order_by('-created')
            else:
                house_shifting = HouseShiftingDetails.objects.all().order_by('-created')

            if search_query:
                try:
                    house_shifting = house_shifting.filter(booking_id=search_query).order_by('-created')
                except:
                    house_shifting = HouseShiftingDetails.objects.all().order_by('-created')
            house_shifting_detail = HouseShiftingDetails.objects.all().order_by('-created')
            for house_shifting_data in house_shifting_detail:
                print(">>>>for")
                if house_shifting_data.completed is False or house_shifting_data.completed is None:
                    completed_datetime = house_shifting_data.completed_date
                    if completed_datetime is not None:
                        completed_date = completed_datetime.date()
                        completed_time = completed_datetime.time()
                        now_date = now.date()
                        now_time = now.time()
                        if completed_date < now_date:
                            print(">>>>>>>date less than>>>>>>>>>>>>>")
                            house_shifting_data.completed = True
                            house_shifting_data.save()
                        elif completed_date == now_date:
                            print(">>>>>>>date equal to >>>>>>>>>>>>>")
                            if completed_time <= now_time:
                                print("<>>>>>>>>>>time less than or equal to>>>>>>>>>>>>>>>>>")
                                house_shifting_data.completed = True
                                house_shifting_data.save()
                else:
                    completed_datetime = house_shifting_data.completed_date
                    if house_shifting_data.completed is True:
                        if completed_datetime is not None:
                            completed_date = completed_datetime.date()
                            completed_time = completed_datetime.time()
                            now_date = now.date()
                            now_time = now.time()
                            if completed_date > now_date:
                                print(">>>>>>>date greater than>>>>>>>>>>>>>")
                                house_shifting_data.completed = False
                                house_shifting_data.save()
                            elif completed_date == now_date:
                                print(">>>>>>>date equal than>>>>>>>>>>>>>")
                                if completed_time > now_time:
                                    print(">>>>>>>time greater than>>>>>>>>>>>>>")
                                    house_shifting_data.completed = False
                                    house_shifting_data.save()
            return render(request, 'truck_app_web/house_shifting.html', {"house_shifting": house_shifting,
                                                                         "search_query": search_query})
        else:
            search_query = ""
            house_shifting = HouseShiftingDetails.objects.all().order_by('-created')
            house_shifting_detail = HouseShiftingDetails.objects.all().order_by('-created')
            for house_shifting_data in house_shifting_detail:
                print(">>>>for")
                if house_shifting_data.completed is False or house_shifting_data.completed is None:
                    completed_datetime = house_shifting_data.completed_date
                    if completed_datetime is not None:
                        completed_date = completed_datetime.date()
                        completed_time = completed_datetime.time()
                        now_date = now.date()
                        now_time = now.time()
                        if completed_date < now_date:
                            print(">>>>>>>date less than>>>>>>>>>>>>>")
                            house_shifting_data.completed = True
                            house_shifting_data.save()
                        elif completed_date == now_date:
                            print(">>>>>>>date equal to >>>>>>>>>>>>>")
                            if completed_time <= now_time:
                                print("<>>>>>>>>>>time less than or equal to>>>>>>>>>>>>>>>>>")
                                house_shifting_data.completed = True
                                house_shifting_data.save()
                else:
                    completed_datetime = house_shifting_data.completed_date
                    if house_shifting_data.completed is True:
                        if completed_datetime is not None:
                            completed_date = completed_datetime.date()
                            completed_time = completed_datetime.time()
                            now_date = now.date()
                            now_time = now.time()
                            if completed_date > now_date:
                                print(">>>>>>>date greater than>>>>>>>>>>>>>")
                                house_shifting_data.completed = False
                                house_shifting_data.save()
                            elif completed_date == now_date:
                                print(">>>>>>>date equal than>>>>>>>>>>>>>")
                                if completed_time > now_time:
                                    print(">>>>>>>time greater than>>>>>>>>>>>>>")
                                    house_shifting_data.completed = False
                                    house_shifting_data.save()
            return render(request, 'truck_app_web/house_shifting.html', {"house_shifting": house_shifting,
                                                                         "search_query": search_query})
    else:
        return redirect("login")


@login_required
def vehicle_shifting(request):
    request_user_id = request.user.id
    if request_user_id == 9:
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)
        if request.method == "POST":
            status = request.POST.get('status')
            search_query = request.POST.get('search')
            if status == "all":
                vehicle_shifting = VehicleShiftingDetails.objects.all().order_by('-created')
            elif status == "completed":
                vehicle_shifting = HouseShiftingDetails.objects.filter(completed=True).order_by('-created')
            elif status == "pending":
                vehicle_shifting = HouseShiftingDetails.objects.filter((Q(completed=False) | Q(completed__isnull=True))).order_by('-created')
            else:
                vehicle_shifting = HouseShiftingDetails.objects.all().order_by('-created')

            if search_query:
                try:
                    vehicle_shifting = vehicle_shifting.filter(booking_id=search_query).order_by('-created')
                except:
                    vehicle_shifting = VehicleShiftingDetails.objects.all().order_by('-created')
            vehicle_shifting_detail = VehicleShiftingDetails.objects.all().order_by('-created')
            for vehicle_shifting_data in vehicle_shifting_detail:
                print("for")
                if vehicle_shifting_data.completed is False or vehicle_shifting_data.completed is None:
                    completed_datetime = vehicle_shifting_data.completed_date
                    if completed_datetime is not None:
                        completed_date = completed_datetime.date()
                        completed_time = completed_datetime.time()
                        now_date = now.date()
                        now_time = now.time()
                        if completed_date < now_date:
                            print(">>>>>>>date less than>>>>>>>>>>>>>")
                            vehicle_shifting_data.completed = True
                            vehicle_shifting_data.save()
                        elif completed_date == now_date:
                            print(">>>>>>>date equal to >>>>>>>>>>>>>")
                            if completed_time <= now_time:
                                print("<>>>>>>>>>>time less than or equal to>>>>>>>>>>>>>>>>>")
                                vehicle_shifting_data.completed = True
                                vehicle_shifting_data.save()
                else:
                    completed_datetime = vehicle_shifting_data.completed_date
                    if vehicle_shifting_data.completed is True:
                        if completed_datetime is not None:
                            completed_date = completed_datetime.date()
                            completed_time = completed_datetime.time()
                            now_date = now.date()
                            now_time = now.time()
                            if completed_date > now_date:
                                print(">>>>>>>date greater than>>>>>>>>>>>>>")
                                vehicle_shifting_data.completed = False
                                vehicle_shifting_data.save()
                            elif completed_date == now_date:
                                print(">>>>>>>date equal than>>>>>>>>>>>>>")
                                if completed_time > now_time:
                                    print(">>>>>>>time greater than>>>>>>>>>>>>>")
                                    vehicle_shifting_data.completed = False
                                    vehicle_shifting_data.save()
            return render(request, 'truck_app_web/vehicle_shifting.html', {"vehicle_shifting": vehicle_shifting,
                                                                           "search_query": search_query})
        else:
            search_query = ""
            vehicle_shifting = VehicleShiftingDetails.objects.all().order_by('-created')
            vehicle_shifting_detail = VehicleShiftingDetails.objects.all().order_by('-created')
            for vehicle_shifting_data in vehicle_shifting_detail:
                print("for")
                if vehicle_shifting_data.completed is False or vehicle_shifting_data.completed is None:
                    completed_datetime = vehicle_shifting_data.completed_date
                    if completed_datetime is not None:
                        completed_date = completed_datetime.date()
                        completed_time = completed_datetime.time()
                        now_date = now.date()
                        now_time = now.time()
                        if completed_date < now_date:
                            print(">>>>>>>date less than>>>>>>>>>>>>>")
                            vehicle_shifting_data.completed = True
                            vehicle_shifting_data.save()
                        elif completed_date == now_date:
                            print(">>>>>>>date equal to >>>>>>>>>>>>>")
                            if completed_time <= now_time:
                                print("<>>>>>>>>>>time less than or equal to>>>>>>>>>>>>>>>>>")
                                vehicle_shifting_data.completed = True
                                vehicle_shifting_data.save()
                else:
                    completed_datetime = vehicle_shifting_data.completed_date
                    if vehicle_shifting_data.completed is True:
                        if completed_datetime is not None:
                            completed_date = completed_datetime.date()
                            completed_time = completed_datetime.time()
                            now_date = now.date()
                            now_time = now.time()
                            if completed_date > now_date:
                                print(">>>>>>>date greater than>>>>>>>>>>>>>")
                                vehicle_shifting_data.completed = False
                                vehicle_shifting_data.save()
                            elif completed_date == now_date:
                                print(">>>>>>>date equal than>>>>>>>>>>>>>")
                                if completed_time > now_time:
                                    print(">>>>>>>time greater than>>>>>>>>>>>>>")
                                    vehicle_shifting_data.completed = False
                                    vehicle_shifting_data.save()
            return render(request, 'truck_app_web/vehicle_shifting.html', {"vehicle_shifting": vehicle_shifting,
                                                                           "search_query": search_query})
    else:
        return redirect("login")


@login_required
def warehouse_shifting(request):
    request_user_id = request.user.id
    if request_user_id == 9:
        india_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(india_tz)
        if request.method == "POST":
            status = request.POST.get('status')
            search_query = request.POST.get('search')
            if status == "all":
                warehouse_shifting = WareHouseStorageDetails.objects.all().order_by('-created')
            elif status == "completed":
                warehouse_shifting = WareHouseStorageDetails.objects.filter(completed=True).order_by('-created')
            elif status == "pending":
                warehouse_shifting = WareHouseStorageDetails.objects.filter((Q(completed=False) | Q(completed__isnull=True))).order_by('-created')
            else:
                warehouse_shifting = WareHouseStorageDetails.objects.all().order_by('-created')
            if search_query:
                try:
                    warehouse_shifting = warehouse_shifting.filter(booking_id=search_query).order_by('-created')
                except:
                    warehouse_shifting = WareHouseStorageDetails.objects.all().order_by('-created')

            warehouse_shifting_detail = WareHouseStorageDetails.objects.all().order_by('-created')
            for warehouse_shifting_data in warehouse_shifting_detail:
                print("for")
                if warehouse_shifting_data.completed is False or warehouse_shifting_data.completed is None:
                    completed_datetime = warehouse_shifting_data.completed_date
                    if completed_datetime is not None:
                        completed_date = completed_datetime.date()
                        completed_time = completed_datetime.time()
                        now_date = now.date()
                        now_time = now.time()
                        if completed_date < now_date:
                            print(">>>>>>>date less than>>>>>>>>>>>>>")
                            warehouse_shifting_data.completed = True
                            warehouse_shifting_data.save()
                        elif completed_date == now_date:
                            print(">>>>>>>date equal to >>>>>>>>>>>>>")
                            if completed_time <= now_time:
                                print("<>>>>>>>>>>time less than or equal to>>>>>>>>>>>>>>>>>")
                                warehouse_shifting_data.completed = True
                                warehouse_shifting_data.save()
                else:
                    completed_datetime = warehouse_shifting_data.completed_date
                    if warehouse_shifting_data.completed is True:
                        if completed_datetime is not None:
                            completed_date = completed_datetime.date()
                            completed_time = completed_datetime.time()
                            now_date = now.date()
                            now_time = now.time()
                            if completed_date > now_date:
                                print(">>>>>>>date greater than>>>>>>>>>>>>>")
                                warehouse_shifting_data.completed = False
                                warehouse_shifting_data.save()
                            elif completed_date == now_date:
                                print(">>>>>>>date equal than>>>>>>>>>>>>>")
                                if completed_time > now_time:
                                    print(">>>>>>>time greater than>>>>>>>>>>>>>")
                                    warehouse_shifting_data.completed = False
                                    warehouse_shifting_data.save()

            return render(request, 'truck_app_web/warehouse_shifting.html', {"warehouse_shifting": warehouse_shifting,
                                                                             "search_query": search_query})
        else:
            search_query = ""
            warehouse_shifting = WareHouseStorageDetails.objects.all().order_by('-created')
            warehouse_shifting_detail = WareHouseStorageDetails.objects.all().order_by('-created')
            for warehouse_shifting_data in warehouse_shifting_detail:
                print("for")
                if warehouse_shifting_data.completed is False or warehouse_shifting_data.completed is None:
                    completed_datetime = warehouse_shifting_data.completed_date
                    if completed_datetime is not None:
                        completed_date = completed_datetime.date()
                        completed_time = completed_datetime.time()
                        now_date = now.date()
                        now_time = now.time()
                        if completed_date < now_date:
                            print(">>>>>>>date less than>>>>>>>>>>>>>")
                            warehouse_shifting_data.completed = True
                            warehouse_shifting_data.save()
                        elif completed_date == now_date:
                            print(">>>>>>>date equal to >>>>>>>>>>>>>")
                            if completed_time <= now_time:
                                print("<>>>>>>>>>>time less than or equal to>>>>>>>>>>>>>>>>>")
                                warehouse_shifting_data.completed = True
                                warehouse_shifting_data.save()
                else:
                    completed_datetime = warehouse_shifting_data.completed_date
                    if warehouse_shifting_data.completed is True:
                        if completed_datetime is not None:
                            completed_date = completed_datetime.date()
                            completed_time = completed_datetime.time()
                            now_date = now.date()
                            now_time = now.time()
                            if completed_date > now_date:
                                print(">>>>>>>date greater than>>>>>>>>>>>>>")
                                warehouse_shifting_data.completed = False
                                warehouse_shifting_data.save()
                            elif completed_date == now_date:
                                print(">>>>>>>date equal than>>>>>>>>>>>>>")
                                if completed_time > now_time:
                                    print(">>>>>>>time greater than>>>>>>>>>>>>>")
                                    warehouse_shifting_data.completed = False
                                    warehouse_shifting_data.save()

            return render(request, 'truck_app_web/warehouse_shifting.html', {"warehouse_shifting": warehouse_shifting,
                                                                             "search_query": search_query})
    else:
        return redirect("login")


# @login_required
# def completed(request):
#     request_user_id = request.user.id
#     if request_user_id == 9:
#         house_shifting_table = HouseShiftingDetails.objects.filter(completed=True)
#         vehicle_shifting_table = VehicleShiftingDetails.objects.filter(completed=True)
#         # warehouse_shifting_table = WareHouseStorageDetails.objects.filter(completed=True)
#         three_tables_data = house_shifting_table.union(vehicle_shifting_table)
#         combined_data = []
#         for three_table_data in three_tables_data:
#             combined_data.append(three_table_data)
#         print("combined_data",combined_data)
#         return render(request, 'truck_app_web/completed.html', {'data': combined_data})


# @login_required
# def completed(request):
#     request_user_id = request.user.id
#     if request_user_id == 9:
#         house_shifting_table = HouseShiftingDetails.objects.filter(completed=True)
#         vehicle_shifting_table = VehicleShiftingDetails.objects.filter(completed=True)
#         warehouse_shifting_table = WareHouseStorageDetails.objects.filter(completed=True)
#
#         return render(request, 'truck_app_web/completed.html', {'house_shifting_table': house_shifting_table,
#                                                                 'vehicle_shifting_table': vehicle_shifting_table,
#                                                                 'warehouse_shifting_table': warehouse_shifting_table})
#
#
# @login_required
# def pending(request):
#     request_user_id = request.user.id
#     if request_user_id == 9:
#         house_shifting_table = HouseShiftingDetails.objects.filter((Q(completed=False) | Q(completed__isnull=True)))
#         vehicle_shifting_table = VehicleShiftingDetails.objects.filter((Q(completed=False) | Q(completed__isnull=True)))
#         warehouse_shifting_table = WareHouseStorageDetails.objects.filter((Q(completed=False) | Q(completed__isnull=True)))
#
#         return render(request, 'truck_app_web/pending.html', {'house_shifting_table': house_shifting_table,
#                                                               'vehicle_shifting_table': vehicle_shifting_table,
#                                                               'warehouse_shifting_table': warehouse_shifting_table})


@login_required
def house_shifting_details(request, id):
    request_user_id = request.user.id
    if request_user_id == 9:
        house_shifting_detail_id = id
        if house_shifting_detail_id:
            if request.method == 'POST':
                try:
                    completed_date = request.POST['completed_date']
                except:
                    completed_date = ""
                if completed_date is not None:
                    date_obj = datetime.strptime(completed_date, '%Y-%m-%dT%H:%M')
                    date_formatted = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    HouseShiftingDetails.objects.filter(id=house_shifting_detail_id).update(completed_date=date_formatted)
                    house_shifting_detail = HouseShiftingDetails.objects.filter(id=house_shifting_detail_id).first()
                    user_id = house_shifting_detail.user_id
                    my_datetime_str = house_shifting_detail.completed_date
                    completed_date = my_datetime_str.strftime("%Y-%m-%dT%H:%M")
                    user_profile = UserProfile.objects.filter(user=user_id).first()
                    return render(request, 'truck_app_web/houseshifting_details.html',
                                  {"house_shifting_detail": house_shifting_detail,
                                   "user_profile": user_profile,
                                   "completed_date": completed_date})
            else:
                house_shifting_detail = HouseShiftingDetails.objects.filter(id=house_shifting_detail_id).first()
                my_datetime_str = house_shifting_detail.completed_date
                if my_datetime_str is not None:
                    completed_date = my_datetime_str.strftime("%Y-%m-%dT%H:%M")
                else:
                    completed_date = ""
                user_id = house_shifting_detail.user_id
                user_profile = UserProfile.objects.filter(user=user_id).first()
                return render(request, 'truck_app_web/houseshifting_details.html',
                              {"house_shifting_detail": house_shifting_detail,
                               "user_profile": user_profile,
                               "completed_date": completed_date})
        else:
            return render(request, "truck_app_web/houseshifting_details.html")
    else:
        return redirect("login")


@login_required
def vehicle_shifting_details(request, id):
    request_user_id = request.user.id
    if request_user_id == 9:
        vehicle_shifting_detail_id = id
        if vehicle_shifting_detail_id:
            if request.method == 'POST':
                try:
                    completed_date = request.POST['completed_date']
                except:
                    completed_date = ""
                if completed_date is not None:
                    date_obj = datetime.strptime(completed_date, '%Y-%m-%dT%H:%M')
                    date_formatted = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    VehicleShiftingDetails.objects.filter(id=vehicle_shifting_detail_id).update(
                        completed_date=date_formatted)
                    vehicle_shifting_detail = VehicleShiftingDetails.objects.filter(id=vehicle_shifting_detail_id).first()
                    user_id = vehicle_shifting_detail.user_id
                    my_datetime_str = vehicle_shifting_detail.completed_date
                    completed_date = my_datetime_str.strftime("%Y-%m-%dT%H:%M")
                    user_profile = UserProfile.objects.filter(user=user_id).first()
                    return render(request, 'truck_app_web/vehicleshifting_details.html',
                                  {"vehicle_shifting_detail": vehicle_shifting_detail,
                                   "user_profile": user_profile,
                                   "completed_date": completed_date})

            else:
                vehicle_shifting_detail = VehicleShiftingDetails.objects.filter(id=vehicle_shifting_detail_id).first()
                my_datetime_str = vehicle_shifting_detail.completed_date
                if my_datetime_str is not None:
                    completed_date = my_datetime_str.strftime("%Y-%m-%dT%H:%M")
                else:
                    completed_date = ""
                user_id = vehicle_shifting_detail.user_id
                user_profile = UserProfile.objects.filter(user=user_id).first()
                return render(request, 'truck_app_web/vehicleshifting_details.html',
                              {"vehicle_shifting_detail": vehicle_shifting_detail,
                               "user_profile": user_profile,
                               "completed_date": completed_date})

    else:
        return redirect("login")


@login_required
def warehouse_shifting_details(request, id):
    request_user_id = request.user.id
    if request_user_id == 9:
        warehouse_shifting_details_id = id
        if warehouse_shifting_details_id:
            if request.method == 'POST':
                try:
                    completed_date = request.POST['completed_date']
                except:
                    completed_date = ""
                if completed_date is not None:
                    date_obj = datetime.strptime(completed_date, '%Y-%m-%dT%H:%M')
                    date_formatted = date_obj.strftime('%Y-%m-%d %H:%M:%S')
                    WareHouseStorageDetails.objects.filter(id=warehouse_shifting_details_id).update(
                        completed_date=date_formatted)
                    warehouse_shifting_detail = WareHouseStorageDetails.objects.filter(id=warehouse_shifting_details_id).first()
                    user_id = warehouse_shifting_detail.user_id
                    my_datetime_str = warehouse_shifting_detail.completed_date
                    completed_date = my_datetime_str.strftime("%Y-%m-%dT%H:%M")
                    user_profile = UserProfile.objects.filter(user=user_id).first()
                    return render(request, 'truck_app_web/warehouseshifting_details.html',
                                  {"warehouse_shifting_detail": warehouse_shifting_detail,
                                   "user_profile": user_profile,
                                   "completed_date": completed_date})
            else:
                warehouse_shifting_detail = WareHouseStorageDetails.objects.filter(id=warehouse_shifting_details_id).first()
                my_datetime_str = warehouse_shifting_detail.completed_date
                if my_datetime_str is not None:
                    completed_date = my_datetime_str.strftime("%Y-%m-%dT%H:%M")
                else:
                    completed_date = ""
                user_id = warehouse_shifting_detail.user_id
                user_profile = UserProfile.objects.filter(user=user_id).first()
                return render(request, 'truck_app_web/warehouseshifting_details.html',
                              {"warehouse_shifting_detail": warehouse_shifting_detail,
                               "user_profile": user_profile,
                               "completed_date": completed_date})
        else:
            return render(request, "truck_app_web/warehouseshifting_details.html")
    else:
        return redirect("login")


def testing(request):


    url = "https://2factor.in/API/V1//SMS/+919999999999/AUTOGEN/OTP1"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

    return render(request, 'truck_app_web/testing.html')


def verify_phone_number(request):
    if request.method == "POST":
        phone_number = request.POST['phone_number']
        print("phone_number", phone_number)
        user_phone_number = User.objects.values_list("phone_number", flat=True)
        for phone_number_list in user_phone_number:
            print("fnvkjhvbdjkhvdjkfvdsfvh n", phone_number_list)
            if phone_number_list == phone_number:
                print("phone_nfhbvdfumber",phone_number)
                phone_numbers = "+91" + phone_number
                print("phone_numbers", phone_numbers)
                url_1 = "https://2factor.in/API/V1"
                api_key = "/8375cfcd-077a-11ee-addf-0200cd936042"
                sms = "/SMS/"
                auto_generate = "/AUTOGEN2/APM_testing_OTP"
                # template_name = "/APM_testing_OTP"
                url = url_1 + api_key + sms + phone_numbers + auto_generate
                print("url", url)
                payload = {}
                headers = {}
                response = requests.request("GET", url, headers=headers, data=payload)
                response_json = json.loads(response.text)
                otp = response_json["OTP"]
                register = Register.objects.filter(user_phone_number=phone_number).first()
                register.otp = otp
                register.save()
                return render(request, 'truck_app_web/verify_otp.html', {"otp": otp,
                                                                         "phone_number": phone_number})
        else:
            messages.success(request, 'Invalid Phone Number.')
            return render(request, 'truck_app_web/verify_phone_number.html')
    return render(request, 'truck_app_web/verify_phone_number.html')


def change_new_password(request, phone_number):
    phone_number = phone_number
    if request.method == "POST":

        try:
            password_1 = request.POST["password1"]
        except:
            password_1 = ""

        try:
            password_2 = request.POST["password2"]
        except:
            password_2 = ""

        if password_1:
            len_password = len(password_1)
            regex = r"[~!@#$%^&*()_+`\-={}\[\]:\";'<>?,./]"
            password = request.POST['password1']
            if re.search(regex, password) and len_password > 7:
                user = User.objects.filter(phone_number=phone_number).first()
                user.set_password(password_1)
                user.save()
                phone_number = user.phone_number
                register = Register.objects.filter(user_phone_number=phone_number).first()
                register.password1 = password_1
                register.password2 = password_2
                register.is_verified = True
                register.save()
                messages.success(request,
                                 "Password Should contains atleast 1 special character, alphabets and morethan or equal 8 Characters")
                return render(request, 'truck_app_web/change_new_password.html')
            else:
                messages.success(request,
                                 "Password Should contains atleast 1 special character, alphabets and morethan or equal 8 Characters")
                return render(request, 'truck_app_web/change_new_password.html')
        else:
            return render(request, 'truck_app_web/change_new_password.html')
    return render(request, 'truck_app_web/change_new_password.html')

