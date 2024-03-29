from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts', views.posts, name='posts'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('new/', views.new_post, name='new_post'),
    
    path('follow/', views.follow_index, name='follow_index'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path(
        '<str:username>/<int:post_id>/edit/',
        views.post_edit,
        name='post_edit'
    ),
    path('<str:username>/<int:post_id>/comment/',
         views.add_comment,
         name='add_comment'),
    path('<str:username>/update/',
         views.update_user,
         name='update_user'),
    path('<str:username>/follow/', views.profile_follow, name='profile_follow'),
    path('<str:username>/unfollow/', views.profile_unfollow, name='profile_unfollow'),
    path('<int:post_id>/like/', views.post_like, name='post_like'),
    path('<int:post_id>/unlike/', views.post_unlike, name='post_unlike'),
]
