from django.urls import path
from .views import MangaListView, MangaDetailView, MangaUpdateView, MangaCreateView, \
    MangaDeleteView, ChapterDetailView, ChapterCreateView, VolumeCreateView, ChapterUpdateView, delete_page, \
    PainterCreateView, AuthorCreateView

urlpatterns = [
    path("", MangaListView.as_view(), name="manga_list"),
    path("<int:pk>/", MangaDetailView.as_view(), name="manga_detail"),
    path("<int:pk>/update/", MangaUpdateView.as_view(), name="manga_update"),
    path("create/", MangaCreateView.as_view(), name="manga_create"),
    path("<int:pk>/delete/", MangaDeleteView.as_view(), name="manga_delete"),
    path("<int:m_pk>/volume/<int:volume>/chapter/<int:chapter>/page/<int:page>/", ChapterDetailView.as_view(),
         name="chapter_detail"),
    path("chapter/create/", ChapterCreateView.as_view(), name="chapter_create"),
    path('chapter/update/<int:pk>/', ChapterUpdateView.as_view(), name='chapter_update'),
    path('chapter/delete/<int:pk>/', delete_page, name='chapter_delete'),
    path("volume/create/", VolumeCreateView.as_view(), name="volume_create"),
    path("painter/create/", PainterCreateView.as_view(), name="painter_create"),
    path("author/create/", AuthorCreateView.as_view(), name="author_create"),
]
