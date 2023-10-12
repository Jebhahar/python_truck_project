from django.urls import path
from . import views

urlpatterns = [
    path('', views.webpage, name=''),
    path('Login/', views.login, name='Login'),
    path('Register/', views.register, name='Register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('Resend_otp/', views.resend_otp, name="Resend_otp"),
    path("VerifyPhoneNumber/", views.verify_phone_number, name='VerifyPhoneNumber'),
    path("ResetPassword/", views.reset_password, name='ResetPassword'),
    path('UserProfile/', views.user_profile, name='UserProfile'),
    path("BookingDetails/", views.booking_details, name="BookingDetails"),
    path("UserBookingDetails/", views.user_booking_details, name="UserBookingDetails"),
    path('HouseShiftingDetails/', views.house_shifting_details, name='HouseShiftingDetails'),
    # path('HouseShiftingSelectedVehicle/', views.house_shifting_selected_vehicle, name='HouseShiftingSelectedVehicle'),
    path('HouseShiftingProducts/', views.house_shifting_products, name='HouseShiftingProducts'),
    path('HouseShiftingSummaryDetails/', views.house_shifting_summary_details, name='HouseShiftingSummaryDetails'),
    path('VehicleShiftingDetails/', views.vehicle_shifting_details, name='VehicleShiftingDetails'),
    path('ChooseShiftingVehicle/', views.chosen_shifting_vehicle, name='ChooseShiftingVehicle'),
    path('VehicleShiftingSummaryDetails/', views.vehicle_shifting_summary_details, name='VehicleShiftingSummaryDetails'),
    path('WareHouseStorageDetails/', views.warehouse_storage_details, name='WareHouseStorageDetails'),
    # path('WareHouseSelectedVehicle/', views.warehouse_selected_vehicle, name='WareHouseSelectedVehicle'),
    path('WareHouseStoringProducts/', views.warehouse_storing_products, name='WareHouseStoringProducts'),
    path('WareHouseSummaryDetails/', views.warehouse_summary_details, name='WareHouseSummaryDetails'),
    path('OrderBooking/', views.order_booking, name='OrderBooking'),

]


