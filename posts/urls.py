from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

urlpatterns = [
    #path("404/", views.page_not_found, name="page_not_found"),
    #path("500/", views.server_error, name="server_error"),    
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    path("new/", views.new_post, name="new_post"),
    path("<username>/", views.profile_view, name="profile_view"),
    path("<username>/<int:post_id>/", views.post_view, name="post_view"),
    path("<username>/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("", views.index, name="index"),
]
