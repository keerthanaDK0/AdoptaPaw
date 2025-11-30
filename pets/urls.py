from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views
from .views import custom_login_view, register_view
from django.contrib.auth.views import LogoutView
from .views import CustomPasswordResetView


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('footer/', views.footer, name='footer.html'),
    path('user_dashboard/', views.user_home, name='user_home'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_home'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_home'),
    path('contact-us/', views.contact_us, name='contact_us'),

    path('login/', custom_login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),


    path('pet_details/<int:pet_id>/', views.pet_detail, name='pet_detail'),
# urls.py
    path('viewpets/', views.view_pets, name='viewpets'),
    path('chatroom/<int:pet_id>/', views.create_or_redirect_chat, name='create_or_redirect_chat'),
    path('chatroom/<int:pet_id>/<int:other_user_id>/', views.chatroom, name='chatroom'),
    path('delete_message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('seller_chats/', views.seller_chat_list, name='seller_chat_list'),
    path('seller_home/', views.seller_home, name='seller_home'),
    path('add_pets/', views.add_pets, name='add_pets'),
    path('view_my_pets/', views.view_my_pets, name='view_my_pets'),
    path('feedback/', views.feedback, name='feedback'),
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('buyer-request/', views.buyer_request_view, name='buyer_request'),
    path('buyer-request/update/<int:request_id>/<str:status>/', views.update_request_status, name='update_buyer_request_status'),
    path('seller-request/', views.seller_request, name='seller_requests'),
    path('seller-request/view/<int:request_id>/', views.view_seller_request, name='view_seller_request'),
    path('request_doctor_clearance/<int:pet_id>/', views.request_doctor_clearance, name='request_doctor_clearance'),
    path('my-requests/', views.my_requests, name='my_requests'),
    #path('submit-doctor-clearance-request/<int:pet_id>/', views.submit_doctor_clearance_request, name='submit_doctor_clearance_request'),
    #path('clearance-success/', views.clearance_success, name='clearance_success'),
    #path('clearance-error/', views.clearance_error, name='clearance_error'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('mark_as_adopted/<int:pet_id>/', views.mark_as_adopted, name='mark_as_adopted'),
    path('activate-user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate-user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('update-pet-status/<int:pet_id>/', views.update_pet_status, name='update_pet_status'),
    path('approve-pets/', views.approve_pets, name='approve_pets'),
    path('approve-pet/<int:pet_id>/', views.approve_pet, name='approve_pet'),
    path('reject-pet/<int:pet_id>/', views.reject_pet, name='reject_pet'),
    path('add-doctor/', views.add_doctor, name='add_doctor'),
    path('view-doctors/', views.view_doctors, name='view_doctors'),
    path('edit_doctor/<int:id>/', views.edit_doctor, name='edit_doctor'),
    path('delete_doctor/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('viewfeedback/', views.view_feedback, name='view_feedback'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('shop/', views.product_list, name='shop'),
]








