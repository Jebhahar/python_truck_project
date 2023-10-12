from django.urls import path
from . import views

urlpatterns = [
    path('', views.webpage, name=''),
    path('Login/', views.login, name='Login'),
    path('Register/', views.register, name='Register'),
    path('UserProfile/', views.user_profile, name='UserProfile_v1'),
    path('HouseShiftingDetails/', views.house_shifting_details, name='HouseShiftingDetails'),
    path('HouseShiftingProducts/', views.house_shifting_products, name='HouseShiftingProducts'),
    path('HouseShiftingSummaryDetails/', views.house_shifting_summary_details, name='HouseShiftingSummaryDetails'),
    path('VehicleShiftingDetails/', views.vehicle_shifting_details, name='VehicleShiftingDetails'),
    path('ChooseShiftingVehicle/', views.chosen_shifting_vehicle, name='ChooseShiftingVehicle'),
    path('VehicleShiftingSummaryDetails/', views.vehicle_shifting_summary_details, name='VehicleShiftingSummaryDetails'),
    path('WareHouseStorageDetails/', views.warehouse_storage_details, name='VehicleShiftingSummaryDetails'),
    path('WareHouseSelectedVehicle/', views.warehouse_selected_vehicle, name='WareHouseSelectedVehicle'),
    path('WareHouseStoringProducts/', views.warehouse_storing_products, name='WareHouseStoringProducts'),
    path('WareHouseSummaryDetails/', views.warehouse_summary_details, name='WareHouseSummaryDetails'),

]

