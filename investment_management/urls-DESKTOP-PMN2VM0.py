from django.contrib import admin
from django.urls import path, include
from investment_management import views  # Import your views module
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('add_investment/', views.add_investment, name='add_investment'),
    path('investment_list/', views.investment_list, name='investment_list'),
    path('add_transaction/', views.add_transaction, name='add_transaction'),
    path('investment_detail/<int:investment_id>/', views.investment_detail, name='investment_detail'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transaction_list/', views.transaction_list, name='transaction_list'),
  path('calculate_investment_schedule/<int:investment_id>/', views.calculate_investment_schedule, name='calculate_investment_schedule'),
   path('schedule/<int:investment_id>/', views.schedule, name='schedule'),
    # Add a URL pattern for the root URL
    path('transactions/<int:transaction_id>/edit/', views.edit_transaction, name='transaction_edit'),
    path('transactions/<int:transaction_id>/delete/', views.delete_transaction, name='transaction_delete'),
    path('', views.home, name='home'),
     path('investment/<int:investment_id>/delete/', views.delete_investment, name='delete_investment'),
     path('investments/<int:investment_id>/edit/', views.edit_investment, name='edit_investment'),
     path('investment/<int:investment_id>/download_schedule/', views.download_schedule, name='download_schedule'),
     path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
      path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add_user/', views.add_user, name='add_user'),
      path('profile/edit/', views.profile_edit, name='profile_edit'),
       path('investment_data/', views.investment_data, name='investment_data'),
        path('access_logs/', views.access_logs, name='user_log'),
        path('report/',views.report, name='report'),
         path('create_group/', views.create_investment_group, name='create_group'),
    path('group_list/', views.group_list, name='group_list'),
    path('join_group/<int:group_id>/', views.join_group, name='join_group'),
    path('leave_group/<int:group_id>/', views.leave_group, name='leave_group'),
   path('groups/join/<int:group_id>/', views.group_join, name='group_join'),
 path('groups/user-selection/<int:group_id>/', views.user_selection, name='user_selection'),
 path('groups/details/<int:group_id>/', views.group_details, name='group_details'),
 path('groups/delete/<int:group_id>/', views.delete_group, name='delete_group'),
 path('groups/add-members/<int:group_id>/', views.add_members, name='add_members'),
path('investment-report/', views.investment_report, name='investment_report'),
path('group_investment_schedule/<int:group_id>/', views.group_investment_schedule, name='group_investment_schedule'),
#path('investment_group_details/<int:group_id>/', views.investment_group_details, name='investment_group_details'),
 path('edit_group/<int:group_id>/', views.edit_investment_group, name='edit_investment_group'),
 path('investment-group/<int:group_id>/', views.investment_group_detail, name='investment_group_details'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)