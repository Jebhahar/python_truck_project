from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name="logout"),
    path('Dashboard/', views.dashboard, name='Dashboard'),
    path('CustomerDetails/', views.customer_details, name='CustomerDetails'),
    path("HouseShifting/", views.house_shifting, name="HouseShifting"),
    path('VehicleShifting/', views.vehicle_shifting, name='VehicleShifting'),
    path('WarehouseShifting/', views.warehouse_shifting, name='WarehouseShifting'),
    path('Verify_Phone_Number/', views.verify_phone_number, name='Verify_Phone_Number'),
    path('ChangeNewPassword/<str:phone_number>', views.change_new_password, name='ChangeNewPassword'),
    # path('Completed/', views.completed, name='Completed'),
    # path('Pending/', views.pending, name='Pending'),
    path('Testing/', views.testing, name='Testing'),
    path('HouseShifting_Details/<int:id>', views.house_shifting_details, name='HouseShifting_Details'),
    path('VehicleShifting_Details/<int:id>', views.vehicle_shifting_details, name='VehicleShifting_Details'),
    path('WarehouseShifting_Details/<int:id>', views.warehouse_shifting_details, name='WarehouseShifting_Details'),


]
