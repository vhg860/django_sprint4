from django.urls import path
from blog import views

app_name: str = 'blog'

urlpatterns = [
    path('',
         views.PostListView.as_view(),
         name='post_list'),

    path('posts/<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'),

    path('profile/<str:username>/',
         views.ProfileView.as_view(),
         name='profile'),

    path('profile/edit_profile/<str:username>/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),

    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create_post'),

    path('posts/<int:pk>/edit/',
         views.PostUpdateView.as_view(),
         name='edit_post'),

    path('posts/<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'),

    path('posts/<int:pk>/comment/',
         views.CommentCreateView.as_view(),
         name='add_comment'),

    path('posts/<int:post_pk>/edit_comment/<int:comment_pk>.',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),

    path('posts/<int:post_pk>/delete_comment/<int:comment_pk>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),

    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(),
         name='category_posts'),
]
