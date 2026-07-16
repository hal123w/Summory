from django.urls import path

from . import views

app_name = 'summaries'

urlpatterns = [
    path('login/', views.SummoryLoginView.as_view(), name='login'),
    path('logout/', views.SummoryLogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('', views.summary_create, name='create'),
    path('history/', views.summary_list, name='list'),
    path('<int:pk>/', views.summary_detail, name='detail'),
    path('<int:pk>/edit/', views.summary_edit, name='edit'),
    path('<int:pk>/delete/', views.summary_delete, name='delete'),
]
