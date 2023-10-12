from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .functions import remove_string
import requests
from datetime import datetime
from django.utils.dateparse import parse_datetime
import random
import re


from .models import CustomUser as User
from .models import UserProfile
from .models import Register
from .models import HouseShiftingDetails
from .models import HouseShiftingProducts
from .models import VehicleShiftingDetails
from .models import ChosenShiftingVehicle
from .models import WareHouseStorageDetails
from .models import WareHouseSelectedVehicle
from .models import WareHouseStoringProducts
from .models import OrderBooking
from .models import HouseShiftingSelectedVehicle
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session as session
from django.contrib.auth.hashers import make_password
import json
from django.shortcuts import render
from .forms import CustomUserCreationForm
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from truckapp_project import settings


def webpage(request):
    return render(request, 'truck_app/index.html')


# Create your views here.
@csrf_exempt
def login(request):
    """Login the Registered Users in the app"""
    header_secret_key = request.headers['Authorization']
    settings_secret_key = settings.SECRET_KEY
    if header_secret_key == settings_secret_key:
        request_data = json.loads(request.body)
        if request_data:
            phone_number = request_data['phone_number']
            password = request_data['password']
            user = User.objects.filter(phone_number=phone_number).first()
            registered_user = Register.objects.filter(user_phone_number=phone_number).first()
            register_id = registered_user.id
            if user is not None:
                print("user.password", registered_user.password1)
                if password != registered_user.password1:
                    return JsonResponse({'status_code': 400, 'message': 'User Password is Wrong'}, safe=False)

                else:
                    if registered_user.is_verified == True:
                        login_user = User.objects.filter(phone_number=phone_number).first()
                        user_id = login_user.id
                        return JsonResponse({'status_code': 200, 'message': 'User Login Successfully', 'user_id': user_id},
                                            safe=False)
                    else:
                        if registered_user.is_verified == None:
                            user_phone_number = User.objects.values_list("phone_number", flat=True)
                            for phone_number_list in user_phone_number:
                                if phone_number_list == phone_number:
                                    phone_numbers = "+91" + phone_number
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
                                    registered_user.otp = otp
                                    registered_user.save()
                                    return JsonResponse({'status_code': 500,
                                                         "otp": otp,
                                                         "register_id": register_id,
                                                         'message': 'User ID Not verified'}, safe=False)

            else:
                return JsonResponse({'status_code': 400, 'message': 'User ID Not Register'}, safe=False)
    else:
        return JsonResponse({'status_code': 407, 'message': 'Need to enter the proper authentication SECRET KEY'})


@csrf_exempt
def resend_otp(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        now = timezone.localtime(timezone.now())
        user_phone_number = request_data['phone_number']
        print("user_phone_number", user_phone_number)
        user_id = request_data['user_id']
        print("user_id",user_id)
        phone_number_list = User.objects.values_list("phone_number", flat=True)
        print("phone_number_list", phone_number_list)
        if user_phone_number in phone_number_list:
            print(">>>>>>>>>>>>>>>>>>")
            phone_number = "+91" + user_phone_number
            url_1 = "https://2factor.in/API/V1"
            api_key = "/8375cfcd-077a-11ee-addf-0200cd936042"
            sms = "/SMS/"
            auto_generate = "/AUTOGEN2/APM_testing_OTP"
            # template_name = "/APM_testing_OTP"
            url = url_1 + api_key + sms + phone_number + auto_generate
            print("url", url)
            payload = {}
            headers = {}

            response = requests.request("GET", url, headers=headers, data=payload)

            response_json = json.loads(response.text)
            otp = response_json["OTP"]
            print("otp",otp)
            register = Register.objects.filter(user_phone_number=user_phone_number).first()
            register.otp = otp
            register.save()
            register_id = register.id
            return JsonResponse({'status_code': 200,
                                 'message': 'OTP Send successfully',
                                 "OTP": otp,
                                 "register_id": register_id,
                                 "user_id": user_id})


@csrf_exempt
def register(request):
    """Get the Register user data store in User(CustomUser) and UserProfile Table"""
    # Checking the requesting the data method
    if request.method == 'POST':
        request_data = json.loads(request.body)

        now = timezone.localtime(timezone.now())
        register_datetime = timezone.localtime(timezone.now())

        str_user_name = request_data['user_name']
        user_name = remove_string(str_user_name)
        if user_name == '':
            user_name = 'null'

        str_user_phone_number = request_data['phone_number']
        user_phone_number = remove_string(str_user_phone_number)
        if user_phone_number == '':
            user_phone_number = 'null'

        str_user_email = request_data['email']
        user_email = remove_string(str_user_email)
        if user_email == '':
            user_email = 'null'

        len_password = len(request_data['password1'])
        regex = r"[~!@#$%^&*()_+`\-={}\[\]:\";'<>?,./]"
        password = request_data['password1']
        if re.search(regex, password) and len_password > 7:
            str_password = request_data['password1']
            password1 = remove_string(str_password)
            if password1 == '':
                password1 = 'null'

            str_password = request_data['password2']
            password2 = remove_string(str_password)
            if password2 == '':
                password2 = 'null'

            str_terms_condition = request_data['terms_condition']
            terms_condition = remove_string(str_terms_condition)
            if terms_condition == "1":
                terms_condition = True

            str_privacy_policy = request_data['privacy_policy']
            privacy_policy = remove_string(str_privacy_policy)
            if privacy_policy == "1":
                privacy_policy = True

            otp = None
            phone_number_list = User.objects.values_list("phone_number", flat=True)
            if user_phone_number not in phone_number_list:
                phone_number = "+91" + user_phone_number
                url_1 = "https://2factor.in/API/V1"
                api_key = "/8375cfcd-077a-11ee-addf-0200cd936042"
                sms = "/SMS/"
                auto_generate = "/AUTOGEN2/APM_testing_OTP"
                # template_name = "/APM_testing_OTP"
                url = url_1 + api_key + sms + phone_number + auto_generate
                print("url",url)
                payload = {}
                headers = {}

                response = requests.request("GET", url, headers=headers, data=payload)

                response_json = json.loads(response.text)
                otp = response_json["OTP"]

            form = CustomUserCreationForm(request_data)

            if form.is_valid():
                form.save()
                user_id = User.objects.values('id').order_by('-id').first()['id']
                User.objects.filter(id=user_id).update(first_name=user_name)
                session = SessionStore()
                session["user_id"] = user_id
                session["user_name"] = user_name
                session["phone_number"] = user_phone_number
                session["email"] = user_email
                session["password1"] = password1
                session["password2"] = password2
                session.save()

                register = Register(user_name=user_name,
                                    user_phone_number=user_phone_number,
                                    user_email=user_email,
                                    password1=password1,
                                    password2=password2,
                                    terms_condition=terms_condition,
                                    privacy_policy=privacy_policy,
                                    registered_datetime=register_datetime,
                                    otp=otp,
                                    created=now,
                                    updated=now)
                register.save()

                user = User.objects.filter(id=user_id).first()
                user_profile = UserProfile(user=user,
                                           user_name=user_name,
                                           user_phone_number=user_phone_number,
                                           user_email=user_email,
                                           password=password1,
                                           terms_condition=terms_condition,
                                           privacy_policy=privacy_policy,
                                           user_created=register_datetime,
                                           created=now,
                                           updated=now)
                user_profile.save()

                return JsonResponse({'status_code': 200,
                                     'message': 'User Register Successfully',
                                     'otp': otp,
                                     "user_id": user.id,
                                     "register_id": register.id}, safe=False)

            else:
                return JsonResponse({'status_code': 400,
                                     "message": " This user id is already registered"})

        else:
            return JsonResponse({'status_code': 400, "message": "Password Should contains atleast 1 special character, alphabets and morethan or equal 8 Characters"})

    return JsonResponse({'message': 'Register Page'}, safe=False)


@csrf_exempt
def verify_otp(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        register_id = request_data['register_id']
        otp = request_data['otp']
        try:
            register = Register.objects.get(id=register_id)
            if register.otp == otp:
                register.is_verified = True
                register.save()
                return JsonResponse({'message': "OTP verified successfully."})
            else:
                return JsonResponse({"message": 'Invalid OTP.'})
        except:
            return JsonResponse({"message": 'User not found'})


@csrf_exempt
def verify_phone_number(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        phone_number = request_data["phone_number"]
        user_phone_number = User.objects.values_list("phone_number", flat=True)
        for phone_number_list in user_phone_number:
            print("phone_number_list",phone_number_list)
            if phone_number_list == phone_number:
                print("phone_number_list--phone_number_list",phone_number_list)
                phone_numbers = "+91" + phone_number
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
                register_id = register.id
                return JsonResponse({"status": 200,
                                     "register_id": register_id,
                                     "OTP": otp,
                                     "message": "phone number verify OTP send successfully"})
    else:
        return JsonResponse({"message": "forget password page"})


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        register_id = request_data["register_id"]
        phone_number = request_data["phone_number"]
        password_1 = request_data["password1"]
        password_2 = request_data["password2"]
        len_password = len(password_1)
        regex = r"[~!@#$%^&*()_+`\-={}\[\]:\";'<>?,./]"
        password = request_data['password1']
        if re.search(regex, password) and len_password > 7:
            register = Register.objects.filter(id=register_id).first()
            register.password1 = password_1
            register.password2 = password_2
            register.save()
            user = User.objects.filter(phone_number=phone_number).first()
            user.set_password(password_1)
            user.save()
            return JsonResponse({"status": 200,
                                 "message": "user password reset successfully"})
        else:
            return JsonResponse({'status_code': 400,
                                 "message": "Password Should contains atleast 1 special character, alphabets and "
                                            "morethan or equal 8 Characters"})


@csrf_exempt
def user_profile(request):
    """Get the user details through the user id"""
    if request.method == 'POST':
        header_secret_key = request.headers['Authorization']
        settings_secret_key = settings.SECRET_KEY
        if header_secret_key == settings_secret_key:
            request_data = json.loads(request.body)
            user_id = request_data["user_id"]

            # Getting the Login user's details from User(CustomUser) table
            user_profile = UserProfile.objects.filter(user_id=user_id).first()
            booking_count = OrderBooking.objects.filter(user=user_id).count()

            if user_profile is not None:
                user_name = user_profile.user_name

                if user_name is None or "":
                    user_name = "null"

                user_phone_number = user_profile.user_phone_number
                if user_phone_number is None or "":
                    user_phone_number = "null"

                user_email = user_profile.user_email
                if user_email is None or "":
                    user_email = "null"

                password = user_profile.password
                if password is None or "":
                    password = "null"

                return JsonResponse({'status_code': 200,
                                     'message': 'User Details',
                                     "user_id": user_id,
                                     "booking_count": booking_count,
                                     "user_name": user_name,
                                     "user_phone_number": user_phone_number,
                                     "user_email": user_email,
                                     "password": password}, safe=False)
            else:
                return JsonResponse({'status_code': 400, 'message': 'User Profile is None'})
        else:
            return JsonResponse({'status_code': 407, 'message': 'Need to enter the proper authentication SECRET KEY'})
    else:
        JsonResponse({'message': 'User Profile page'})


@csrf_exempt
def booking_details(request):
    if request.method == "POST":
        header_secret_key = request.headers['Authorization']
        settings_secret_key = settings.SECRET_KEY
        if header_secret_key == settings_secret_key:
            if request.body:
                now = timezone.localtime(timezone.now())
                request_data = json.loads(request.body)
                try:
                    user_id = request_data["user_id"]
                except:
                    user_id = ''

                user = User.objects.filter(id=user_id).first()
                booking_count = OrderBooking.objects.filter(user=user).order_by('-created')
                print("booking_count", booking_count)
                # Convert the query set to a list of dictionaries
                bookings = list(booking_count.values())
                print("bookings", bookings)
                return JsonResponse({'status_code': 200,
                                     'message': 'user booking details',
                                     "booking_details": bookings}, safe=False)
        else:
            return JsonResponse({'status_code': 407, 'message': 'Need to enter the proper authentication SECRET KEY'})


@csrf_exempt
def user_booking_details(request):
    if request.method == "POST":
        header_secret_key = request.headers['Authorization']
        settings_secret_key = settings.SECRET_KEY
        if header_secret_key == settings_secret_key:
            if request.body:
                print(">>>>")
                now = timezone.localtime(timezone.now())
                request_data = json.loads(request.body)

                try:
                    user_id = request_data["user_id"]
                except:
                    user_id = ''

                try:
                    house_shifting_details_id = request_data["house_shifting_details_id"]
                except:
                    house_shifting_details_id = ""

                try:
                    house_shifting_product_id = request_data["house_shifting_product_id"]
                except:
                    house_shifting_product_id = ""

                try:
                    vehicle_shifting_details_id = request_data["vehicle_shifting_details_id"]
                except:
                    vehicle_shifting_details_id = ""

                print("vehicle_shifting_details_id",vehicle_shifting_details_id)
                try:
                    chosen_shifting_vehicle_id = request_data["chosen_shifting_vehicle_details_id"]
                except:
                    chosen_shifting_vehicle_id = ""
                print("chosen_shifting_vehicle_id",chosen_shifting_vehicle_id)
                try:
                    warehouse_storing_details_id = request_data["warehouse_storing_details_id"]
                except:
                    warehouse_storing_details_id = ""

                print("warehouse_storing_details_id", warehouse_storing_details_id)
                try:
                    warehouse_storing_products_id = request_data["warehouse_storing_products_id"]
                except:
                    warehouse_storing_products_id = ""

                if house_shifting_details_id:
                    house_shifting_products_id = HouseShiftingProducts.objects.filter(id=house_shifting_product_id).first()
                    house_shifting_details_id_2 = house_shifting_products_id.house_shifting_details.id
                    if str(house_shifting_details_id_2) == house_shifting_details_id:
                        house_shifting_products = HouseShiftingProducts.objects.filter(id=house_shifting_product_id).first()
                        house_shifting_details_id_3 = house_shifting_products_id.house_shifting_details.id
                        summary_address_details = HouseShiftingDetails.objects.filter(
                            id=house_shifting_details_id_3).first()
                        user_id = summary_address_details.user.id
                        shifting_type = summary_address_details.shifting_type
                        moving_datetime = summary_address_details.moving_datetime
                        pickup_location = summary_address_details.pickup_location
                        pickup_address = summary_address_details.pickup_address
                        pickup_floor = summary_address_details.pickup_floor
                        pickup_lift = summary_address_details.pickup_lift
                        drop_location = summary_address_details.drop_location
                        drop_address = summary_address_details.drop_address
                        drop_floor = summary_address_details.drop_floor
                        drop_lift = summary_address_details.drop_lift

                        # house_shifting_selected_vehicle = HouseShiftingSelectedVehicle.objects \
                        #     .filter(house_shifting_details=house_shifting_details_id) \
                        #     .first()

                        if house_shifting_products.product_amount:
                            product_amount = house_shifting_products.product_amount
                        else:
                            product_amount = None

                        # if house_shifting_selected_vehicle.vehicle_amount:
                        #     vehicle_amount = house_shifting_selected_vehicle.vehicle_amount
                        # else:
                        #     vehicle_amount = None
                        #
                        # if house_shifting_selected_vehicle.total_shifting_KMs:
                        #     total_shifting_KMs = house_shifting_selected_vehicle.total_shifting_KMs
                        # else:
                        #     total_shifting_KMs = None

                        if house_shifting_products.single_sofa:
                            single_sofa = house_shifting_products.single_sofa
                        else:
                            single_sofa = None

                        if house_shifting_products.double_sofa:
                            double_sofa = house_shifting_products.double_sofa
                        else:
                            double_sofa = None

                        if house_shifting_products.three_seater:
                            three_seater = house_shifting_products.three_seater
                        else:
                            three_seater = None

                        if house_shifting_products.four_seater:
                            four_seater = house_shifting_products.four_seater
                        else:
                            four_seater = None

                        if house_shifting_products.five_seater:
                            five_seater = house_shifting_products.five_seater
                        else:
                            five_seater = None

                        if house_shifting_products.six_seater:
                            six_seater = house_shifting_products.six_seater
                        else:
                            six_seater = None

                        if house_shifting_products.recliner:
                            recliner = house_shifting_products.recliner
                        else:
                            recliner = None

                        if house_shifting_products.single_bed_storage:
                            single_bed_storage = house_shifting_products.single_bed_storage
                        else:
                            single_bed_storage = None

                        if house_shifting_products.single_bed_dismantallable:
                            single_bed_dismantallable = house_shifting_products.single_bed_dismantallable
                        else:
                            single_bed_dismantallable = None

                        if house_shifting_products.double_bed_storage:
                            double_bed_storage = house_shifting_products.double_bed_storage
                        else:
                            double_bed_storage = ""

                        if house_shifting_products.double_bed_dismantallable:
                            double_bed_dismantallable = house_shifting_products.double_bed_dismantallable
                        else:
                            double_bed_dismantallable = None

                        if house_shifting_products.bunk_dismantallabel:
                            bunk_dismantallabel = house_shifting_products.bunk_dismantallabel
                        else:
                            bunk_dismantallabel = None

                        if house_shifting_products.folding_cot_dismantallabel:
                            folding_cot_dismantallabel = house_shifting_products.folding_cot_dismantallabel
                        else:
                            folding_cot_dismantallabel = None

                        if house_shifting_products.single_mattress_foldable:
                            single_mattress_foldable = house_shifting_products.single_mattress_foldable
                        else:
                            single_mattress_foldable = None

                        if house_shifting_products.single_mattress_non_foldable:
                            single_mattress_non_foldable = house_shifting_products.single_mattress_non_foldable
                        else:
                            single_mattress_non_foldable = None

                        if house_shifting_products.double_mattress_foldable:
                            double_mattress_foldable = house_shifting_products.double_mattress_foldable
                        else:
                            double_mattress_foldable = None

                        if house_shifting_products.double_mattress_nonfoldable:
                            double_mattress_nonfoldable = house_shifting_products.double_mattress_nonfoldable
                        else:
                            double_mattress_nonfoldable = None

                        if house_shifting_products.dining_table_chairs:
                            dining_table_chairs = house_shifting_products.dining_table_chairs
                        else:
                            dining_table_chairs = None

                        if house_shifting_products.baby_chairs:
                            baby_chairs = house_shifting_products.baby_chairs
                        else:
                            baby_chairs = None

                        if house_shifting_products.rocking_chair:
                            rocking_chair = house_shifting_products.rocking_chair
                        else:
                            rocking_chair = None

                        if house_shifting_products.plastic_floding_chair:
                            plastic_floding_chair = house_shifting_products.plastic_floding_chair
                        else:
                            plastic_floding_chair = None

                        if house_shifting_products.office_chair:
                            office_chair = house_shifting_products.office_chair
                        else:
                            office_chair = None

                        if house_shifting_products.bed_side_table:
                            bed_side_table = house_shifting_products.bed_side_table
                        else:
                            bed_side_table = None

                        if house_shifting_products.dressing_table:
                            dressing_table = house_shifting_products.dressing_table
                        else:
                            dressing_table = None

                        if house_shifting_products.study_or_computer_table:
                            study_or_computer_table = house_shifting_products.study_or_computer_table
                        else:
                            study_or_computer_table = None

                        if house_shifting_products.center_table:
                            center_table = house_shifting_products.center_table
                        else:
                            center_table = None

                        if house_shifting_products.dining_table:
                            dining_table = house_shifting_products.dining_table
                        else:
                            dining_table = None

                        if house_shifting_products.tea_poy:
                            tea_poy = house_shifting_products.tea_poy
                        else:
                            tea_poy = None

                        if house_shifting_products.tv_stand:
                            tv_stand = house_shifting_products.tv_stand
                        else:
                            tv_stand = None

                        if house_shifting_products.book_self:
                            book_self = house_shifting_products.book_self
                        else:
                            book_self = None

                        if house_shifting_products.mirror:
                            mirror = house_shifting_products.mirror
                        else:
                            mirror = None

                        if house_shifting_products.shoe_rack:
                            shoe_rack = house_shifting_products.shoe_rack
                        else:
                            shoe_rack = None

                        if house_shifting_products.mandir:
                            mandir = house_shifting_products.mandir
                        else:
                            mandir = None

                        if house_shifting_products.iron_trunk_chest:
                            iron_trunk_chest = house_shifting_products.iron_trunk_chest
                        else:
                            iron_trunk_chest = None

                        if house_shifting_products.tv_size_upto_20:
                            tv_size_upto_20 = house_shifting_products.tv_size_upto_20
                        else:
                            tv_size_upto_20 = None

                        if house_shifting_products.tv_size_29to43:
                            tv_size_29to43 = house_shifting_products.tv_size_29to43
                        else:
                            tv_size_29to43 = None

                        if house_shifting_products.tv_size_49to55:
                            tv_size_49to55 = house_shifting_products.tv_size_49to55
                        else:
                            tv_size_49to55 = None

                        if house_shifting_products.tv_size_above55:
                            tv_size_above55 = house_shifting_products.tv_size_above55
                        else:
                            tv_size_above55 = None

                        if house_shifting_products.home_theater:
                            home_theater = house_shifting_products.home_theater
                        else:
                            home_theater = None

                        if house_shifting_products.ac_split:
                            ac_split = house_shifting_products.ac_split
                        else:
                            ac_split = None

                        if house_shifting_products.ac_window:
                            ac_window = house_shifting_products.ac_window
                        else:
                            ac_window = None

                        if house_shifting_products.cooler:
                            cooler = house_shifting_products.cooler
                        else:
                            cooler = None

                        if house_shifting_products.ceiling_fan:
                            ceiling_fan = house_shifting_products.ceiling_fan
                        else:
                            ceiling_fan = None

                        if house_shifting_products.table_fan:
                            table_fan = house_shifting_products.table_fan
                        else:
                            table_fan = None

                        if house_shifting_products.exhaust_fan:
                            exhaust_fan = house_shifting_products.exhaust_fan
                        else:
                            exhaust_fan = None

                        if house_shifting_products.mini_fridge:
                            mini_fridge = house_shifting_products.mini_fridge
                        else:
                            mini_fridge = None

                        if house_shifting_products.small_fridge:
                            small_fridge = house_shifting_products.small_fridge
                        else:
                            small_fridge = None

                        if house_shifting_products.medium_fridge:
                            medium_fridge = house_shifting_products.medium_fridge
                        else:
                            medium_fridge = None

                        if house_shifting_products.large_fridge:
                            large_fridge = house_shifting_products.large_fridge
                        else:
                            large_fridge = None

                        if house_shifting_products.large_above450_ltrs_fridge:
                            large_above450_ltrs_fridge = house_shifting_products.large_above450_ltrs_fridge
                        else:
                            large_above450_ltrs_fridge = None

                        if house_shifting_products.washing_machine:
                            washing_machine = house_shifting_products.washing_machine
                        else:
                            washing_machine = None

                        if house_shifting_products.geyser:
                            geyser = house_shifting_products.geyser
                        else:
                            geyser = None

                        if house_shifting_products.bath_tub:
                            bath_tub = house_shifting_products.bath_tub
                        else:
                            bath_tub = None

                        if house_shifting_products.gas_stove:
                            gas_stove = house_shifting_products.gas_stove
                        else:
                            gas_stove = None

                        if house_shifting_products.water_purifier:
                            water_purifier = house_shifting_products.water_purifier
                        else:
                            water_purifier = None

                        if house_shifting_products.microwave_otg:
                            microwave_otg = house_shifting_products.microwave_otg
                        else:
                            microwave_otg = None

                        if house_shifting_products.chimney:
                            chimney = house_shifting_products.chimney
                        else:
                            chimney = None

                        if house_shifting_products.dish_washer:
                            dish_washer = house_shifting_products.dish_washer
                        else:
                            dish_washer = None

                        if house_shifting_products.gas_cylinder:
                            gas_cylinder = house_shifting_products.gas_cylinder
                        else:
                            gas_cylinder = None

                        if house_shifting_products.inverter_ups:
                            inverter_ups = house_shifting_products.inverter_ups
                        else:
                            inverter_ups = None

                        if house_shifting_products.treadmill:
                            treadmill = house_shifting_products.treadmill
                        else:
                            treadmill = None

                        if house_shifting_products.piano_guitar:
                            piano_guitar = house_shifting_products.piano_guitar
                        else:
                            piano_guitar = None

                        if house_shifting_products.sewing_mechine:
                            sewing_mechine = house_shifting_products.sewing_mechine
                        else:
                            sewing_mechine = None

                        if house_shifting_products.vaccum_cleaner:
                            vaccum_cleaner = house_shifting_products.vaccum_cleaner
                        else:
                            vaccum_cleaner = None

                        if house_shifting_products.lamp:
                            lamp = house_shifting_products.lamp
                        else:
                            lamp = None

                        if house_shifting_products.plants:
                            plants = house_shifting_products.plants
                        else:
                            plants = None

                        if house_shifting_products.iron_board:
                            iron_board = house_shifting_products.iron_board
                        else:
                            iron_board = None

                        if house_shifting_products.dish_antenna:
                            dish_antenna = house_shifting_products.dish_antenna
                        else:
                            dish_antenna = None

                        if house_shifting_products.service_carton_box:
                            service_carton_box = house_shifting_products.service_carton_box
                        else:
                            service_carton_box = None

                        if house_shifting_products.self_carton_box:
                            self_carton_box = house_shifting_products.self_carton_box
                        else:
                            self_carton_box = None

                        if house_shifting_products.gunny_bags:
                            gunny_bags = house_shifting_products.gunny_bags
                        else:
                            gunny_bags = None

                        return JsonResponse({'status_code': 200,
                                             'message': 'User House Shifting Details',
                                             "user_id": user_id,
                                             "product_amount": product_amount,
                                             # "vehicle_amount": vehicle_amount,
                                             # "total_shifting_KMs": total_shifting_KMs,
                                             "house_shifting_details_id": house_shifting_details_id,
                                             "house_shifting_product_id": house_shifting_product_id,
                                             # "house_shifting_selected_vehicle_id": house_shifting_selected_vehicle.id,
                                             "shifting_type": shifting_type,
                                             "moving_datetime": moving_datetime,
                                             "pickup_location": pickup_location,
                                             "pickup_address": pickup_address,
                                             "pickup_floor": pickup_floor,
                                             "pickup_lift": pickup_lift,
                                             "drop_location": drop_location,
                                             "drop_address": drop_address,
                                             "drop_floor": drop_floor,
                                             "drop_lift": drop_lift,

                                             "sofa": {
                                                 "single_sofa": single_sofa,
                                                 "double_sofa": double_sofa,
                                                 "three_seater": three_seater,
                                                 "four_seater": four_seater,
                                                 "five_seater": five_seater,
                                                 "six_seater": six_seater,
                                                 "recliner": recliner
                                             },
                                             "bed": {
                                                 "single_bed_storage": single_bed_storage,
                                                 "single_bed_dismantallable": single_bed_dismantallable,
                                                 "double_bed_storage": double_bed_storage,
                                                 "double_bed_dismantallable": double_bed_dismantallable,
                                                 "bunk_dismantallabel": bunk_dismantallabel,
                                                 "folding_cot_dismantallabel": folding_cot_dismantallabel
                                             },
                                             "mattress": {
                                                 "single_mattress_foldable": single_mattress_foldable,
                                                 "single_mattress_non_foldable": single_mattress_non_foldable,
                                                 "double_mattress_foldable": double_mattress_foldable,
                                                 "double_mattress_nonfoldable": double_mattress_nonfoldable
                                             },
                                             "chairs": {
                                                 "dining_table_chairs": dining_table_chairs,
                                                 "baby_chairs": baby_chairs,
                                                 "rocking_chair": rocking_chair,
                                                 "plastic_floding_chair": plastic_floding_chair,
                                                 "office_chair": office_chair
                                             },
                                             "tables": {
                                                 "bed_side_table": bed_side_table,
                                                 "dressing_table": dressing_table,
                                                 "study_or_computer_table": study_or_computer_table,
                                                 "center_table": center_table,
                                                 "dining_table": dining_table,
                                                 "tea_poy": tea_poy
                                             },
                                             "accessories": {
                                                 "tv_stand": tv_stand,
                                                 "book_self": book_self,
                                                 "mirror": mirror,
                                                 "shoe_rack": shoe_rack,
                                                 "mandir": mandir,
                                                 "iron_trunk_chest": iron_trunk_chest
                                             },
                                             "tv": {
                                                 "tv_size_upto_20": tv_size_upto_20,
                                                 "tv_size_29to43": tv_size_29to43,
                                                 "tv_size_49to55": tv_size_49to55,
                                                 "tv_size_above55": tv_size_above55,
                                                 "home_theater": home_theater
                                             },
                                             "ac": {
                                                 "ac_split": ac_split,
                                                 "ac_window": ac_window,
                                                 "cooler": cooler,
                                                 "ceiling_fan": ceiling_fan,
                                                 "table_fan": table_fan,
                                                 "exhaust_fan": exhaust_fan
                                             },
                                             "fridge": {
                                                 "mini_fridge": mini_fridge,
                                                 "small_fridge": small_fridge,
                                                 "medium_fridge": medium_fridge,
                                                 "large_fridge": large_fridge,
                                                 "large_above450_ltrs_fridge": large_above450_ltrs_fridge
                                             },
                                             "bathroom": {
                                                 "washing_machine": washing_machine,
                                                 "geyser": geyser,
                                                 "bath_tub": bath_tub
                                             },
                                             "kitchen_utility": {
                                                 "gas_stove": gas_stove,
                                                 "water_purifier": water_purifier,
                                                 "microwave_otg": microwave_otg,
                                                 "chimney": chimney,
                                                 "dish_washer": dish_washer,
                                                 "gas_cylinder": gas_cylinder
                                             },
                                             "others": {
                                                 "inverter_ups": inverter_ups,
                                                 "treadmill": treadmill,
                                                 "piano_guitar": piano_guitar
                                             },
                                             "home_utility": {
                                                 "sewing_mechine": sewing_mechine,
                                                 "vaccum_cleaner": vaccum_cleaner,
                                                 "lamp": lamp,
                                                 "plants": plants,
                                                 "iron_board": iron_board,
                                                 "dish_antenna": dish_antenna
                                             },
                                             "cartons": {
                                                 "service_carton_box": service_carton_box,
                                                 "self_carton_box": self_carton_box
                                             },
                                             "gunny_bags": {
                                                 "gunny_bags": gunny_bags
                                             }

                                             })
                elif vehicle_shifting_details_id:
                    chosen_shifting_vehicle_details = ChosenShiftingVehicle.objects.filter(
                        id=chosen_shifting_vehicle_id).first()
                    vehicle_shifting_details_id_2 = chosen_shifting_vehicle_details.vehicle_shifting_details.id
                    if str(vehicle_shifting_details_id_2) == vehicle_shifting_details_id:
                        summary_address_details = VehicleShiftingDetails.objects.filter(
                            id=vehicle_shifting_details_id).first()
                        user_id = summary_address_details.user.id
                        vehicle_shifting_details_id = summary_address_details.id
                        moving_datetime = summary_address_details.moving_datetime
                        pickup_location = summary_address_details.pickup_location
                        pickup_address = summary_address_details.pickup_address
                        pickup_floor = summary_address_details.pickup_floor
                        pickup_lift = summary_address_details.pickup_lift
                        drop_location = summary_address_details.drop_location
                        drop_address = summary_address_details.drop_address
                        drop_floor = summary_address_details.drop_floor
                        drop_lift = summary_address_details.drop_lift
                        vehicle_name = None
                        vehicle_model = None
                        vehicle_image = None
                        vehicle_amount = None

                        if chosen_shifting_vehicle_details:
                            vehicle_name = chosen_shifting_vehicle_details.vehicle_name
                            if vehicle_name is None:
                                vehicle_name = "Empty"

                            vehicle_model = chosen_shifting_vehicle_details.vehicle_model
                            if vehicle_model is None:
                                vehicle_model = "Empty"

                            vehicle_image = chosen_shifting_vehicle_details.vehicle_image
                            if vehicle_image is None:
                                vehicle_image = "Empty"

                            vehicle_amount = chosen_shifting_vehicle_details.vehicle_amount
                            if vehicle_amount is None:
                                vehicle_amount = "Empty"

                        return JsonResponse({'status_code': 200,
                                             'message': 'User Vehicle Shifting Details',
                                             "user_id": user_id,
                                             "vehicle_shifting_details_id": vehicle_shifting_details_id,
                                             "chosen_shifting_vehicle_id": chosen_shifting_vehicle_id,
                                             "moving_datetime": moving_datetime,
                                             "pickup_location": pickup_location,
                                             "pickup_address": pickup_address,
                                             "pickup_floor": pickup_floor,
                                             "pickup_lift": pickup_lift,
                                             "drop_location": drop_location,
                                             "drop_address": drop_address,
                                             "drop_floor": drop_floor,
                                             "drop_lift": drop_lift,
                                             "vehicle_name": vehicle_name,
                                             "vehicle_model": vehicle_model,
                                             "vehicle_image": vehicle_image,
                                             "vehicle_amount": vehicle_amount})
                elif warehouse_storing_details_id:
                    ware_house_storing_products = WareHouseStoringProducts.objects \
                        .filter(id=warehouse_storing_products_id) \
                        .first()
                    warehouse_storage_details_id_2 = ware_house_storing_products.warehouse_storage_detail.id
                    if str(warehouse_storage_details_id_2) == warehouse_storing_details_id:
                        summary_address_details = WareHouseStorageDetails.objects.filter(
                            id=warehouse_storing_details_id).first()
                        user_id = summary_address_details.user.id
                        shifting_type = summary_address_details.shifting_type
                        moving_datetime = summary_address_details.moving_datetime
                        pickup_location = summary_address_details.pickup_location
                        pickup_address = summary_address_details.pickup_address
                        pickup_floor = summary_address_details.pickup_floor
                        pickup_lift = summary_address_details.pickup_lift
                        storing_days = summary_address_details.storing_days
                        # warehouse_selected_vehicle = WareHouseSelectedVehicle.objects \
                        #     .filter(warehouse_storage_detail=warehouse_storing_details_id) \
                        #     .first()

                        if ware_house_storing_products.product_amount:
                            product_amount = ware_house_storing_products.product_amount
                        else:
                            product_amount = None

                        if ware_house_storing_products.single_sofa:
                            single_sofa = ware_house_storing_products.single_sofa
                        else:
                            single_sofa = None

                        if ware_house_storing_products.double_sofa:
                            double_sofa = ware_house_storing_products.double_sofa
                        else:
                            double_sofa = None

                        if ware_house_storing_products.three_seater:
                            three_seater = ware_house_storing_products.three_seater
                        else:
                            three_seater = None

                        if ware_house_storing_products.four_seater:
                            four_seater = ware_house_storing_products.four_seater
                        else:
                            four_seater = None

                        if ware_house_storing_products.five_seater:
                            five_seater = ware_house_storing_products.five_seater
                        else:
                            five_seater = None

                        if ware_house_storing_products.six_seater:
                            six_seater = ware_house_storing_products.six_seater
                        else:
                            six_seater = None

                        if ware_house_storing_products.recliner:
                            recliner = ware_house_storing_products.recliner
                        else:
                            recliner = None

                        if ware_house_storing_products.single_bed_storage:
                            single_bed_storage = ware_house_storing_products.single_bed_storage
                        else:
                            single_bed_storage = None

                        if ware_house_storing_products.single_bed_dismantallable:
                            single_bed_dismantallable = ware_house_storing_products.single_bed_dismantallable
                        else:
                            single_bed_dismantallable = None

                        if ware_house_storing_products.double_bed_storage:
                            double_bed_storage = ware_house_storing_products.double_bed_storage
                        else:
                            double_bed_storage = ""

                        if ware_house_storing_products.double_bed_dismantallable:
                            double_bed_dismantallable = ware_house_storing_products.double_bed_dismantallable
                        else:
                            double_bed_dismantallable = None

                        if ware_house_storing_products.bunk_dismantallabel:
                            bunk_dismantallabel = ware_house_storing_products.bunk_dismantallabel
                        else:
                            bunk_dismantallabel = None

                        if ware_house_storing_products.folding_cot_dismantallabel:
                            folding_cot_dismantallabel = ware_house_storing_products.folding_cot_dismantallabel
                        else:
                            folding_cot_dismantallabel = None

                        if ware_house_storing_products.single_mattress_foldable:
                            single_mattress_foldable = ware_house_storing_products.single_mattress_foldable
                        else:
                            single_mattress_foldable = None

                        if ware_house_storing_products.single_mattress_non_foldable:
                            single_mattress_non_foldable = ware_house_storing_products.single_mattress_non_foldable
                        else:
                            single_mattress_non_foldable = None

                        if ware_house_storing_products.double_mattress_foldable:
                            double_mattress_foldable = ware_house_storing_products.double_mattress_foldable
                        else:
                            double_mattress_foldable = None

                        if ware_house_storing_products.double_mattress_nonfoldable:
                            double_mattress_nonfoldable = ware_house_storing_products.double_mattress_nonfoldable
                        else:
                            double_mattress_nonfoldable = None

                        if ware_house_storing_products.dining_table_chairs:
                            dining_table_chairs = ware_house_storing_products.dining_table_chairs
                        else:
                            dining_table_chairs = None

                        if ware_house_storing_products.baby_chairs:
                            baby_chairs = ware_house_storing_products.baby_chairs
                        else:
                            baby_chairs = None

                        if ware_house_storing_products.rocking_chair:
                            rocking_chair = ware_house_storing_products.rocking_chair
                        else:
                            rocking_chair = None

                        if ware_house_storing_products.plastic_floding_chair:
                            plastic_floding_chair = ware_house_storing_products.plastic_floding_chair
                        else:
                            plastic_floding_chair = None

                        if ware_house_storing_products.office_chair:
                            office_chair = ware_house_storing_products.office_chair
                        else:
                            office_chair = None

                        if ware_house_storing_products.bed_side_table:
                            bed_side_table = ware_house_storing_products.bed_side_table
                        else:
                            bed_side_table = None

                        if ware_house_storing_products.dressing_table:
                            dressing_table = ware_house_storing_products.dressing_table
                        else:
                            dressing_table = None

                        if ware_house_storing_products.study_or_computer_table:
                            study_or_computer_table = ware_house_storing_products.study_or_computer_table
                        else:
                            study_or_computer_table = None

                        if ware_house_storing_products.center_table:
                            center_table = ware_house_storing_products.center_table
                        else:
                            center_table = None

                        if ware_house_storing_products.dining_table:
                            dining_table = ware_house_storing_products.dining_table
                        else:
                            dining_table = None

                        if ware_house_storing_products.tea_poy:
                            tea_poy = ware_house_storing_products.tea_poy
                        else:
                            tea_poy = None

                        if ware_house_storing_products.tv_stand:
                            tv_stand = ware_house_storing_products.tv_stand
                        else:
                            tv_stand = None

                        if ware_house_storing_products.book_self:
                            book_self = ware_house_storing_products.book_self
                        else:
                            book_self = None

                        if ware_house_storing_products.mirror:
                            mirror = ware_house_storing_products.mirror
                        else:
                            mirror = None

                        if ware_house_storing_products.shoe_rack:
                            shoe_rack = ware_house_storing_products.shoe_rack
                        else:
                            shoe_rack = None

                        if ware_house_storing_products.mandir:
                            mandir = ware_house_storing_products.mandir
                        else:
                            mandir = None

                        if ware_house_storing_products.iron_trunk_chest:
                            iron_trunk_chest = ware_house_storing_products.iron_trunk_chest
                        else:
                            iron_trunk_chest = None

                        if ware_house_storing_products.tv_size_upto_20:
                            tv_size_upto_20 = ware_house_storing_products.tv_size_upto_20
                        else:
                            tv_size_upto_20 = None

                        if ware_house_storing_products.tv_size_29to43:
                            tv_size_29to43 = ware_house_storing_products.tv_size_29to43
                        else:
                            tv_size_29to43 = None

                        if ware_house_storing_products.tv_size_49to55:
                            tv_size_49to55 = ware_house_storing_products.tv_size_49to55
                        else:
                            tv_size_49to55 = None

                        if ware_house_storing_products.tv_size_above55:
                            tv_size_above55 = ware_house_storing_products.tv_size_above55
                        else:
                            tv_size_above55 = None

                        if ware_house_storing_products.home_theater:
                            home_theater = ware_house_storing_products.home_theater
                        else:
                            home_theater = None

                        if ware_house_storing_products.ac_split:
                            ac_split = ware_house_storing_products.ac_split
                        else:
                            ac_split = None

                        if ware_house_storing_products.ac_window:
                            ac_window = ware_house_storing_products.ac_window
                        else:
                            ac_window = None

                        if ware_house_storing_products.cooler:
                            cooler = ware_house_storing_products.cooler
                        else:
                            cooler = None

                        if ware_house_storing_products.ceiling_fan:
                            ceiling_fan = ware_house_storing_products.ceiling_fan
                        else:
                            ceiling_fan = None

                        if ware_house_storing_products.table_fan:
                            table_fan = ware_house_storing_products.table_fan
                        else:
                            table_fan = None

                        if ware_house_storing_products.exhaust_fan:
                            exhaust_fan = ware_house_storing_products.exhaust_fan
                        else:
                            exhaust_fan = None

                        if ware_house_storing_products.mini_fridge:
                            mini_fridge = ware_house_storing_products.mini_fridge
                        else:
                            mini_fridge = None

                        if ware_house_storing_products.small_fridge:
                            small_fridge = ware_house_storing_products.small_fridge
                        else:
                            small_fridge = None

                        if ware_house_storing_products.medium_fridge:
                            medium_fridge = ware_house_storing_products.medium_fridge
                        else:
                            medium_fridge = None

                        if ware_house_storing_products.large_fridge:
                            large_fridge = ware_house_storing_products.large_fridge
                        else:
                            large_fridge = None

                        if ware_house_storing_products.large_above450_ltrs_fridge:
                            large_above450_ltrs_fridge = ware_house_storing_products.large_above450_ltrs_fridge
                        else:
                            large_above450_ltrs_fridge = None

                        if ware_house_storing_products.washing_machine:
                            washing_machine = ware_house_storing_products.washing_machine
                        else:
                            washing_machine = None

                        if ware_house_storing_products.geyser:
                            geyser = ware_house_storing_products.geyser
                        else:
                            geyser = None

                        if ware_house_storing_products.bath_tub:
                            bath_tub = ware_house_storing_products.bath_tub
                        else:
                            bath_tub = None

                        if ware_house_storing_products.gas_stove:
                            gas_stove = ware_house_storing_products.gas_stove
                        else:
                            gas_stove = None

                        if ware_house_storing_products.water_purifier:
                            water_purifier = ware_house_storing_products.water_purifier
                        else:
                            water_purifier = None

                        if ware_house_storing_products.microwave_otg:
                            microwave_otg = ware_house_storing_products.microwave_otg
                        else:
                            microwave_otg = None

                        if ware_house_storing_products.chimney:
                            chimney = ware_house_storing_products.chimney
                        else:
                            chimney = None

                        if ware_house_storing_products.dish_washer:
                            dish_washer = ware_house_storing_products.dish_washer
                        else:
                            dish_washer = None

                        if ware_house_storing_products.gas_cylinder:
                            gas_cylinder = ware_house_storing_products.gas_cylinder
                        else:
                            gas_cylinder = None

                        if ware_house_storing_products.inverter_ups:
                            inverter_ups = ware_house_storing_products.inverter_ups
                        else:
                            inverter_ups = None

                        if ware_house_storing_products.treadmill:
                            treadmill = ware_house_storing_products.treadmill
                        else:
                            treadmill = None

                        if ware_house_storing_products.piano_guitar:
                            piano_guitar = ware_house_storing_products.piano_guitar
                        else:
                            piano_guitar = None

                        if ware_house_storing_products.sewing_mechine:
                            sewing_mechine = ware_house_storing_products.sewing_mechine
                        else:
                            sewing_mechine = None

                        if ware_house_storing_products.vaccum_cleaner:
                            vaccum_cleaner = ware_house_storing_products.vaccum_cleaner
                        else:
                            vaccum_cleaner = None

                        if ware_house_storing_products.lamp:
                            lamp = ware_house_storing_products.lamp
                        else:
                            lamp = None

                        if ware_house_storing_products.plants:
                            plants = ware_house_storing_products.plants
                        else:
                            plants = None

                        if ware_house_storing_products.iron_board:
                            iron_board = ware_house_storing_products.iron_board
                        else:
                            iron_board = None

                        if ware_house_storing_products.dish_antenna:
                            dish_antenna = ware_house_storing_products.dish_antenna
                        else:
                            dish_antenna = None

                        if ware_house_storing_products.service_carton_box:
                            service_carton_box = ware_house_storing_products.service_carton_box
                        else:
                            service_carton_box = None

                        if ware_house_storing_products.self_carton_box:
                            self_carton_box = ware_house_storing_products.self_carton_box
                        else:
                            self_carton_box = None

                        if ware_house_storing_products.gunny_bags:
                            gunny_bags = ware_house_storing_products.gunny_bags
                        else:
                            gunny_bags = None

                        return JsonResponse({'status_code': 200,
                                             'message': 'User Ware House Storing Products Details',
                                             "user_id": user_id,
                                             "warehouse_storing_details_id": warehouse_storing_details_id,
                                             "warehouse_storing_products_id": warehouse_storing_products_id,
                                             # "warehouse_selected_vehicle_id": warehouse_selected_vehicle.id,
                                             "product_amount":product_amount,
                                             "shifting_type": shifting_type,
                                             "moving_datetime": moving_datetime,
                                             "pickup_location": pickup_location,
                                             "pickup_address": pickup_address,
                                             "pickup_floor": pickup_floor,
                                             "pickup_lift": pickup_lift,
                                             "storing_days": storing_days,

                                             "sofa": {
                                                 "single_sofa": single_sofa,
                                                 "double_sofa": double_sofa,
                                                 "three_seater": three_seater,
                                                 "four_seater": four_seater,
                                                 "five_seater": five_seater,
                                                 "six_seater": six_seater,
                                                 "recliner": recliner
                                             },
                                             "bed": {
                                                 "single_bed_storage": single_bed_storage,
                                                 "single_bed_dismantallable": single_bed_dismantallable,
                                                 "double_bed_storage": double_bed_storage,
                                                 "double_bed_dismantallable": double_bed_dismantallable,
                                                 "bunk_dismantallabel": bunk_dismantallabel,
                                                 "folding_cot_dismantallabel": folding_cot_dismantallabel
                                             },
                                             "mattress": {
                                                 "single_mattress_foldable": single_mattress_foldable,
                                                 "single_mattress_non_foldable": single_mattress_non_foldable,
                                                 "double_mattress_foldable": double_mattress_foldable,
                                                 "double_mattress_nonfoldable": double_mattress_nonfoldable
                                             },
                                             "chairs": {
                                                 "dining_table_chairs": dining_table_chairs,
                                                 "baby_chairs": baby_chairs,
                                                 "rocking_chair": rocking_chair,
                                                 "plastic_floding_chair": plastic_floding_chair,
                                                 "office_chair": office_chair
                                             },
                                             "tables": {
                                                 "bed_side_table": bed_side_table,
                                                 "dressing_table": dressing_table,
                                                 "study_or_computer_table": study_or_computer_table,
                                                 "center_table": center_table,
                                                 "dining_table": dining_table,
                                                 "tea_poy": tea_poy
                                             },
                                             "accessories": {
                                                 "tv_stand": tv_stand,
                                                 "book_self": book_self,
                                                 "mirror": mirror,
                                                 "shoe_rack": shoe_rack,
                                                 "mandir": mandir,
                                                 "iron_trunk_chest": iron_trunk_chest
                                             },
                                             "tv": {
                                                 "tv_size_upto_20": tv_size_upto_20,
                                                 "tv_size_29to43": tv_size_29to43,
                                                 "tv_size_49to55": tv_size_49to55,
                                                 "tv_size_above55": tv_size_above55,
                                                 "home_theater": home_theater
                                             },
                                             "ac": {
                                                 "ac_split": ac_split,
                                                 "ac_window": ac_window,
                                                 "cooler": cooler,
                                                 "ceiling_fan": ceiling_fan,
                                                 "table_fan": table_fan,
                                                 "exhaust_fan": exhaust_fan
                                             },
                                             "fridge": {
                                                 "mini_fridge": mini_fridge,
                                                 "small_fridge": small_fridge,
                                                 "medium_fridge": medium_fridge,
                                                 "large_fridge": large_fridge,
                                                 "large_above450_ltrs_fridge": large_above450_ltrs_fridge
                                             },
                                             "bathroom": {
                                                 "washing_machine": washing_machine,
                                                 "geyser": geyser,
                                                 "bath_tub": bath_tub
                                             },
                                             "kitchen_utility": {
                                                 "gas_stove": gas_stove,
                                                 "water_purifier": water_purifier,
                                                 "microwave_otg": microwave_otg,
                                                 "chimney": chimney,
                                                 "dish_washer": dish_washer,
                                                 "gas_cylinder": gas_cylinder
                                             },
                                             "others": {
                                                 "inverter_ups": inverter_ups,
                                                 "treadmill": treadmill,
                                                 "piano_guitar": piano_guitar
                                             },
                                             "home_utility": {
                                                 "sewing_mechine": sewing_mechine,
                                                 "vaccum_cleaner": vaccum_cleaner,
                                                 "lamp": lamp,
                                                 "plants": plants,
                                                 "iron_board": iron_board,
                                                 "dish_antenna": dish_antenna
                                             },
                                             "cartons": {
                                                 "service_carton_box": service_carton_box,
                                                 "self_carton_box": self_carton_box
                                             },
                                             "gunny_bags": {
                                                 "gunny_bags": gunny_bags
                                             }

                                             })
        else:
            return JsonResponse({'status_code': 407, 'message': 'Need to enter the proper authentication SECRET KEY'})
    return JsonResponse({"message": "User Booking Details ID"})


@csrf_exempt
def house_shifting_details(request):
    if request.method == "POST":
        if request.body:
            now = timezone.localtime(timezone.now())
            request_data = json.loads(request.body)
            try:
                user_id = request_data["user_id"]
            except:
                user_id = ''

            user = User.objects.filter(id=user_id).first()

            try:
                house_shifting_type = request_data["house_shifting_type"]
            except:
                house_shifting_type = ""
            try:
                shifting_type = request_data["shifting_type"]
            except:
                shifting_type = ''

            if shifting_type == '1':
                shifting_type = "House Shifting"

            try:
                moving_datetime = request_data["moving_datetime"]
            except:
                moving_datetime = ''

            if moving_datetime == '':
                moving_datetime = None

            if moving_datetime:
                date_string = moving_datetime
                date_format = "%d/%m/%Y %H:%M"

                datetime_obj = datetime.strptime(date_string, date_format)
                moving_formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                moving_formatted_date = ""

            try:
                pickup_location = request_data["pickup_location"]
            except:
                pickup_location = ''

            if pickup_location is None:
                pickup_location = None

            try:
                pickup_address = request_data["pickup_address"]
            except:
                pickup_address = ''

            if pickup_address is None:
                pickup_address = None

            try:
                pickup_floor = request_data["pickup_floor"]
            except:
                pickup_floor = ""

            if pickup_floor is None:
                pickup_floor = None

            try:
                pickup_lift = request_data["pickup_lift"]
            except:
                pickup_lift = ""

            if pickup_lift is None:
                pickup_lift = None

            try:
                drop_location = request_data["drop_location"]
            except:
                drop_location = ""

            if drop_location is None:
                drop_location = None

            try:
                drop_address = request_data["drop_address"]
            except:
                drop_address = ""

            if drop_address is None:
                drop_address = None

            try:
                drop_floor = request_data["drop_floor"]
            except:
                drop_floor = ""

            if drop_floor is None:
                drop_floor = None

            try:
                drop_lift = request_data["drop_lift"]
            except:
                drop_lift = ""

            if drop_lift is None:
                drop_lift = None

            try:
                order_placed_datetime = now
            except:
                order_placed_datetime = ''

            if order_placed_datetime is None:
                order_placed_datetime = None

            house_shifting_details = HouseShiftingDetails(user=user,
                                                          house_shifting_type=house_shifting_type,
                                                          shifting_type=shifting_type,
                                                          moving_datetime=moving_formatted_date,
                                                          pickup_location=pickup_location,
                                                          pickup_address=pickup_address,
                                                          pickup_floor=pickup_floor,
                                                          pickup_lift=pickup_lift,
                                                          drop_location=drop_location,
                                                          drop_address=drop_address,
                                                          drop_floor=drop_floor,
                                                          drop_lift=drop_lift,
                                                          order_placed_datetime=order_placed_datetime,
                                                          created=now,
                                                          updated=now)
            house_shifting_details.save()

            return JsonResponse({'status_code': 200, 'message': 'User House Shifting Details Saved',
                                 "house_shifting_details_id": house_shifting_details.id})

        else:
            return JsonResponse({'status_code': 400, 'message': 'Need to fill the Home Shifting Details properly'})

    return JsonResponse({'message': 'House Shifting Details Page'})


# @csrf_exempt
# def house_shifting_selected_vehicle(request):
#     if request.method == "POST":
#         now = timezone.localtime(timezone.now())
#         request_data = json.loads(request.body)
#         house_shifting_details_id = request_data["house_shifting_details_id"]
#         house_shifting_details = HouseShiftingDetails.objects.filter(id=house_shifting_details_id).first()
#         try:
#             vehicle_name = request_data["vehicle_name"]
#         except:
#             vehicle_name = ""
#
#         try:
#             vehicle_type = request_data["vehicle_type"]
#         except:
#             vehicle_type = ""
#
#         try:
#             vehicle_image = request_data["vehicle_image"]
#         except:
#             vehicle_image = ""
#
#         try:
#             vehicle_amount = request_data["vehicle_amount"]
#         except:
#             vehicle_amount = ""
#
#         try:
#             total_shifting_KMs = request_data["total_shifting_KMs"]
#         except:
#             total_shifting_KMs = ""
#
#         if house_shifting_details:
#             house_shifting_selected_vehicle = HouseShiftingSelectedVehicle(house_shifting_details=house_shifting_details,
#                                                                            vehicle_name=vehicle_name,
#                                                                            vehicle_type=vehicle_type,
#                                                                            vehicle_image=vehicle_image,
#                                                                            vehicle_amount=vehicle_amount,
#                                                                            total_shifting_KMs=total_shifting_KMs,
#                                                                            created=now,
#                                                                            updated=now)
#             house_shifting_selected_vehicle.save()
#
#             return JsonResponse({'status_code': 200, "message": "House Shifting Selected Vehicle",
#                                  "house_shifting_details_id": house_shifting_details.id})


@csrf_exempt
def house_shifting_products(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        house_shifting_details_id = request_data["house_shifting_details_id"]
        product_amount = request_data["product_amount"]
        house_shifting_instance = HouseShiftingDetails.objects.filter(id=house_shifting_details_id).first()
        if request_data["sofa"]:
            requested_sofa = request_data["sofa"]
            single_sofa = requested_sofa["single_sofa"]
            double_sofa = requested_sofa["double_sofa"]
            three_seater = requested_sofa["three_seater"]
            four_seater = requested_sofa["four_seater"]
            five_seater = requested_sofa["five_seater"]
            six_seater = requested_sofa["six_seater"]
            recliner = requested_sofa["recliner"]

        if request_data["bed"]:
            request_bed = request_data["bed"]
            single_bed_storage = request_bed["single_bed_storage"]
            single_bed_dismantallable = request_bed["single_bed_dismantallable"]
            double_bed_storage = request_bed["double_bed_storage"]
            double_bed_dismantallable = request_bed["double_bed_dismantallable"]
            bunk_dismantallabel = request_bed["bunk_dismantallabel"]
            folding_cot_dismantallabel = request_bed["folding_cot_dismantallabel"]

        if request_data["mattress"]:
            request_mattress = request_data["mattress"]
            single_mattress_foldable = request_mattress["single_mattress_foldable"]
            single_mattress_non_foldable = request_mattress["single_mattress_non_foldable"]
            double_mattress_foldable = request_mattress["double_mattress_foldable"]
            double_mattress_nonfoldable = request_mattress["double_mattress_nonfoldable"]

        if request_data["chairs"]:
            request_chairs = request_data["chairs"]
            dining_table_chairs = request_chairs["dining_table_chairs"]
            baby_chairs = request_chairs["baby_chairs"]
            rocking_chair = request_chairs["rocking_chair"]
            plastic_floding_chair = request_chairs["plastic_floding_chair"]
            office_chair = request_chairs["office_chair"]

        if request_data["tables"]:
            request_tables = request_data["tables"]
            bed_side_table = request_tables["bed_side_table"]
            dressing_table = request_tables["dressing_table"]
            study_or_computer_table = request_tables["study_or_computer_table"]
            center_table = request_tables["center_table"]
            dining_table = request_tables["dining_table"]
            tea_poy = request_tables["tea_poy"]

        if request_data["accessories"]:
            request_accessories = request_data["accessories"]
            tv_stand = request_accessories["tv_stand"]
            book_self = request_accessories["book_self"]
            mirror = request_accessories["mirror"]
            shoe_rack = request_accessories["shoe_rack"]
            mandir = request_accessories["mandir"]
            iron_trunk_chest = request_accessories["iron_trunk_chest"]

        if request_data["tv"]:
            request_tv = request_data["tv"]
            tv_size_upto_20 = request_tv["tv_size_upto_20"]
            tv_size_29to43 = request_tv["tv_size_29to43"]
            tv_size_49to55 = request_tv["tv_size_49to55"]
            tv_size_above55 = request_tv["tv_size_above55"]
            home_theater = request_tv["home_theater"]

        if request_data["ac"]:
            request_ac = request_data["ac"]
            ac_split = request_ac["ac_split"]
            ac_window = request_ac["ac_window"]
            cooler = request_ac["cooler"]
            ceiling_fan = request_ac["ceiling_fan"]
            table_fan = request_ac["table_fan"]
            exhaust_fan = request_ac["exhaust_fan"]

        if request_data["fridge"]:
            request_fridge = request_data["fridge"]
            mini_fridge = request_fridge["mini_fridge"]
            small_fridge = request_fridge["small_fridge"]
            medium_fridge = request_fridge["medium_fridge"]
            large_fridge = request_fridge["large_fridge"]
            large_above450_ltrs_fridge = request_fridge["large_above450_ltrs_fridge"]

        if request_data["bathroom"]:
            request_bathroom = request_data["bathroom"]
            washing_machine = request_bathroom["washing_machine"]
            geyser = request_bathroom["geyser"]
            bath_tub = request_bathroom["bath_tub"]

        if request_data["kitchen_utility"]:
            request_kitchen_utility = request_data["kitchen_utility"]
            gas_stove = request_kitchen_utility["gas_stove"]
            water_purifier = request_kitchen_utility["water_purifier"]
            microwave_otg = request_kitchen_utility["microwave_otg"]
            chimney = request_kitchen_utility["chimney"]
            dish_washer = request_kitchen_utility["dish_washer"]
            gas_cylinder = request_kitchen_utility["gas_cylinder"]

        if request_data["home_utility"]:
            request_home_utility = request_data["home_utility"]
            sewing_mechine = request_home_utility["sewing_mechine"]
            vaccum_cleaner = request_home_utility["vaccum_cleaner"]
            lamp = request_home_utility["lamp"]
            plants = request_home_utility["plants"]
            iron_board = request_home_utility["iron_board"]
            dish_antenna = request_home_utility["dish_antenna"]

        if request_data["others"]:
            request_others = request_data["others"]
            inverter_ups = request_others["inverter_ups"]
            treadmill = request_others["treadmill"]
            piano_guitar = request_others["piano_guitar"]

        if request_data["cartons"]:
            request_cartons = request_data["cartons"]
            service_carton_box = request_cartons["service_carton_box"]
            self_carton_box = request_cartons["self_carton_box"]

        if request_data["gunny_bags"]:
            request_gunny_bags = request_data["gunny_bags"]
            gunny_bags = request_gunny_bags["gunny_bags"]

        now = timezone.localtime(timezone.now())
        if house_shifting_instance is not None:
            house_shifting_products = HouseShiftingProducts(house_shifting_details=house_shifting_instance,
                                                            product_amount=product_amount,
                                                            single_sofa=single_sofa,
                                                            double_sofa=double_sofa,
                                                            three_seater=three_seater,
                                                            four_seater=four_seater,
                                                            five_seater=five_seater,
                                                            six_seater=six_seater,
                                                            recliner=recliner,
                                                            single_bed_storage=single_bed_storage,
                                                            single_bed_dismantallable=single_bed_dismantallable,
                                                            double_bed_storage=double_bed_storage,
                                                            double_bed_dismantallable=double_bed_dismantallable,
                                                            bunk_dismantallabel=bunk_dismantallabel,
                                                            folding_cot_dismantallabel=folding_cot_dismantallabel,
                                                            single_mattress_foldable=single_mattress_foldable,
                                                            single_mattress_non_foldable=single_mattress_non_foldable,
                                                            double_mattress_foldable=double_mattress_foldable,
                                                            double_mattress_nonfoldable=double_mattress_nonfoldable,
                                                            dining_table_chairs=dining_table_chairs,
                                                            baby_chairs=baby_chairs,
                                                            rocking_chair=rocking_chair,
                                                            plastic_floding_chair=plastic_floding_chair,
                                                            office_chair=office_chair,
                                                            bed_side_table=bed_side_table,
                                                            dressing_table=dressing_table,
                                                            study_or_computer_table=study_or_computer_table,
                                                            center_table=center_table,
                                                            dining_table=dining_table,
                                                            tea_poy=tea_poy,
                                                            tv_stand=tv_stand,
                                                            book_self=book_self,
                                                            mirror=mirror,
                                                            shoe_rack=shoe_rack,
                                                            mandir=mandir,
                                                            iron_trunk_chest=iron_trunk_chest,
                                                            tv_size_upto_20=tv_size_upto_20,
                                                            tv_size_29to43=tv_size_29to43,
                                                            tv_size_49to55=tv_size_49to55,
                                                            tv_size_above55=tv_size_above55,
                                                            home_theater=home_theater,
                                                            ac_split=ac_split,
                                                            ac_window=ac_window,
                                                            cooler=cooler,
                                                            ceiling_fan=ceiling_fan,
                                                            table_fan=table_fan,
                                                            exhaust_fan=exhaust_fan,
                                                            mini_fridge=mini_fridge,
                                                            small_fridge=small_fridge,
                                                            medium_fridge=medium_fridge,
                                                            large_fridge=large_fridge,
                                                            large_above450_ltrs_fridge=large_above450_ltrs_fridge,
                                                            washing_machine=washing_machine,
                                                            geyser=geyser,
                                                            bath_tub=bath_tub,
                                                            gas_stove=gas_stove,
                                                            water_purifier=water_purifier,
                                                            microwave_otg=microwave_otg,
                                                            chimney=chimney,
                                                            dish_washer=dish_washer,
                                                            gas_cylinder=gas_cylinder,
                                                            sewing_mechine=sewing_mechine,
                                                            vaccum_cleaner=vaccum_cleaner,
                                                            lamp=lamp,
                                                            plants=plants,
                                                            iron_board=iron_board,
                                                            dish_antenna=dish_antenna,
                                                            inverter_ups=inverter_ups,
                                                            treadmill=treadmill,
                                                            piano_guitar=piano_guitar,
                                                            service_carton_box=service_carton_box,
                                                            self_carton_box=self_carton_box,
                                                            gunny_bags=gunny_bags,
                                                            created=now,
                                                            updated=now)
            house_shifting_products.save()

            return JsonResponse({'status_code': 200,
                                 'message': 'User House Shifting Details Saved',
                                 "house_shifting_product_id": house_shifting_products.id,
                                 "house_shifting_details_id": house_shifting_instance.id})


@csrf_exempt
def house_shifting_summary_details(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>")
        house_shifting_details_id = request_data["house_shifting_details_id"]
        print("house_shifting_details_id",house_shifting_details_id)
        house_shifting_product_id = request_data["house_shifting_product_id"]
        print("house_shifting_product_id",house_shifting_product_id)
        house_shifting_products_id = HouseShiftingProducts.objects.filter(id=house_shifting_product_id).first()
        house_shifting_details_id_2 = house_shifting_products_id.house_shifting_details.id
        if str(house_shifting_details_id_2) == house_shifting_details_id:
            house_shifting_products = HouseShiftingProducts.objects.filter(id=house_shifting_product_id).first()
            house_shifting_details_id_3 = house_shifting_products_id.house_shifting_details.id
            summary_address_details = HouseShiftingDetails.objects.filter(id=house_shifting_details_id_3).first()
            user_id = summary_address_details.user.id
            shifting_type = summary_address_details.shifting_type
            moving_datetime = summary_address_details.moving_datetime
            pickup_location = summary_address_details.pickup_location
            pickup_address = summary_address_details.pickup_address
            pickup_floor = summary_address_details.pickup_floor
            pickup_lift = summary_address_details.pickup_lift
            drop_location = summary_address_details.drop_location
            drop_address = summary_address_details.drop_address
            drop_floor = summary_address_details.drop_floor
            drop_lift = summary_address_details.drop_lift

            # house_shifting_selected_vehicle = HouseShiftingSelectedVehicle.objects \
            #     .filter(house_shifting_details=house_shifting_details_id) \
            #     .first()
            if house_shifting_products.product_amount:
                product_amount = house_shifting_products.product_amount
            else:
                product_amount = None

            # if house_shifting_selected_vehicle.vehicle_amount:
            #     vehicle_amount = house_shifting_selected_vehicle.product_amount
            # else:
            #     vehicle_amount = None
            #
            # if house_shifting_selected_vehicle.total_shifting_KMs:
            #     total_shifting_KMs = house_shifting_selected_vehicle.total_shifting_KMs
            # else:
            #     total_shifting_KMs = None

            if house_shifting_products.single_sofa:
                single_sofa = house_shifting_products.single_sofa
            else:
                single_sofa = None

            if house_shifting_products.double_sofa:
                double_sofa = house_shifting_products.double_sofa
            else:
                double_sofa = None

            if house_shifting_products.three_seater:
                three_seater = house_shifting_products.three_seater
            else:
                three_seater = None

            if house_shifting_products.four_seater:
                four_seater = house_shifting_products.four_seater
            else:
                four_seater = None

            if house_shifting_products.five_seater:
                five_seater = house_shifting_products.five_seater
            else:
                five_seater = None

            if house_shifting_products.six_seater:
                six_seater = house_shifting_products.six_seater
            else:
                six_seater = None

            if house_shifting_products.recliner:
                recliner = house_shifting_products.recliner
            else:
                recliner = None

            if house_shifting_products.single_bed_storage:
                single_bed_storage = house_shifting_products.single_bed_storage
            else:
                single_bed_storage = None

            if house_shifting_products.single_bed_dismantallable:
                single_bed_dismantallable = house_shifting_products.single_bed_dismantallable
            else:
                single_bed_dismantallable = None

            if house_shifting_products.double_bed_storage:
                double_bed_storage = house_shifting_products.double_bed_storage
            else:
                double_bed_storage = ""

            if house_shifting_products.double_bed_dismantallable:
                double_bed_dismantallable = house_shifting_products.double_bed_dismantallable
            else:
                double_bed_dismantallable = None

            if house_shifting_products.bunk_dismantallabel:
                bunk_dismantallabel = house_shifting_products.bunk_dismantallabel
            else:
                bunk_dismantallabel = None

            if house_shifting_products.folding_cot_dismantallabel:
                folding_cot_dismantallabel = house_shifting_products.folding_cot_dismantallabel
            else:
                folding_cot_dismantallabel = None

            if house_shifting_products.single_mattress_foldable:
                single_mattress_foldable = house_shifting_products.single_mattress_foldable
            else:
                single_mattress_foldable = None

            if house_shifting_products.single_mattress_non_foldable:
                single_mattress_non_foldable = house_shifting_products.single_mattress_non_foldable
            else:
                single_mattress_non_foldable = None

            if house_shifting_products.double_mattress_foldable:
                double_mattress_foldable = house_shifting_products.double_mattress_foldable
            else:
                double_mattress_foldable = None

            if house_shifting_products.double_mattress_nonfoldable:
                double_mattress_nonfoldable = house_shifting_products.double_mattress_nonfoldable
            else:
                double_mattress_nonfoldable = None

            if house_shifting_products.dining_table_chairs:
                dining_table_chairs = house_shifting_products.dining_table_chairs
            else:
                dining_table_chairs = None

            if house_shifting_products.baby_chairs:
                baby_chairs = house_shifting_products.baby_chairs
            else:
                baby_chairs = None

            if house_shifting_products.rocking_chair:
                rocking_chair = house_shifting_products.rocking_chair
            else:
                rocking_chair = None

            if house_shifting_products.plastic_floding_chair:
                plastic_floding_chair = house_shifting_products.plastic_floding_chair
            else:
                plastic_floding_chair = None

            if house_shifting_products.office_chair:
                office_chair = house_shifting_products.office_chair
            else:
                office_chair = None

            if house_shifting_products.bed_side_table:
                bed_side_table = house_shifting_products.bed_side_table
            else:
                bed_side_table = None

            if house_shifting_products.dressing_table:
                dressing_table = house_shifting_products.dressing_table
            else:
                dressing_table = None

            if house_shifting_products.study_or_computer_table:
                study_or_computer_table = house_shifting_products.study_or_computer_table
            else:
                study_or_computer_table = None

            if house_shifting_products.center_table:
                center_table = house_shifting_products.center_table
            else:
                center_table = None

            if house_shifting_products.dining_table:
                dining_table = house_shifting_products.dining_table
            else:
                dining_table = None

            if house_shifting_products.tea_poy:
                tea_poy = house_shifting_products.tea_poy
            else:
                tea_poy = None

            if house_shifting_products.tv_stand:
                tv_stand = house_shifting_products.tv_stand
            else:
                tv_stand = None

            if house_shifting_products.book_self:
                book_self = house_shifting_products.book_self
            else:
                book_self = None

            if house_shifting_products.mirror:
                mirror = house_shifting_products.mirror
            else:
                mirror = None

            if house_shifting_products.shoe_rack:
                shoe_rack = house_shifting_products.shoe_rack
            else:
                shoe_rack = None

            if house_shifting_products.mandir:
                mandir = house_shifting_products.mandir
            else:
                mandir = None

            if house_shifting_products.iron_trunk_chest:
                iron_trunk_chest = house_shifting_products.iron_trunk_chest
            else:
                iron_trunk_chest = None

            if house_shifting_products.tv_size_upto_20:
                tv_size_upto_20 = house_shifting_products.tv_size_upto_20
            else:
                tv_size_upto_20 = None

            if house_shifting_products.tv_size_29to43:
                tv_size_29to43 = house_shifting_products.tv_size_29to43
            else:
                tv_size_29to43 = None

            if house_shifting_products.tv_size_49to55:
                tv_size_49to55 = house_shifting_products.tv_size_49to55
            else:
                tv_size_49to55 = None

            if house_shifting_products.tv_size_above55:
                tv_size_above55 = house_shifting_products.tv_size_above55
            else:
                tv_size_above55 = None

            if house_shifting_products.home_theater:
                home_theater = house_shifting_products.home_theater
            else:
                home_theater = None

            if house_shifting_products.ac_split:
                ac_split = house_shifting_products.ac_split
            else:
                ac_split = None

            if house_shifting_products.ac_window:
                ac_window = house_shifting_products.ac_window
            else:
                ac_window = None

            if house_shifting_products.cooler:
                cooler = house_shifting_products.cooler
            else:
                cooler = None

            if house_shifting_products.ceiling_fan:
                ceiling_fan = house_shifting_products.ceiling_fan
            else:
                ceiling_fan = None

            if house_shifting_products.table_fan:
                table_fan = house_shifting_products.table_fan
            else:
                table_fan = None

            if house_shifting_products.exhaust_fan:
                exhaust_fan = house_shifting_products.exhaust_fan
            else:
                exhaust_fan = None

            if house_shifting_products.mini_fridge:
                mini_fridge = house_shifting_products.mini_fridge
            else:
                mini_fridge = None

            if house_shifting_products.small_fridge:
                small_fridge = house_shifting_products.small_fridge
            else:
                small_fridge = None

            if house_shifting_products.medium_fridge:
                medium_fridge = house_shifting_products.medium_fridge
            else:
                medium_fridge = None

            if house_shifting_products.large_fridge:
                large_fridge = house_shifting_products.large_fridge
            else:
                large_fridge = None

            if house_shifting_products.large_above450_ltrs_fridge:
                large_above450_ltrs_fridge = house_shifting_products.large_above450_ltrs_fridge
            else:
                large_above450_ltrs_fridge = None

            if house_shifting_products.washing_machine:
                washing_machine = house_shifting_products.washing_machine
            else:
                washing_machine = None

            if house_shifting_products.geyser:
                geyser = house_shifting_products.geyser
            else:
                geyser = None

            if house_shifting_products.bath_tub:
                bath_tub = house_shifting_products.bath_tub
            else:
                bath_tub = None

            if house_shifting_products.gas_stove:
                gas_stove = house_shifting_products.gas_stove
            else:
                gas_stove = None

            if house_shifting_products.water_purifier:
                water_purifier = house_shifting_products.water_purifier
            else:
                water_purifier = None

            if house_shifting_products.microwave_otg:
                microwave_otg = house_shifting_products.microwave_otg
            else:
                microwave_otg = None

            if house_shifting_products.chimney:
                chimney = house_shifting_products.chimney
            else:
                chimney = None

            if house_shifting_products.dish_washer:
                dish_washer = house_shifting_products.dish_washer
            else:
                dish_washer = None

            if house_shifting_products.gas_cylinder:
                gas_cylinder = house_shifting_products.gas_cylinder
            else:
                gas_cylinder = None

            if house_shifting_products.inverter_ups:
                inverter_ups = house_shifting_products.inverter_ups
            else:
                inverter_ups = None

            if house_shifting_products.treadmill:
                treadmill = house_shifting_products.treadmill
            else:
                treadmill = None

            if house_shifting_products.piano_guitar:
                piano_guitar = house_shifting_products.piano_guitar
            else:
                piano_guitar = None

            if house_shifting_products.sewing_mechine:
                sewing_mechine = house_shifting_products.sewing_mechine
            else:
                sewing_mechine = None

            if house_shifting_products.vaccum_cleaner:
                vaccum_cleaner = house_shifting_products.vaccum_cleaner
            else:
                vaccum_cleaner = None

            if house_shifting_products.lamp:
                lamp = house_shifting_products.lamp
            else:
                lamp = None

            if house_shifting_products.plants:
                plants = house_shifting_products.plants
            else:
                plants = None

            if house_shifting_products.iron_board:
                iron_board = house_shifting_products.iron_board
            else:
                iron_board = None

            if house_shifting_products.dish_antenna:
                dish_antenna = house_shifting_products.dish_antenna
            else:
                dish_antenna = None

            if house_shifting_products.service_carton_box:
                service_carton_box = house_shifting_products.service_carton_box
            else:
                service_carton_box = None

            if house_shifting_products.self_carton_box:
                self_carton_box = house_shifting_products.self_carton_box
            else:
                self_carton_box = None

            if house_shifting_products.gunny_bags:
                gunny_bags = house_shifting_products.gunny_bags
            else:
                gunny_bags = None

            return JsonResponse({'status_code': 200,
                                 'message': 'User House Shifting Details',
                                 "user_id": user_id,
                                 "product_amount": product_amount,
                                 # "vehicle_amount": vehicle_amount,
                                 # "total_shifting_KMs": total_shifting_KMs,
                                 "house_shifting_details_id": house_shifting_details_id,
                                 "house_shifting_product_id": house_shifting_product_id,
                                 # "house_shifting_selected_vehicle_id": house_shifting_selected_vehicle.id,
                                 "shifting_type": shifting_type,
                                 "moving_datetime": moving_datetime,
                                 "pickup_location": pickup_location,
                                 "pickup_address": pickup_address,
                                 "pickup_floor": pickup_floor,
                                 "pickup_lift": pickup_lift,
                                 "drop_location": drop_location,
                                 "drop_address": drop_address,
                                 "drop_floor": drop_floor,
                                 "drop_lift": drop_lift,

                                 "sofa": {
                                     "single_sofa": single_sofa,
                                     "double_sofa": double_sofa,
                                     "three_seater": three_seater,
                                     "four_seater": four_seater,
                                     "five_seater": five_seater,
                                     "six_seater": six_seater,
                                     "recliner": recliner
                                 },
                                 "bed": {
                                     "single_bed_storage": single_bed_storage,
                                     "single_bed_dismantallable": single_bed_dismantallable,
                                     "double_bed_storage": double_bed_storage,
                                     "double_bed_dismantallable": double_bed_dismantallable,
                                     "bunk_dismantallabel": bunk_dismantallabel,
                                     "folding_cot_dismantallabel": folding_cot_dismantallabel
                                 },
                                 "mattress": {
                                     "single_mattress_foldable": single_mattress_foldable,
                                     "single_mattress_non_foldable": single_mattress_non_foldable,
                                     "double_mattress_foldable": double_mattress_foldable,
                                     "double_mattress_nonfoldable": double_mattress_nonfoldable
                                 },
                                 "chairs": {
                                     "dining_table_chairs": dining_table_chairs,
                                     "baby_chairs": baby_chairs,
                                     "rocking_chair": rocking_chair,
                                     "plastic_floding_chair": plastic_floding_chair,
                                     "office_chair": office_chair
                                 },
                                 "tables": {
                                     "bed_side_table": bed_side_table,
                                     "dressing_table": dressing_table,
                                     "study_or_computer_table": study_or_computer_table,
                                     "center_table": center_table,
                                     "dining_table": dining_table,
                                     "tea_poy": tea_poy
                                 },
                                 "accessories": {
                                     "tv_stand": tv_stand,
                                     "book_self": book_self,
                                     "mirror": mirror,
                                     "shoe_rack": shoe_rack,
                                     "mandir": mandir,
                                     "iron_trunk_chest": iron_trunk_chest
                                 },
                                 "tv": {
                                     "tv_size_upto_20": tv_size_upto_20,
                                     "tv_size_29to43": tv_size_29to43,
                                     "tv_size_49to55": tv_size_49to55,
                                     "tv_size_above55": tv_size_above55,
                                     "home_theater": home_theater
                                 },
                                 "ac": {
                                     "ac_split": ac_split,
                                     "ac_window": ac_window,
                                     "cooler": cooler,
                                     "ceiling_fan": ceiling_fan,
                                     "table_fan": table_fan,
                                     "exhaust_fan": exhaust_fan
                                 },
                                 "fridge": {
                                     "mini_fridge": mini_fridge,
                                     "small_fridge": small_fridge,
                                     "medium_fridge": medium_fridge,
                                     "large_fridge": large_fridge,
                                     "large_above450_ltrs_fridge": large_above450_ltrs_fridge
                                 },
                                 "bathroom": {
                                     "washing_machine": washing_machine,
                                     "geyser": geyser,
                                     "bath_tub": bath_tub
                                 },
                                 "kitchen_utility": {
                                     "gas_stove": gas_stove,
                                     "water_purifier": water_purifier,
                                     "microwave_otg": microwave_otg,
                                     "chimney": chimney,
                                     "dish_washer": dish_washer,
                                     "gas_cylinder": gas_cylinder
                                 },
                                 "others": {
                                     "inverter_ups": inverter_ups,
                                     "treadmill": treadmill,
                                     "piano_guitar": piano_guitar
                                 },
                                 "home_utility": {
                                     "sewing_mechine": sewing_mechine,
                                     "vaccum_cleaner": vaccum_cleaner,
                                     "lamp": lamp,
                                     "plants": plants,
                                     "iron_board": iron_board,
                                     "dish_antenna": dish_antenna
                                 },
                                 "cartons": {
                                     "service_carton_box": service_carton_box,
                                     "self_carton_box": self_carton_box
                                 },
                                 "gunny_bags": {
                                     "gunny_bags": gunny_bags
                                 }

                                 })
        else:
            return JsonResponse({'status_code': 200, "message": "House Shifting Details id is None"})

    return JsonResponse({'status_code': 200, "message": "House Shifting Details PAGE"})

@csrf_exempt
def vehicle_shifting_details(request):
    if request.method == "POST":
        if request.body:
            now = timezone.localtime(timezone.now())
            request_data = json.loads(request.body)
            try:
                user_id = request_data["user_id"]
            except:
                user_id = ''

            user = User.objects.filter(id=user_id).first()

            try:
                shifting_type = request_data["shifting_type"]
            except:
                shifting_type = ''

            if shifting_type == '2':
                shifting_type = "Vehicle Shifting"
            else:
                shifting_type = "None"

            try:
                moving_datetime = request_data["moving_datetime"]
            except:
                moving_datetime = ''

            if moving_datetime == '':
                moving_datetime = None
            if moving_datetime:
                date_string = moving_datetime
                date_format = "%d/%m/%Y %H:%M"

                datetime_obj = datetime.strptime(date_string, date_format)
                moving_formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                moving_formatted_date = ""

            try:
                pickup_location = request_data["pickup_location"]
            except:
                pickup_location = ''

            if pickup_location == '':
                pickup_location = "None"

            try:
                pickup_address = request_data["pickup_address"]
            except:
                pickup_address = ''

            try:
                pickup_floor = request_data["pickup_floor"]
            except:
                pickup_floor = ""

            try:
                pickup_lift = request_data["pickup_lift"]
            except:
                pickup_lift = ""

            try:
                drop_location = request_data["drop_location"]
            except:
                drop_location = ""

            try:
                drop_address = request_data["drop_address"]
            except:
                drop_address = ""

            try:
                drop_floor = request_data["drop_floor"]
            except:
                drop_floor = ""

            try:
                drop_lift = request_data["drop_lift"]
            except:
                drop_lift = ""

            try:
                order_place_datetime = now
            except:
                order_place_datetime = ''

            if user is not None:
                vehicle_shifting_detail = VehicleShiftingDetails(user=user,
                                                                 shifting_type=shifting_type,
                                                                 pickup_location=pickup_location,
                                                                 moving_datetime=moving_formatted_date,
                                                                 pickup_address=pickup_address,
                                                                 pickup_floor=pickup_floor,
                                                                 pickup_lift=pickup_lift,
                                                                 drop_location=drop_location,
                                                                 drop_address=drop_address,
                                                                 drop_floor=drop_floor,
                                                                 drop_lift=drop_lift,
                                                                 order_place_datetime=order_place_datetime,
                                                                 created=now,
                                                                 updated=now)
                vehicle_shifting_detail.save()

                return JsonResponse({'status_code': 200, 'message': 'User Vehicle Shifting Details Saved',
                                     "vehicle_shifting_details_id": vehicle_shifting_detail.id})

        else:
            return JsonResponse({'status_code': 400, 'message': 'Need to fill the Vehicle Shifting Details properly'})

    return JsonResponse({'message': 'Vehicle Shifting Details Page'})


@csrf_exempt
def chosen_shifting_vehicle(request):
    if request.method == "POST":
        if request.body:
            now = timezone.localtime(timezone.now())
            request_data = json.loads(request.body)

            try:
                vehicle_shifting_details_id = request_data["vehicle_shifting_details_id"]
            except:
                vehicle_shifting_details_id = ""

            if vehicle_shifting_details_id:
                vehicle_shifting_detail_id = VehicleShiftingDetails.objects.filter(
                    id=vehicle_shifting_details_id).first()
            else:
                vehicle_shifting_detail_id = ""

            try:
                vehicle_name = request_data["vehicle_name"]
            except:
                vehicle_name = ""

            try:
                vehicle_model = request_data["vehicle_model"]
            except:
                vehicle_model = ""

            try:
                vehicle_image = request_data["vehicle_image"]
            except:
                vehicle_image = ""

            try:
                vehicle_amount = request_data["vehicle_amount"]
            except:
                vehicle_amount = ""
            try:
                order_place_datetime = now
            except:
                order_place_datetime = ""

            if vehicle_shifting_details_id is not None:
                chosen_shifting_vehicle = ChosenShiftingVehicle(vehicle_shifting_details=vehicle_shifting_detail_id,
                                                                vehicle_name=vehicle_name,
                                                                vehicle_model=vehicle_model,
                                                                vehicle_image=vehicle_image,
                                                                vehicle_amount=vehicle_amount,
                                                                order_place_datetime=order_place_datetime,
                                                                created=now,
                                                                updated=now)
                chosen_shifting_vehicle.save()
                return JsonResponse({"status_code": 200,
                                     "message": "User Vehicle Shifting Details Saved",
                                     "chosen_shifting_vehicle_id": chosen_shifting_vehicle.id,
                                     "vehicle_shifting_details_id": vehicle_shifting_detail_id.id})


@csrf_exempt
def vehicle_shifting_summary_details(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        vehicle_shifting_details_id = request_data["vehicle_shifting_details_id"]
        chosen_shifting_vehicle_id = request_data["chosen_shifting_vehicle_id"]
        chosen_shifting_vehicle_details = ChosenShiftingVehicle.objects.filter(
            id=chosen_shifting_vehicle_id).first()
        vehicle_shifting_details_id_2 = chosen_shifting_vehicle_details.vehicle_shifting_details.id
        if str(vehicle_shifting_details_id_2) == vehicle_shifting_details_id:
            summary_address_details = VehicleShiftingDetails.objects.filter(id=vehicle_shifting_details_id).first()
            user_id = summary_address_details.user.id
            vehicle_shifting_details_id = summary_address_details.id
            moving_datetime = summary_address_details.moving_datetime
            pickup_location = summary_address_details.pickup_location
            pickup_address = summary_address_details.pickup_address
            pickup_floor = summary_address_details.pickup_floor
            pickup_lift = summary_address_details.pickup_lift
            drop_location = summary_address_details.drop_location
            drop_address = summary_address_details.drop_address
            drop_floor = summary_address_details.drop_floor
            drop_lift = summary_address_details.drop_lift
            vehicle_name = None
            vehicle_model = None
            vehicle_image = None
            vehicle_amount = None

            if chosen_shifting_vehicle_details:
                vehicle_name = chosen_shifting_vehicle_details.vehicle_name
                if vehicle_name is None:
                    vehicle_name = "Empty"

                vehicle_model = chosen_shifting_vehicle_details.vehicle_model
                if vehicle_model is None:
                    vehicle_model = "Empty"

                vehicle_image = chosen_shifting_vehicle_details.vehicle_image
                if vehicle_image is None:
                    vehicle_image = "Empty"

                vehicle_amount = chosen_shifting_vehicle_details.vehicle_amount
                if vehicle_amount is None:
                    vehicle_amount = "Empty"

            return JsonResponse({'status_code': 200,
                                 'message': 'User Vehicle Shifting Details',
                                 "user_id": user_id,
                                 "vehicle_shifting_details_id": vehicle_shifting_details_id,
                                 "chosen_shifting_vehicle_id": chosen_shifting_vehicle_id,
                                 "moving_datetime": moving_datetime,
                                 "pickup_location": pickup_location,
                                 "pickup_address": pickup_address,
                                 "pickup_floor": pickup_floor,
                                 "pickup_lift": pickup_lift,
                                 "drop_location": drop_location,
                                 "drop_address": drop_address,
                                 "drop_floor": drop_floor,
                                 "drop_lift": drop_lift,
                                 "vehicle_name": vehicle_name,
                                 "vehicle_model": vehicle_model,
                                 "vehicle_image": vehicle_image,
                                 "vehicle_amount": vehicle_amount})
        return JsonResponse({"message": "vehicle shifting details page"})


@csrf_exempt
def warehouse_storage_details(request):
    if request.method == "POST":
        if request.body:
            now = timezone.localtime(timezone.now())
            request_data = json.loads(request.body)
            try:
                user_id = request_data["user_id"]
            except:
                user_id = ''

            user = User.objects.filter(id=user_id).first()

            try:
                shifting_type = request_data["shifting_type"]
            except:
                shifting_type = ''
            if shifting_type == '3':
                shifting_type = "Warehouse Storage"
            else:
                shifting_type = "None"

            try:
                moving_datetime = request_data["moving_datetime"]
            except:
                moving_datetime = ''

            if moving_datetime == '':
                moving_datetime = None
            if moving_datetime:
                date_string = moving_datetime
                date_format = "%d/%m/%Y %H:%M"

                datetime_obj = datetime.strptime(date_string, date_format)
                moving_formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                moving_formatted_date = ""


            try:
                pickup_location = request_data["pickup_location"]
            except:
                pickup_location = ''

            if pickup_location == '':
                pickup_location = "None"

            try:
                pickup_address = request_data["pickup_address"]
            except:
                pickup_address = ''

            try:
                pickup_floor = request_data["pickup_floor"]
            except:
                pickup_floor = ""

            try:
                pickup_lift = request_data["pickup_lift"]
            except:
                pickup_lift = ""

            try:
                storing_days = request_data["storing_days"]
            except:
                storing_days = ""

            try:
                order_place_datetime = now
            except:
                order_place_datetime = ''

            if user is not None:
                warehouse_storage_detail = WareHouseStorageDetails(user=user,
                                                                   shifting_type=shifting_type,
                                                                   pickup_location=pickup_location,
                                                                   moving_datetime=moving_formatted_date,
                                                                   pickup_address=pickup_address,
                                                                   pickup_floor=pickup_floor,
                                                                   pickup_lift=pickup_lift,
                                                                   storing_days=storing_days,
                                                                   order_place_datetime=order_place_datetime,
                                                                   created=now,
                                                                   updated=now)
                warehouse_storage_detail.save()

                return JsonResponse({'status_code': 200, 'message': 'User WareHouse Storage Details Saved',
                                     "warehouse_storage_detail_id": warehouse_storage_detail.id})

        else:
            return JsonResponse({'status_code': 400, 'message': 'Need to fill the Warehouse Storage Details properly'})

    return JsonResponse({'message': 'WareHouse Storage Details Page'})


# @csrf_exempt
# def warehouse_selected_vehicle(request):
#     if request.method == "POST":
#         now = timezone.localtime(timezone.now())
#         request_data = json.loads(request.body)
#         warehouse_storage_detail_id = request_data["warehouse_storage_detail_id"]
#         warehouse_storage_detail = WareHouseStorageDetails.objects.filter(id=warehouse_storage_detail_id).first()
#         vehicle_name = request_data["vehicle_name"]
#         vehicle_type = request_data["vehicle_type"]
#         try:
#             vehicle_image = request_data["vehicle_image"]
#         except:
#             vehicle_image = ""
#         if warehouse_storage_detail:
#             warehouse_selected_vehicle = WareHouseSelectedVehicle(warehouse_storage_detail=warehouse_storage_detail,
#                                                                   vehicle_name=vehicle_name,
#                                                                   vehicle_type=vehicle_type,
#                                                                   vehicle_image=vehicle_image,
#                                                                   created=now,
#                                                                   updated=now)
#             warehouse_selected_vehicle.save()
#
#             return JsonResponse({'status_code': 200, 'message': 'WareHouse Selected Vehicle',
#                                  "warehouse_storage_detail_id": warehouse_storage_detail.id})


@csrf_exempt
def warehouse_storing_products(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        warehouse_storage_detail_id = request_data["warehouse_storage_detail_id"]
        product_amount = request_data["product_amount"]
        warehouse_storage_detail = WareHouseStorageDetails.objects.filter(id=warehouse_storage_detail_id).first()
        if request_data["sofa"]:
            requested_sofa = request_data["sofa"]
            single_sofa = requested_sofa["single_sofa"]
            double_sofa = requested_sofa["double_sofa"]
            three_seater = requested_sofa["three_seater"]
            four_seater = requested_sofa["four_seater"]
            five_seater = requested_sofa["five_seater"]
            six_seater = requested_sofa["six_seater"]
            recliner = requested_sofa["recliner"]

        if request_data["bed"]:
            request_bed = request_data["bed"]
            single_bed_storage = request_bed["single_bed_storage"]
            single_bed_dismantallable = request_bed["single_bed_dismantallable"]
            double_bed_storage = request_bed["double_bed_storage"]
            double_bed_dismantallable = request_bed["double_bed_dismantallable"]
            bunk_dismantallabel = request_bed["bunk_dismantallabel"]
            folding_cot_dismantallabel = request_bed["folding_cot_dismantallabel"]

        if request_data["mattress"]:
            request_mattress = request_data["mattress"]
            single_mattress_foldable = request_mattress["single_mattress_foldable"]
            single_mattress_non_foldable = request_mattress["single_mattress_non_foldable"]
            double_mattress_foldable = request_mattress["double_mattress_foldable"]
            double_mattress_nonfoldable = request_mattress["double_mattress_nonfoldable"]

        if request_data["chairs"]:
            request_chairs = request_data["chairs"]
            dining_table_chairs = request_chairs["dining_table_chairs"]
            baby_chairs = request_chairs["baby_chairs"]
            rocking_chair = request_chairs["rocking_chair"]
            plastic_floding_chair = request_chairs["plastic_floding_chair"]
            office_chair = request_chairs["office_chair"]

        if request_data["tables"]:
            request_tables = request_data["tables"]
            bed_side_table = request_tables["bed_side_table"]
            dressing_table = request_tables["dressing_table"]
            study_or_computer_table = request_tables["study_or_computer_table"]
            center_table = request_tables["center_table"]
            dining_table = request_tables["dining_table"]
            tea_poy = request_tables["tea_poy"]

        if request_data["accessories"]:
            request_accessories = request_data["accessories"]
            tv_stand = request_accessories["tv_stand"]
            book_self = request_accessories["book_self"]
            mirror = request_accessories["mirror"]
            shoe_rack = request_accessories["shoe_rack"]
            mandir = request_accessories["mandir"]
            iron_trunk_chest = request_accessories["iron_trunk_chest"]

        if request_data["tv"]:
            request_tv = request_data["tv"]
            tv_size_upto_20 = request_tv["tv_size_upto_20"]
            tv_size_29to43 = request_tv["tv_size_29to43"]
            tv_size_49to55 = request_tv["tv_size_49to55"]
            tv_size_above55 = request_tv["tv_size_above55"]
            home_theater = request_tv["home_theater"]

        if request_data["ac"]:
            request_ac = request_data["ac"]
            ac_split = request_ac["ac_split"]
            ac_window = request_ac["ac_window"]
            cooler = request_ac["cooler"]
            ceiling_fan = request_ac["ceiling_fan"]
            table_fan = request_ac["table_fan"]
            exhaust_fan = request_ac["exhaust_fan"]

        if request_data["fridge"]:
            request_fridge = request_data["fridge"]
            mini_fridge = request_fridge["mini_fridge"]
            small_fridge = request_fridge["small_fridge"]
            medium_fridge = request_fridge["medium_fridge"]
            large_fridge = request_fridge["large_fridge"]
            large_above450_ltrs_fridge = request_fridge["large_above450_ltrs_fridge"]

        if request_data["bathroom"]:
            request_bathroom = request_data["bathroom"]
            washing_machine = request_bathroom["washing_machine"]
            geyser = request_bathroom["geyser"]
            bath_tub = request_bathroom["bath_tub"]

        if request_data["kitchen_utility"]:
            request_kitchen_utility = request_data["kitchen_utility"]
            gas_stove = request_kitchen_utility["gas_stove"]
            water_purifier = request_kitchen_utility["water_purifier"]
            microwave_otg = request_kitchen_utility["microwave_otg"]
            chimney = request_kitchen_utility["chimney"]
            dish_washer = request_kitchen_utility["dish_washer"]
            gas_cylinder = request_kitchen_utility["gas_cylinder"]

        if request_data["home_utility"]:
            request_home_utility = request_data["home_utility"]
            sewing_mechine = request_home_utility["sewing_mechine"]
            vaccum_cleaner = request_home_utility["vaccum_cleaner"]
            lamp = request_home_utility["lamp"]
            plants = request_home_utility["plants"]
            iron_board = request_home_utility["iron_board"]
            dish_antenna = request_home_utility["dish_antenna"]

        if request_data["others"]:
            request_others = request_data["others"]
            inverter_ups = request_others["inverter_ups"]
            treadmill = request_others["treadmill"]
            piano_guitar = request_others["piano_guitar"]

        if request_data["cartons"]:
            request_cartons = request_data["cartons"]
            service_carton_box = request_cartons["service_carton_box"]
            self_carton_box = request_cartons["self_carton_box"]

        if request_data["gunny_bags"]:
            request_gunny_bags = request_data["gunny_bags"]
            gunny_bags = request_gunny_bags["gunny_bags"]

        now = timezone.localtime(timezone.now())
        if warehouse_storage_detail is not None:
            ware_house_storing_products = WareHouseStoringProducts(warehouse_storage_detail=warehouse_storage_detail,
                                                                   product_amount=product_amount,
                                                                   single_sofa=single_sofa,
                                                                   double_sofa=double_sofa,
                                                                   three_seater=three_seater,
                                                                   four_seater=four_seater,
                                                                   five_seater=five_seater,
                                                                   six_seater=six_seater,
                                                                   recliner=recliner,
                                                                   single_bed_storage=single_bed_storage,
                                                                   single_bed_dismantallable=single_bed_dismantallable,
                                                                   double_bed_storage=double_bed_storage,
                                                                   double_bed_dismantallable=double_bed_dismantallable,
                                                                   bunk_dismantallabel=bunk_dismantallabel,
                                                                   folding_cot_dismantallabel=folding_cot_dismantallabel,
                                                                   single_mattress_foldable=single_mattress_foldable,
                                                                   single_mattress_non_foldable=single_mattress_non_foldable,
                                                                   double_mattress_foldable=double_mattress_foldable,
                                                                   double_mattress_nonfoldable=double_mattress_nonfoldable,
                                                                   dining_table_chairs=dining_table_chairs,
                                                                   baby_chairs=baby_chairs,
                                                                   rocking_chair=rocking_chair,
                                                                   plastic_floding_chair=plastic_floding_chair,
                                                                   office_chair=office_chair,
                                                                   bed_side_table=bed_side_table,
                                                                   dressing_table=dressing_table,
                                                                   study_or_computer_table=study_or_computer_table,
                                                                   center_table=center_table,
                                                                   dining_table=dining_table,
                                                                   tea_poy=tea_poy,
                                                                   tv_stand=tv_stand,
                                                                   book_self=book_self,
                                                                   mirror=mirror,
                                                                   shoe_rack=shoe_rack,
                                                                   mandir=mandir,
                                                                   iron_trunk_chest=iron_trunk_chest,
                                                                   tv_size_upto_20=tv_size_upto_20,
                                                                   tv_size_29to43=tv_size_29to43,
                                                                   tv_size_49to55=tv_size_49to55,
                                                                   tv_size_above55=tv_size_above55,
                                                                   home_theater=home_theater,
                                                                   ac_split=ac_split,
                                                                   ac_window=ac_window,
                                                                   cooler=cooler,
                                                                   ceiling_fan=ceiling_fan,
                                                                   table_fan=table_fan,
                                                                   exhaust_fan=exhaust_fan,
                                                                   mini_fridge=mini_fridge,
                                                                   small_fridge=small_fridge,
                                                                   medium_fridge=medium_fridge,
                                                                   large_fridge=large_fridge,
                                                                   large_above450_ltrs_fridge=large_above450_ltrs_fridge,
                                                                   washing_machine=washing_machine,
                                                                   geyser=geyser,
                                                                   bath_tub=bath_tub,
                                                                   gas_stove=gas_stove,
                                                                   water_purifier=water_purifier,
                                                                   microwave_otg=microwave_otg,
                                                                   chimney=chimney,
                                                                   dish_washer=dish_washer,
                                                                   gas_cylinder=gas_cylinder,
                                                                   sewing_mechine=sewing_mechine,
                                                                   vaccum_cleaner=vaccum_cleaner,
                                                                   lamp=lamp,
                                                                   plants=plants,
                                                                   iron_board=iron_board,
                                                                   dish_antenna=dish_antenna,
                                                                   inverter_ups=inverter_ups,
                                                                   treadmill=treadmill,
                                                                   piano_guitar=piano_guitar,
                                                                   service_carton_box=service_carton_box,
                                                                   self_carton_box=self_carton_box,
                                                                   gunny_bags=gunny_bags,
                                                                   created=now,
                                                                   updated=now)
            ware_house_storing_products.save()

            return JsonResponse({'status_code': 200, 'message': 'User WareHouse Storing products',
                                 "warehouse_storing_products": ware_house_storing_products.id,
                                 "warehouse_storage_details_id": warehouse_storage_detail.id})


@csrf_exempt
def warehouse_summary_details(request):
    request_data = json.loads(request.body)
    warehouse_storage_detail_id = request_data["warehouse_storage_details_id"]
    warehouse_storing_products_id = request_data["warehouse_storing_products_id"]
    ware_house_storing_products = WareHouseStoringProducts.objects \
        .filter(id=warehouse_storing_products_id) \
        .first()
    warehouse_storage_details_id_2 = ware_house_storing_products.warehouse_storage_detail.id
    if str(warehouse_storage_details_id_2) == warehouse_storage_detail_id:
        summary_address_details = WareHouseStorageDetails.objects.filter(id=warehouse_storage_detail_id).first()
        user_id = summary_address_details.user.id
        shifting_type = summary_address_details.shifting_type
        moving_datetime = summary_address_details.moving_datetime
        pickup_location = summary_address_details.pickup_location
        pickup_address = summary_address_details.pickup_address
        pickup_floor = summary_address_details.pickup_floor
        pickup_lift = summary_address_details.pickup_lift
        storing_days = summary_address_details.storing_days

        # warehouse_selected_vehicle = WareHouseSelectedVehicle.objects \
        #     .filter(warehouse_storage_detail=warehouse_storage_detail_id) \
        #     .first()

        if ware_house_storing_products.product_amount:
            product_amount = ware_house_storing_products.product_amount
        else:
            product_amount = None

        if ware_house_storing_products.single_sofa:
            single_sofa = ware_house_storing_products.single_sofa
        else:
            single_sofa = None

        if ware_house_storing_products.double_sofa:
            double_sofa = ware_house_storing_products.double_sofa
        else:
            double_sofa = None

        if ware_house_storing_products.three_seater:
            three_seater = ware_house_storing_products.three_seater
        else:
            three_seater = None

        if ware_house_storing_products.four_seater:
            four_seater = ware_house_storing_products.four_seater
        else:
            four_seater = None

        if ware_house_storing_products.five_seater:
            five_seater = ware_house_storing_products.five_seater
        else:
            five_seater = None

        if ware_house_storing_products.six_seater:
            six_seater = ware_house_storing_products.six_seater
        else:
            six_seater = None

        if ware_house_storing_products.recliner:
            recliner = ware_house_storing_products.recliner
        else:
            recliner = None

        if ware_house_storing_products.single_bed_storage:
            single_bed_storage = ware_house_storing_products.single_bed_storage
        else:
            single_bed_storage = None

        if ware_house_storing_products.single_bed_dismantallable:
            single_bed_dismantallable = ware_house_storing_products.single_bed_dismantallable
        else:
            single_bed_dismantallable = None

        if ware_house_storing_products.double_bed_storage:
            double_bed_storage = ware_house_storing_products.double_bed_storage
        else:
            double_bed_storage = ""

        if ware_house_storing_products.double_bed_dismantallable:
            double_bed_dismantallable = ware_house_storing_products.double_bed_dismantallable
        else:
            double_bed_dismantallable = None

        if ware_house_storing_products.bunk_dismantallabel:
            bunk_dismantallabel = ware_house_storing_products.bunk_dismantallabel
        else:
            bunk_dismantallabel = None

        if ware_house_storing_products.folding_cot_dismantallabel:
            folding_cot_dismantallabel = ware_house_storing_products.folding_cot_dismantallabel
        else:
            folding_cot_dismantallabel = None

        if ware_house_storing_products.single_mattress_foldable:
            single_mattress_foldable = ware_house_storing_products.single_mattress_foldable
        else:
            single_mattress_foldable = None

        if ware_house_storing_products.single_mattress_non_foldable:
            single_mattress_non_foldable = ware_house_storing_products.single_mattress_non_foldable
        else:
            single_mattress_non_foldable = None

        if ware_house_storing_products.double_mattress_foldable:
            double_mattress_foldable = ware_house_storing_products.double_mattress_foldable
        else:
            double_mattress_foldable = None

        if ware_house_storing_products.double_mattress_nonfoldable:
            double_mattress_nonfoldable = ware_house_storing_products.double_mattress_nonfoldable
        else:
            double_mattress_nonfoldable = None

        if ware_house_storing_products.dining_table_chairs:
            dining_table_chairs = ware_house_storing_products.dining_table_chairs
        else:
            dining_table_chairs = None

        if ware_house_storing_products.baby_chairs:
            baby_chairs = ware_house_storing_products.baby_chairs
        else:
            baby_chairs = None

        if ware_house_storing_products.rocking_chair:
            rocking_chair = ware_house_storing_products.rocking_chair
        else:
            rocking_chair = None

        if ware_house_storing_products.plastic_floding_chair:
            plastic_floding_chair = ware_house_storing_products.plastic_floding_chair
        else:
            plastic_floding_chair = None

        if ware_house_storing_products.office_chair:
            office_chair = ware_house_storing_products.office_chair
        else:
            office_chair = None

        if ware_house_storing_products.bed_side_table:
            bed_side_table = ware_house_storing_products.bed_side_table
        else:
            bed_side_table = None

        if ware_house_storing_products.dressing_table:
            dressing_table = ware_house_storing_products.dressing_table
        else:
            dressing_table = None

        if ware_house_storing_products.study_or_computer_table:
            study_or_computer_table = ware_house_storing_products.study_or_computer_table
        else:
            study_or_computer_table = None

        if ware_house_storing_products.center_table:
            center_table = ware_house_storing_products.center_table
        else:
            center_table = None

        if ware_house_storing_products.dining_table:
            dining_table = ware_house_storing_products.dining_table
        else:
            dining_table = None

        if ware_house_storing_products.tea_poy:
            tea_poy = ware_house_storing_products.tea_poy
        else:
            tea_poy = None

        if ware_house_storing_products.tv_stand:
            tv_stand = ware_house_storing_products.tv_stand
        else:
            tv_stand = None

        if ware_house_storing_products.book_self:
            book_self = ware_house_storing_products.book_self
        else:
            book_self = None

        if ware_house_storing_products.mirror:
            mirror = ware_house_storing_products.mirror
        else:
            mirror = None

        if ware_house_storing_products.shoe_rack:
            shoe_rack = ware_house_storing_products.shoe_rack
        else:
            shoe_rack = None

        if ware_house_storing_products.mandir:
            mandir = ware_house_storing_products.mandir
        else:
            mandir = None

        if ware_house_storing_products.iron_trunk_chest:
            iron_trunk_chest = ware_house_storing_products.iron_trunk_chest
        else:
            iron_trunk_chest = None

        if ware_house_storing_products.tv_size_upto_20:
            tv_size_upto_20 = ware_house_storing_products.tv_size_upto_20
        else:
            tv_size_upto_20 = None

        if ware_house_storing_products.tv_size_29to43:
            tv_size_29to43 = ware_house_storing_products.tv_size_29to43
        else:
            tv_size_29to43 = None

        if ware_house_storing_products.tv_size_49to55:
            tv_size_49to55 = ware_house_storing_products.tv_size_49to55
        else:
            tv_size_49to55 = None

        if ware_house_storing_products.tv_size_above55:
            tv_size_above55 = ware_house_storing_products.tv_size_above55
        else:
            tv_size_above55 = None

        if ware_house_storing_products.home_theater:
            home_theater = ware_house_storing_products.home_theater
        else:
            home_theater = None

        if ware_house_storing_products.ac_split:
            ac_split = ware_house_storing_products.ac_split
        else:
            ac_split = None

        if ware_house_storing_products.ac_window:
            ac_window = ware_house_storing_products.ac_window
        else:
            ac_window = None

        if ware_house_storing_products.cooler:
            cooler = ware_house_storing_products.cooler
        else:
            cooler = None

        if ware_house_storing_products.ceiling_fan:
            ceiling_fan = ware_house_storing_products.ceiling_fan
        else:
            ceiling_fan = None

        if ware_house_storing_products.table_fan:
            table_fan = ware_house_storing_products.table_fan
        else:
            table_fan = None

        if ware_house_storing_products.exhaust_fan:
            exhaust_fan = ware_house_storing_products.exhaust_fan
        else:
            exhaust_fan = None

        if ware_house_storing_products.mini_fridge:
            mini_fridge = ware_house_storing_products.mini_fridge
        else:
            mini_fridge = None

        if ware_house_storing_products.small_fridge:
            small_fridge = ware_house_storing_products.small_fridge
        else:
            small_fridge = None

        if ware_house_storing_products.medium_fridge:
            medium_fridge = ware_house_storing_products.medium_fridge
        else:
            medium_fridge = None

        if ware_house_storing_products.large_fridge:
            large_fridge = ware_house_storing_products.large_fridge
        else:
            large_fridge = None

        if ware_house_storing_products.large_above450_ltrs_fridge:
            large_above450_ltrs_fridge = ware_house_storing_products.large_above450_ltrs_fridge
        else:
            large_above450_ltrs_fridge = None

        if ware_house_storing_products.washing_machine:
            washing_machine = ware_house_storing_products.washing_machine
        else:
            washing_machine = None

        if ware_house_storing_products.geyser:
            geyser = ware_house_storing_products.geyser
        else:
            geyser = None

        if ware_house_storing_products.bath_tub:
            bath_tub = ware_house_storing_products.bath_tub
        else:
            bath_tub = None

        if ware_house_storing_products.gas_stove:
            gas_stove = ware_house_storing_products.gas_stove
        else:
            gas_stove = None

        if ware_house_storing_products.water_purifier:
            water_purifier = ware_house_storing_products.water_purifier
        else:
            water_purifier = None

        if ware_house_storing_products.microwave_otg:
            microwave_otg = ware_house_storing_products.microwave_otg
        else:
            microwave_otg = None

        if ware_house_storing_products.chimney:
            chimney = ware_house_storing_products.chimney
        else:
            chimney = None

        if ware_house_storing_products.dish_washer:
            dish_washer = ware_house_storing_products.dish_washer
        else:
            dish_washer = None

        if ware_house_storing_products.gas_cylinder:
            gas_cylinder = ware_house_storing_products.gas_cylinder
        else:
            gas_cylinder = None

        if ware_house_storing_products.inverter_ups:
            inverter_ups = ware_house_storing_products.inverter_ups
        else:
            inverter_ups = None

        if ware_house_storing_products.treadmill:
            treadmill = ware_house_storing_products.treadmill
        else:
            treadmill = None

        if ware_house_storing_products.piano_guitar:
            piano_guitar = ware_house_storing_products.piano_guitar
        else:
            piano_guitar = None

        if ware_house_storing_products.sewing_mechine:
            sewing_mechine = ware_house_storing_products.sewing_mechine
        else:
            sewing_mechine = None

        if ware_house_storing_products.vaccum_cleaner:
            vaccum_cleaner = ware_house_storing_products.vaccum_cleaner
        else:
            vaccum_cleaner = None

        if ware_house_storing_products.lamp:
            lamp = ware_house_storing_products.lamp
        else:
            lamp = None

        if ware_house_storing_products.plants:
            plants = ware_house_storing_products.plants
        else:
            plants = None

        if ware_house_storing_products.iron_board:
            iron_board = ware_house_storing_products.iron_board
        else:
            iron_board = None

        if ware_house_storing_products.dish_antenna:
            dish_antenna = ware_house_storing_products.dish_antenna
        else:
            dish_antenna = None

        if ware_house_storing_products.service_carton_box:
            service_carton_box = ware_house_storing_products.service_carton_box
        else:
            service_carton_box = None

        if ware_house_storing_products.self_carton_box:
            self_carton_box = ware_house_storing_products.self_carton_box
        else:
            self_carton_box = None

        if ware_house_storing_products.gunny_bags:
            gunny_bags = ware_house_storing_products.gunny_bags
        else:
            gunny_bags = None

        return JsonResponse({'status_code': 200,
                             'message': 'User Ware House Storing Products Details',
                             "user_id": user_id,
                             "warehouse_storing_details_id": warehouse_storage_detail_id,
                             "warehouse_storing_products_id": warehouse_storing_products_id,
                             # "warehouse_selected_vehicle_id": warehouse_selected_vehicle.id,
                             "product_amount":product_amount,
                             "shifting_type": shifting_type,
                             "moving_datetime": moving_datetime,
                             "pickup_location": pickup_location,
                             "pickup_address": pickup_address,
                             "pickup_floor": pickup_floor,
                             "pickup_lift": pickup_lift,
                             "storing_days": storing_days,

                             "sofa": {
                                 "single_sofa": single_sofa,
                                 "double_sofa": double_sofa,
                                 "three_seater": three_seater,
                                 "four_seater": four_seater,
                                 "five_seater": five_seater,
                                 "six_seater": six_seater,
                                 "recliner": recliner
                             },
                             "bed": {
                                 "single_bed_storage": single_bed_storage,
                                 "single_bed_dismantallable": single_bed_dismantallable,
                                 "double_bed_storage": double_bed_storage,
                                 "double_bed_dismantallable": double_bed_dismantallable,
                                 "bunk_dismantallabel": bunk_dismantallabel,
                                 "folding_cot_dismantallabel": folding_cot_dismantallabel
                             },
                             "mattress": {
                                 "single_mattress_foldable": single_mattress_foldable,
                                 "single_mattress_non_foldable": single_mattress_non_foldable,
                                 "double_mattress_foldable": double_mattress_foldable,
                                 "double_mattress_nonfoldable": double_mattress_nonfoldable
                             },
                             "chairs": {
                                 "dining_table_chairs": dining_table_chairs,
                                 "baby_chairs": baby_chairs,
                                 "rocking_chair": rocking_chair,
                                 "plastic_floding_chair": plastic_floding_chair,
                                 "office_chair": office_chair
                             },
                             "tables": {
                                 "bed_side_table": bed_side_table,
                                 "dressing_table": dressing_table,
                                 "study_or_computer_table": study_or_computer_table,
                                 "center_table": center_table,
                                 "dining_table": dining_table,
                                 "tea_poy": tea_poy
                             },
                             "accessories": {
                                 "tv_stand": tv_stand,
                                 "book_self": book_self,
                                 "mirror": mirror,
                                 "shoe_rack": shoe_rack,
                                 "mandir": mandir,
                                 "iron_trunk_chest": iron_trunk_chest
                             },
                             "tv": {
                                 "tv_size_upto_20": tv_size_upto_20,
                                 "tv_size_29to43": tv_size_29to43,
                                 "tv_size_49to55": tv_size_49to55,
                                 "tv_size_above55": tv_size_above55,
                                 "home_theater": home_theater
                             },
                             "ac": {
                                 "ac_split": ac_split,
                                 "ac_window": ac_window,
                                 "cooler": cooler,
                                 "ceiling_fan": ceiling_fan,
                                 "table_fan": table_fan,
                                 "exhaust_fan": exhaust_fan
                             },
                             "fridge": {
                                 "mini_fridge": mini_fridge,
                                 "small_fridge": small_fridge,
                                 "medium_fridge": medium_fridge,
                                 "large_fridge": large_fridge,
                                 "large_above450_ltrs_fridge": large_above450_ltrs_fridge
                             },
                             "bathroom": {
                                 "washing_machine": washing_machine,
                                 "geyser": geyser,
                                 "bath_tub": bath_tub
                             },
                             "kitchen_utility": {
                                 "gas_stove": gas_stove,
                                 "water_purifier": water_purifier,
                                 "microwave_otg": microwave_otg,
                                 "chimney": chimney,
                                 "dish_washer": dish_washer,
                                 "gas_cylinder": gas_cylinder
                             },
                             "others": {
                                 "inverter_ups": inverter_ups,
                                 "treadmill": treadmill,
                                 "piano_guitar": piano_guitar
                             },
                             "home_utility": {
                                 "sewing_mechine": sewing_mechine,
                                 "vaccum_cleaner": vaccum_cleaner,
                                 "lamp": lamp,
                                 "plants": plants,
                                 "iron_board": iron_board,
                                 "dish_antenna": dish_antenna
                             },
                             "cartons": {
                                 "service_carton_box": service_carton_box,
                                 "self_carton_box": self_carton_box
                             },
                             "gunny_bags": {
                                 "gunny_bags": gunny_bags
                             }

                             })
    else:
        return JsonResponse({'status_code': 200, "message": "WareHouse Storing Details id is None"})


@csrf_exempt
def order_booking(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        if request_data:
            try:
                user_id = request_data['user_id']
            except:
                user_id = None
            try:
                house_shifting_details_id = request_data['house_shifting_details_id']
            except:
                house_shifting_details_id = None

            try:
                house_shifting_product_id = request_data['house_shifting_product_id']
            except:
                house_shifting_product_id = None

            try:
                vehicle_shifting_details_id = request_data['vehicle_shifting_details_id']
            except:
                vehicle_shifting_details_id = None

            try:
                chosen_shifting_vehicle_details_id = request_data['chosen_shifting_vehicle_details_id']
            except:
                chosen_shifting_vehicle_details_id = ""
            try:
                warehouse_storing_details_id = request_data['warehouse_storing_details_id']
            except:
                warehouse_storing_details_id = None

            try:
                warehouse_storing_products_id = request_data['warehouse_storing_products_id']
            except:
                warehouse_storing_products_id = None

            try:
                booking_datetime = request_data['booking_datetime']

            except:
                booking_datetime = ""
            if booking_datetime:
                date_string = booking_datetime
                date_format = "%d/%m/%Y %H:%M"

                datetime_obj = datetime.strptime(date_string, date_format)
                booking_formatted_date = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                booking_formatted_date = ""


            try:
                shifting_type = request_data['shifting_type']
            except:
                shifting_type = None

            try:
                payment_method = request_data['payment_method']
            except:
                payment_method = None

            try:
                total_amount = request_data['total_amount']
            except:
                total_amount = None

            if payment_method == "COD":
                now = timezone.localtime(timezone.now())
                booking_id = None
                if user_id:
                    print(">>>>>>>")
                    user = User.objects.filter(id=user_id).first()
                    order_booking = OrderBooking(user=user,
                                                 booking_id=booking_id,
                                                 booking_datetime=booking_formatted_date,
                                                 house_shifting_details_id=house_shifting_details_id,
                                                 house_shifting_product_id=house_shifting_product_id,
                                                 vehicle_shifting_details_id=vehicle_shifting_details_id,
                                                 chosen_shifting_vehicle_details_id=chosen_shifting_vehicle_details_id,
                                                 ware_house_storing_details_id=warehouse_storing_details_id,
                                                 ware_house_storing_products_id=warehouse_storing_products_id,
                                                 shifting_type=shifting_type,
                                                 payment_method=payment_method,
                                                 total_amount=total_amount,
                                                 created=now,
                                                 updated=now)
                    order_booking.save()
                    booking_id = order_booking.id
                    booking_details_id = OrderBooking.objects.filter(id=booking_id).first()
                    booking_details_id.booking_id = "APM00" + str(booking_id)
                    booking_details_id.save()
                    if not booking_details_id.house_shifting_details_id == None or booking_details_id.house_shifting_details_id == " ":
                        house_shifting_id = booking_details_id.house_shifting_details_id
                        house_shifting_details = HouseShiftingDetails.objects.filter(id=house_shifting_id).first()
                        house_shifting_details.booking_id = "APM00" + str(booking_id)
                        house_shifting_details.save()
                    elif not booking_details_id.vehicle_shifting_details_id == None or booking_details_id.vehicle_shifting_details_id == " ":
                        vehicle_shifting_id = booking_details_id.vehicle_shifting_details_id
                        vehicle_shifting_details = VehicleShiftingDetails.objects.filter(id=vehicle_shifting_id).first()
                        vehicle_shifting_details.booking_id = "APM00" + str(booking_id)
                        vehicle_shifting_details.save()
                    elif not booking_details_id.ware_house_storing_details_id == None or booking_details_id.ware_house_storing_details_id == " ":
                        ware_house_storing_id = booking_details_id.ware_house_storing_details_id
                        warehouse_storage_details = WareHouseStorageDetails.objects.filter(id=ware_house_storing_id).first()
                        warehouse_storage_details.booking_id = "APM00" + str(booking_id)
                        warehouse_storage_details.save()
                    else:
                        shifting_id = None
                    booking_ids = booking_details_id.booking_id
                    return JsonResponse({"status": 200,
                                         "message": "Your order placed successfully",
                                         "Booking_id": booking_ids})

            else:
                booking_id = None
                # now = timezone.localtime(timezone.now())
                # user = User.objects.filter(id=user_id).first()
                # order_booking = OrderBooking(user=user,
                #                              house_shifting_details_id=house_shifting_details_id,
                #                              house_shifting_product_id=house_shifting_product_id,
                #                              vehicle_shifting_details_id=vehicle_shifting_details_id,
                #                              ware_house_storing_details_id=ware_house_storing_details_id,
                #                              ware_house_storing_products_id=ware_house_storing_products_id,
                #                              shifting_type=shifting_type,
                #                              created=now,
                #                              updated=now)
                # order_booking.save()
                # booking_id = order_booking.id
                return JsonResponse({"status": 200,
                                     "message": "Online Payment not yet",
                                     "Booking_id": booking_id})

        else:
            return JsonResponse({"status": 400,
                                 "message": "user details are not getting properly"})

