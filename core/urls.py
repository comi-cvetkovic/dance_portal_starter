from django.urls import path
from . import views
from .views import event_awards_view

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include

urlpatterns = [
    # General pages
    path('', views.home, name='home'),
    path('register/', views.register_club, name='register_club'),
    path('dashboard/', views.club_dashboard, name='club_dashboard'),

    # Dancer management
    path('add/', views.add_dancer, name='add_dancer'),
    path('clubs/<int:club_id>/dancers/add/', views.add_dancer, name='admin_add_dancer'),
    path('list/', views.list_dancers, name='list_dancers'),
    path('dancers/delete/<int:dancer_id>/', views.delete_dancer, name='delete_dancer'),

    # Superuser: Dancer management by club
    path('clubs/<int:club_id>/dancers/', views.list_dancers, name='admin_list_dancers'),
    path('clubs/<int:club_id>/dancers/add/', views.add_dancer, name='add_dancer_by_club'),
    path('clubs/<int:club_id>/dancers/<int:dancer_id>/delete/', views.delete_dancer, name='delete_dancer_by_club'),

    # Club management (admin)
    path('manage/clubs/register/', views.register_club, name='admin_register_club'),
    path('manage/clubs/<int:club_id>/delete/', views.delete_club, name='delete_club'),

    # Event management
    path('events/create/', views.create_event, name='create_event'),
    path('events/', views.event_list, name='event_list'),

    # Event registration (by club or admin)
    path('events/<int:event_id>/register/', views.register_dancer, name='register_dancer'),
    path('events/<int:event_id>/register/<int:club_id>/', views.register_dancer, name='admin_register_dancer'),

    # View participants for an event
    path('events/<int:event_id>/participants/', views.list_event_participants, name='list_event_participants'),

    path('events/<int:event_id>/styles/manage/', views.manage_styles, name='manage_styles'),

    path('manage/clubs/<int:club_id>/edit/', views.edit_club, name='edit_club'),
    path('myclub/edit/', views.edit_club, name='edit_own_club'),
    path('dancers/<int:dancer_id>/edit/', views.edit_dancer, name='edit_dancer'),
    path('participation/<int:participation_id>/edit/', views.edit_participation, name='edit_participation'),
    path('participation/<int:participation_id>/delete/', views.delete_participation, name='delete_participation'),
    path('participation/delete/', views.delete_participation_group, name='delete_participation_group'),

    path('events/<int:event_id>/startlist/', views.start_list, name='start_list'),
    path('events/<int:event_id>/startlist/manage/', views.manage_start_list, name='manage_start_list'),
    path('public/events/', views.event_list_public, name='event_list_public'),

    path('events/<int:event_id>/startlist/publish/', views.publish_start_list, name='publish_start_list'),
    path('events/<int:event_id>/startlist/unpublish/', views.unpublish_start_list, name='unpublish_start_list'),
    
    path("events/<int:event_id>/music/", views.event_music_view, name="event_music"),

    path('manage/clubs/pending/', views.pending_club_requests, name='pending_club_requests'),

    path('events/<int:event_id>/create_judges/', views.create_judges_for_event, name='create_judges'),
    path('events/<int:event_id>/judge/', views.judge_view, name='judge_view'),
    path('events/<int:event_id>/delete_judges/', views.delete_judges_for_event, name='delete_judges'),

    path("events/<int:event_id>/awards/generate/", views.generate_diploma, name="generate_diploma"),
    path("events/<int:event_id>/awards/", event_awards_view, name="event_awards"),
    
    path("events/<int:event_id>/results/publish/", views.publish_event_results, name="publish_event_results"),
    path("events/<int:event_id>/results/<str:group_key>/", views.category_results, name="category_results"),

    path("events/<int:event_id>/judges/", views.manage_judges, name="manage_judges"),

    path("events/<int:event_id>/edit/", views.edit_event, name="edit_event"),
    path("events/<int:event_id>/publish_awards/", views.publish_awards, name="publish_awards"),
    path("participation/<int:participation_id>/scores/", views.participation_scores, name="participation_scores"),

    path('events/<int:event_id>/calculate_age_group/', views.calculate_age_group_view, name='calculate_age_group'),

    path("events/<int:event_id>/notify_clubs/", views.notify_clubs_of_event, name="notify_clubs"),
    
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

    path("events/<int:event_id>/judges/<int:judge_id>/delete/", views.delete_single_judge, name="delete_single_judge"),

    path("events/<int:event_id>/diplomas/", views.diploma_list, name="diploma_list"),

    path("events/<int:event_id>/add_ceremony/", views.add_ceremony, name="add_ceremony"),
    path("ceremony/<int:slot_id>/edit/", views.edit_ceremony, name="edit_ceremony"),
    path("ceremony/<int:slot_id>/delete/", views.delete_ceremony, name="delete_ceremony"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)