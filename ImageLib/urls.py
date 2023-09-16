from django.urls import path, re_path

from . import views


urlpatterns = [
    path("", views.MangaListView.as_view(), name="manga_list"),
    path("<int:pk>/", views.MangaDetailView.as_view(), name="manga_detail"),
    path("<int:pk>/update/", views.MangaUpdateView.as_view(), name="manga_update"),
    path("create/", views.MangaCreateView.as_view(), name="manga_create"),
    path("<int:pk>/delete/", views.MangaDeleteView.as_view(), name="manga_delete"),
    path(
        "<int:m_pk>/volume/<int:volume>/chapter/<int:chapter>/page/<int:page>/",
        views.ChapterDetailView.as_view(),
        name="chapter_detail"
    ),

    re_path(r"^chapter/create/$", views.ChapterCreateView.as_view(), {'manga': None}, name="chapter_create"),
    path("chapter/create/<int:manga>/", views.ChapterCreateView.as_view(), name="chapter_create_manga_bounded"),
    path('chapter/update/<int:pk>/', views.ChapterUpdateView.as_view(), name='chapter_update'),
    path('chapter/delete/<int:pk>/', views.delete_page, name='chapter_delete'),

    path("volume/create/", views.VolumeCreateView.as_view(), name="volume_create"),
    path("painter/create/", views.PainterCreateView.as_view(), name="painter_create"),
    path("author/create/", views.AuthorCreateView.as_view(), name="author_create"),
]
