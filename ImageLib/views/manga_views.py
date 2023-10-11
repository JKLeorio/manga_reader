from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import CreateView, UpdateView, DetailView, DeleteView

from django_filters.views import FilterView

from ..filters import MangaFilter
from ..forms import MangaForm
from ..models import Manga


class MangaCreateView(CreateView, LoginRequiredMixin):
    template_name = 'manga/manga_create.html'
    form_class = MangaForm
    success_url = reverse_lazy('manga_list')


class MangaListView(FilterView):
    filterset_class = MangaFilter
    template_name = 'manga/manga_list.html'
    model = Manga
    context_object_name = 'mangas'

    def get_queryset(self):
        params = self.request.GET
        queryset = Manga.objects.all()
        order_by = params.get('order_by')
        filter_order = ["-release_year", "release_year"]
        if order_by in filter_order:
            queryset = queryset.order_by(order_by)

        return queryset


class MangaDetailView(DetailView):
    model = Manga
    template_name = "manga/manga_detail.html"
    context_object_name = "manga"


class MangaUpdateView(LoginRequiredMixin, UpdateView):
    model = Manga
    form_class = MangaForm
    template_name = "manga/manga_update.html"

    def get_success_url(self):
        return reverse("manga_detail", args=[self.kwargs['pk']])


class MangaDeleteView(LoginRequiredMixin, DeleteView):
    model = Manga
    success_url = reverse_lazy("manga_list")
